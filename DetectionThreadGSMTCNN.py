import cv2
from datetime import datetime, timedelta
from queue import Queue
import threading
from mtcnn import MTCNN

framerate = 30  # the framerate of the cameras
detectionQ = Queue()
lock = threading.Lock()
detectorModel = MTCNN()


def calculateEndTime(givenSubject, restarted):
    if restarted:
        return (datetime.strptime(givenSubject['restart_start_time'], '%H:%M:%S') +
                timedelta(minutes=int(givenSubject['restart_duration']))).strftime('%H:%M:%S')

    temp = datetime.strptime(givenSubject['time'], '%H:%M:%S')
    temp = temp + timedelta(
        minutes=(int(givenSubject['attendance_post']) + int(givenSubject['attendance_present']) + int(givenSubject['attendance_extend'])))
    return temp.strftime('%H:%M:%S')


def calculateIsAttended(givenSubject, restarted, captureTime):
    if restarted:
        return True

    temp = datetime.strptime(givenSubject['time'], '%H:%M:%S')
    temp = temp + timedelta(
        minutes=(int(givenSubject['attendance_post']) + int(givenSubject['attendance_extend'])))
    return temp.strftime('%H:%M:%S') > captureTime


def calculateConfidence(faces):
    result = 0
    for face in faces:
        result += face['confidence']
    if (len(faces) == 0):
        return 0
    return result/len(faces)


def detectionThreadGSMTCNN(givenSubject, cam_url, detectQ, notifyCondition, jobIsDone, restarted=False):
    print("detection thread started working at:",
          datetime.now().strftime('%H:%M:%S'))
    # caputure webcam input
    cap = cv2.VideoCapture(int(cam_url))
    # handle webcam not opened
    if not cap.isOpened():
        print("can't reach the camera. Terminating this thread after informing the related recognition thread to terminate.")
        # jobIsDone['jobIsDone'] = True
        # with notifyCondition:
        #     notifyCondition.notify_all()
        # return

    frameCount = 0
    frame = []
    faces = []
    while datetime.now().strftime('%H:%M:%S') < calculateEndTime(givenSubject, restarted):
        detections = []
        ret, camFrame = cap.read()
        frameCount += 1
        # select some frames to apply the face detection model on
        if frameCount == 1 or frameCount == 8 or frameCount == framerate / 2 or frameCount == 22 or frameCount == framerate:
            # detecting faces on the tempFrame
            facesTemp = detectorModel.detect_faces(
                cv2.cvtColor(camFrame, cv2.COLOR_BGR2RGB))
            # selected frame has more faces than the last saved frame (in the current second)
            if (len(facesTemp) > len(faces)):
                faces = facesTemp
                frame = camFrame
            # selected frame has the same number of faces as the last saved frame
            elif (len(facesTemp) == len(faces)):
                # the average confidence over the faces of the selected frame is larger than the one of the last saved frame
                if (calculateConfidence(facesTemp) > calculateConfidence(faces)):
                    faces = facesTemp
                    frame = camFrame

        if frameCount == framerate:
            for face in faces:
                if face['confidence'] > 0.9999:
                    # extract the bounding box info
                    (x, y, w, h) = face['box']
                    # add the face to the valid detections
                    detections.append(
                        frame[y - 20:y + h + 10, x - 10:x + w + 10])
                    # draw the bounding box on the frame
                    frame = cv2.rectangle(
                        frame, (x - 10, y - 20), (x + w + 10, y + h + 10), (255, 0, 0), 2)
            # if none of the faces made it to the valid detections skip writing to the queue and start a new second
            if len(detections) != 0:
                detectQ.put({
                    "detections": detections,
                    'frame': cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'isAttended': calculateIsAttended(givenSubject=givenSubject, restarted=restarted, captureTime=datetime.now().strftime('%H:%M:%S'))
                })
                with notifyCondition:
                    notifyCondition.notify_all()
            # start a new second
            frame = []
            faces = []
            frameCount = 0
            print(calculateEndTime(givenSubject, restarted=restarted))
    jobIsDone['jobIsDone'] = True
    with notifyCondition:
        notifyCondition.notify_all()
    cap.release()
    print('Detection Thread terminated')
