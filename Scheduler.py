from datetime import datetime, timedelta
from queue import Queue
import sys
import threading
from time import sleep
import pysher
import schedule
from DetectionThreadCamMTCNN import detectionThreadCamMTCNN
from DetectionThreadGSMTCNN import detectionThreadGSMTCNN
from RecognitionThreadGS import recognitionThreadGS
from RecognitionThreadCam import recognitionThreadCam
import json
import Api2
from log import log
from DataHelperFunctions import givenSubjectClean
pusher = pysher.Pusher(u"anykey", cluster='mt1', secure=False, secret=u'anysecret', port=6001,
                       custom_host='localhost', http_proxy_auth='localhost:8000/sanctum/csrf-cookie')

givenSubjectsUpdate = {}
reqQGlobal = None
conditionGlobal = None


def handleGSExtendEvent(*args, **kwargs):
    print("####################### Extend Handle #######################")
    log('Scheduler Thread: recieved gs extension command')
    data = json.loads(args[0])
    givenSubjectsUpdate[data['gsId']
                        ]["attendance_extend"] = data['extendDuration']


def handleGSRestartEvent(*args, **kwargs):
    log('Scheduler Thread: recieved gs restart command')
    print("####################### Restart Handle #######################")
    print(json.loads(args[0]))
    data = json.loads(args[0])
    if data['gsId'] in givenSubjectsUpdate.keys():
        givenSubjectsUpdate[data['gsId']
                            ]['restart_start_time'] = data['restart_start_time']
        givenSubjectsUpdate[data['gsId']
                            ]['restart_duration'] = data['restart_duration']
    else:
        print(givenSubjectsUpdate)
        givenSubjectsUpdate[data['gsId']
                            ] = givenSubjectClean(Api2.fetchASubjectById(data['gsId']))
    startTime = data['restart_start_time']
    if datetime.now().strftime('%H:%M:%S') > data['restart_start_time']:
        startTime = (datetime.now() + timedelta(seconds=5)
                     ).strftime('%H:%M:%S')
    schedule.every().day.at(startTime).do(
        givenSubjectBlock,
        givenSubject=givenSubjectsUpdate[data['gsId']],
        reqQ=reqQGlobal,
        condition=conditionGlobal,
        restarted=True
    )
    print("Scheduler: scheduled a GSBlock job at",
          startTime)


def handleTerminateEvent(*args, **kwargs):
    log('Scheduler Thread: recieved a termination command')
    print("####################### Termination Handle #######################")
    sys.exit()


# We can't subscribe until we've connected, so we use a callback handler
# to subscribe when able
def connect_handler(data):
    channel = pusher.subscribe('pythonChannel')
    print('connected to channel [pythonChannel]')
    channel.bind('App\Events\GsExtendEvent', handleGSExtendEvent)
    channel.bind('App\Events\GsRestartEvent', handleGSRestartEvent)
    channel.bind('App\Events\TerminateEvent', handleTerminateEvent)
    print('bounded the Event to the function')


def givenSubjectBlock(givenSubject, reqQ, condition, restarted=False):
    print('Given Subject block started')
    # a condition for the recognition and the detection thread to communicate on
    inbredCondition = threading.Condition()
    # for the recognition thread to know that the job is done and should self-terminate
    jobIsDone = {'jobIsDone': False}
    # the queue the threads will transfer data on
    detectQ = Queue()

    # initializing the detection thread
    detThread = threading.Thread(target=detectionThreadGSMTCNN, args=(
        givenSubject, givenSubject['cam_url'], detectQ, inbredCondition, jobIsDone, restarted))

    # initializing the recognition thread
    recThread = threading.Thread(target=recognitionThreadGS, args=(
        givenSubject, reqQ, detectQ, condition, inbredCondition, jobIsDone))

    # run the threads
    detThread.start()
    recThread.start()

    # wait for the threads to finish their job
    detThread.join()
    recThread.join()
    return schedule.CancelJob


def camBlock(cam, people, reqQ, schedule, condition):
    # a condition for the recognition and the detection thread to communicate on
    inbredCondition = threading.Condition()
    # for the recognition thread to know that the job is done and should self-terminate
    jobIsDone = {'jobIsDone': False}
    # the queue the threads will transfer data on
    detectQ = Queue()

    # initializing the detection thread
    detThread = threading.Thread(target=detectionThreadCamMTCNN, args=(
        cam, schedule, detectQ, inbredCondition, jobIsDone))

    # initializing the recognition thread
    recThread = threading.Thread(target=recognitionThreadCam, args=(
        people, cam['id'], reqQ, detectQ, condition, inbredCondition, jobIsDone))

    # run the threads
    detThread.start()
    recThread.start()

    # wait for the threads to finish their job
    detThread.join()
    recThread.join()
    return schedule.CancelJob


def launchScheduler(givenSubjects, cams, people, reqQ, condition):
    global givenSubjectsUpdate, reqQGlobal, conditionGlobal
    givenSubjectsUpdate = givenSubjects
    reqQGlobal = reqQ
    conditionGlobal = condition
    # subscribe to the channel and add an event listener
    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()
    # log('Scheduler Thread: reading information and creating detection & recognition units')

    # loop givenSubjects and schedule each one at the right time
    for givenId, givenSubject in givenSubjectsUpdate.items():
        startTime = (datetime.strptime(
            givenSubject['time'], '%H:%M:%S') - timedelta(minutes=givenSubject['attendance_pre'])).strftime('%H:%M:%S')
        # if the startTime is before the current time start now
        if datetime.now().strftime('%H:%M:%S') > startTime:
            startTime = (datetime.now() + timedelta(seconds=5)
                         ).strftime('%H:%M:%S')
        schedule.every().day.at(startTime).do(givenSubjectBlock, givenSubject=givenSubject,
                                              reqQ=reqQGlobal, condition=conditionGlobal)
        print("Scheduler: scheduled a GSBlock job at",
              startTime)

    # loop cameras
    for cam_id, cam in cams.items():
        # loop schedules of each camera
        for sch in cam['schedule']:
            startTime = sch['start']
            if datetime.now().strftime('%H:%M:%S') > sch['start']:
                if datetime.now().strftime('%H:%M:%S') > sch['end']:
                    continue
                startTime = (datetime.now() + timedelta(seconds=5)
                             ).strftime('%H:%M:%S')
            # schedule a job for each schedule in the camera
            schedule.every().day.at(startTime).do(camBlock, cam, people=people, schedule=sch,
                                                  reqQ=reqQGlobal, condition=conditionGlobal)
            print("Scheduler: scheduled a CamBlock job at",
                  startTime, 'actual Start:', sch['start'], ', actual End', sch['end'])
    while True:
        schedule.run_pending()
        sleep(1)
