from datetime import datetime
import numpy as np
from RecognitionFunction import recognize
import skimage
from PIL import Image
import json
import Api2
from log import log
resultFile = open('/home/kamil/MTCNNImages/result.txt', 'w')


def recognitionThreadCam(people, camId, reqQ, detectQ, notifyCondition, waitCondition, jobIsDone):
    print("recognition thread started working at:",
          datetime.now().strftime('%H:%M:%S'))
    count = 0

    # jobIsDone is a way for the detection thread to let this thread that the job is done
    # the readFromDetectionQueue is here in case there's any more detection that this thread should check before termination
    while (not jobIsDone['jobIsDone'] or not detectQ.empty()):
        # loop as long as there's detections in the queue
        while not detectQ.empty():
            # a set of people id's captured in this specific frame
            recognitions = set()
            # get the detections and the frame from the queue
            data = detectQ.get()
            # number of unrecognized people
            unknown = 0
            for detection in data["detections"]:
                recognized = False
                for id, person in people.items():
                    image = skimage.io.imread(
                        person['images'][0]['url'])
                    if image.shape[-1] == 4:
                        image = np.delete(image, 3, 2)

                    if (recognize(detection, image)):
                        # add the person's id to the set
                        log('cam recognition thread captured person: ' +
                            person['name'], 'green')
                        recognitions.add(person['id'])
                        recognized = True
                        break
                # increase the count of the unrecognized
                if not recognized:
                    log('cam recognition thread captured an unknown person', 'yellow')
                    unknown += 1
            resultFile.write(json.dumps(list(recognitions)))
            resultFile.write("\nunknown::"+str(unknown)+"\n")
            resultFile.write(
                "===============================================\n")
            resultFile.flush()
            print("recognized ids :", recognitions)
            print("unknown count:", unknown)
            im = Image.fromarray(data['frame'])
            im.save("rec" + str(count) + ".jpeg")
            reqQ.put(
                {
                    'hasFile': True,
                    'url': '/api/cameras/' + str(camId) + "/log-python",
                    "data": {
                        'recognitions': Api2.getSendableList(list(recognitions)),
                        'unknown': unknown,
                    },
                    'frame': {"frame": Api2.getSendableImage(data['frame'])},
                })
            with notifyCondition:
                notifyCondition.notify_all()
        with waitCondition:
            print("Recogntion Thread: went to sleep")
            waitCondition.wait()
            print("Recogntion Thread: woke up")
