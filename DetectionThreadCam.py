from PIL import Image
import cv2
from datetime import datetime, timedelta
from queue import Queue
import threading

from cv2 import imshow
import numpy as np
framerate = 30  # the framerate of the cameras
detectionQ = Queue()
lock = threading.Lock()


def calculateEndTime(schedule):
    return schedule['end']


def detectionThreadCam(cam, schedule, detectQ, notifyCondition, jobIsDone):
    print("detection thread started working at:",
          datetime.now().strftime('%H:%M:%S'))

    cap = cv2.VideoCapture(int(cam['cam_url']))
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    frameCount = 0
    frame = []
    faces = []
    frameCountTemp = 0
    while datetime.now().strftime('%H:%M:%S') < calculateEndTime(schedule):
        detections = []
        ret, tempFrame = cap.read()
        frameCount += 1
        facesTemp = face_cascade.detectMultiScale(
            cv2.cvtColor(tempFrame, cv2.COLOR_BGR2GRAY), 1.3, 5)
        if (len(facesTemp) > len(faces)):
            print(len(facesTemp) > len(faces), len(facesTemp), ' ', len(faces))
            faces = facesTemp
            frame = tempFrame
            frameCountTemp = frameCount
        # print("Detection Thread: detected", len(faces), "faces")
        if frameCount == framerate:
            for (x, y, w, h) in faces:
                detections.append(frame[y - 20:y + h + 10, x - 10:x + w + 10])
                frame = cv2.rectangle(
                    frame, (x - 10, y - 20), (x + w + 10, y + h + 10), (255, 0, 0), 2)
            if len(detections) != 0:
                detectQ.put({"detections": detections, 'frame': frame})
                cv2.imwrite('rec.png', frame)
                print("frameCount:", frameCountTemp)
                with notifyCondition:
                    notifyCondition.notify_all()
            # start a new second
            frame = []
            faces = []
            frameCountTemp = 0
            frameCount = 0
            print(calculateEndTime(schedule))
    jobIsDone = True
    cap.release()
    cv2.destroyAllWindows()


# import cv2
# from datetime import datetime, timedelta
# from queue import Queue
# import threading
# framerate = 30  # the framerate of the cameras
# detectionQ = Queue()
# lock = threading.Lock()


# def calculateEndTime(schedule):
#     return schedule['end']


# def detectionThreadCam(cam, schedule, detectQ, notifyCondition, jobIsDone):
#     print("detection thread started working at:",
#           datetime.now().strftime('%H:%M:%S'))

#     cap = cv2.VideoCapture(int(cam['cam_url']))
#     face_cascade = cv2.CascadeClassifier(
#         cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     if not cap.isOpened():
#         raise IOError("Cannot open webcam")
#     frameCount = 0
#     while datetime.now().strftime('%H:%M:%S') < calculateEndTime(schedule):
#         detections = []
#         ret, frame = cap.read()
#         frameCount += 1
#         # detect faces only on the first, the middle and the last frame of the second
#         if 1 == 1 or frameCount == 1 or frameCount == framerate / 2 or frameCount == framerate:
#             faces = face_cascade.detectMultiScale(
#                 cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.3, 5)
#             for (x, y, w, h) in faces:
#                 detections.append(frame[y:y + h, x:x + w])
#                 frame = cv2.rectangle(
#                     frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#             # print("Detection Thread: detected", len(faces), "faces")
#             if frameCount == framerate:
#                 # start a new second
#                 frameCount = 0
#                 print(calculateEndTime(schedule))
#             if len(faces) != 0:
#                 detectQ.put({"detections": detections, 'frame': frame})
#                 with notifyCondition:
#                     notifyCondition.notify_all()
#     jobIsDone = True
#     cap.release()
#     cv2.destroyAllWindows()
