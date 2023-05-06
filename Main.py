import threading
from queue import Queue
import Api2
import DataHelperFunctions
from Scheduler import launchScheduler
from log import log
reqQ = Queue()
condition = threading.Condition()
wait_timeout = 1800  # 30 minutes

# log('Main Thread: Requesting information')
# given Subject data
givenSubjects = {data["id"]: DataHelperFunctions.givenSubjectClean(
    data) for data in Api2.getData('/api/python-data-gs')}

# all cams which are scheduled to work on this day
cams = {data["id"]: DataHelperFunctions.camClean(data)
        for data in Api2.getData('/api/python-data-cams')}

# all people with only id's and images
people = {data["id"]: DataHelperFunctions.personClean(data)
          for data in Api2.getData('/api/python-data-people')}
print("Main Thread: givenSubjects data::", givenSubjects)
print("Main Thread: cams data::", cams)
print("Main Thread: people data::", people)

# log('=================================================================\nStarted a new session\n=================================================================', 'yellow')
# log('Main Thread: recieved information')
# log('Main Thread: creating the Scheduler Thread')


# give the scheduler the data and the Qeueue write function
schedulerThread = threading.Thread(
    target=launchScheduler, args=(givenSubjects, cams, people, reqQ, condition))
schedulerThread.start()

while True:
    with condition:
        print('Main Thread: checking requests')
        # log('Main Thread: checking Queue')

        while not reqQ.empty():
            # log('Main Thread: Sending a request to API')
            req = reqQ.get()
            if req['hasFile']:
                Api2.sendRequest(req['url'],
                                 req['data'], req['frame'])
            else:
                Api2.sendRequestWithoutFiles(req['url'], req['data'])
            print('Main Thread: sent a request to:', req['url'])

            # print('Main Thread: data', req['data'])
        # log('Main Thread: Queue is empty waiting...')
        print('Main Thread: waiting to be notified')
        condition.wait(wait_timeout)
        # log('Main Thread: notified')
