from datetime import datetime
from urllib.parse import urlencode
import skimage
import json
from PIL import Image
import Api2
import numpy as np
from RecognitionFunction import recognize
from log import log

resultFile = open('/home/kamil/MTCNNImages/result.txt', 'w')

#  "Content-Type": "multipart/form-data"


def recognitionThreadGS(givenSubject, reqQ, detectQ, notifyCondition, waitCondition, jobIsDone):
    print("recognition thread started working at:",
          datetime.now().strftime('%H:%M:%S'))
# encoded_data = json.dumps(data).encode('utf-8')
    # inform the backend that this week attendance for this givenSubject is visited
    log('GS recognition thread informing backend to mark the current week as visited')
    reqQ.put({
        'hasFile': False,
        'url': '/api/given-subjects/' + str(givenSubject['id']) + '/visit-this-week',
        'data': {'attIds': Api2.getSendableList([student['attId'] for student in givenSubject['students']])},
    })
    with notifyCondition:
        notifyCondition.notify_all()

    count = 0

    professorRecognized = False
    # jobIsDone is a way for the detection thread to let this thread that the job is done
    # the readFromDetectionQueue is here in case there's any more detection that this thread should check before termination
    while (not jobIsDone['jobIsDone'] or not detectQ.empty()):
        # loop as long as there's detections in the queue
        while not detectQ.empty():
            # a set of people id's captured in this specific frame
            recognitions = set()
            profAttId = -1
            # get the detections and the frame from the queue
            data = detectQ.get()
            for detection in data["detections"]:
                if professorRecognized:
                    log('GS recognition thread checking for students')
                    print("checking for students")
                    for student in givenSubject['students']:
                        image = skimage.io.imread(
                            student['images'][0])
                        if image.shape[-1] == 4:
                            image = np.delete(image, 3, 2)

                        if (recognize(detection, image)):
                            log('GS recognition thread captured a student')
                            # add the person's id to the set
                            recognitions.add(student['attId'])
                            break
                else:
                    log('GS recognition thread checking if the captured person is the professor')
                    print("checking for professor")
                    image = skimage.io.imread(
                        givenSubject["profImageUrl"])
                    if image.shape[-1] == 4:
                        image = np.delete(image, 3, 2)

                    if (recognize(detection, image)):
                        log('GS recognition thread captured the professor')
                        print('professor found')
                        # add the person's id to the set
                        profAttId = givenSubject['profAttId']
                        # recognize the professor
                        professorRecognized = True

            # testing code
            resultFile.write(json.dumps(list(recognitions)))
            resultFile.write(
                "===============================================\n")
            resultFile.flush()
            print("recognized ids :", recognitions)
            im = Image.fromarray(data['frame'])
            im.save("rec" + str(count) + ".jpeg")
            # ===================
            reqQ.put(
                {
                    'hasFile': True,
                    'url': '/api/given-subjects/' + str(givenSubject['id']) + '/attendance-python',
                    'data': {
                        'recognitions': Api2.getSendableList(list(recognitions)),
                        'profAttId': profAttId,
                        'isAttended': data['isAttended']
                    },
                    'frame':  {"frame": Api2.getSendableImage(data['frame'])},

                })
            profAttId = -1
            with notifyCondition:
                notifyCondition.notify_all()
        with waitCondition:
            print("Recogntion Thread: went to sleep")
            waitCondition.wait()
            print("Recogntion Thread: woke up")

    # reset the given subject's attendance_extend to 0 in the database
    if (givenSubject['attendance_extend'] != "0" or givenSubject['restart_duration'] != "0"):
        print("resetting this givenSubject extension and resart fields")
        reqQ.put({
            'hasFile': False,
            'url': '/api/given-subjects/' + str(givenSubject['id']) + '/reset',
            'data': {}
        })
        with notifyCondition:
            notifyCondition.notify_all()
    # handle if the professorRecognized is false. Make this session skipped for students
    if not professorRecognized:
        log('GS recognition thread: professor didn\'t show up')
        print("skipping students attendance this week because the professor didn't attend")
        reqQ.put({
            'hasFile': False,
            'url': '/api/given-subjects/' + str(givenSubject['id']) + '/skip-this-students-week',
            'data': {}
        })
        with notifyCondition:
            notifyCondition.notify_all()
    else:  # calculate the absent count for all the students in this gs
        log('GS recognition thread: finished attendance taking... informing backend to calculate absence')
        print("calculating the abscence for the students of this givenSubject")
        reqQ.put({
            'hasFile': False,
            'url': '/api/taken-subjects/calculate-absence',
            'data': {'takenSubjectIds': Api2.getSendableList([student['takenSubjectId'] for student in givenSubject['students']])}
        })
        with notifyCondition:
            notifyCondition.notify_all()
    print('recognition thread terminated gracefully')
