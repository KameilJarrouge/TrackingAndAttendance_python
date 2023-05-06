import cv2
from datetime import datetime, timedelta
from queue import Queue
import threading
framerate = 30  # the framerate of the cameras
detectionQ = Queue()
lock = threading.Lock()


def calculateEndTime(givenSubject):
    return "23:00:00"
    temp = datetime.strptime(givenSubject['time'], '%H:%M:%S')
    temp = temp + timedelta(
        minutes=(givenSubject['attendance_post'] + givenSubject['attendance_present']))
    return temp.strftime('%H:%M:%S')


def detectionThreadGS(givenSubject, cam_url, writeToDetectionQ, notifyCondition, jobIsDone):
    with notifyCondition:
        cap = cv2.VideoCapture(cam_url)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if not cap.isOpened():
            raise IOError("Cannot open webcam")
        frameCount = 0
        while datetime.now().strftime('%H:%M:%S') < calculateEndTime(givenSubject):
            detections = []
            ret, frame = cap.read()
            frameCount += 1
            # detect faces only on the first, the middle and the last frame of the second
            if 1 == 1 or frameCount == 1 or frameCount == framerate / 2 or frameCount == framerate:
                faces = face_cascade.detectMultiScale(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.3, 5)
                print(len(faces))
                for (x, y, w, h) in faces:
                    detections.append(frame[y:y + h, x:x + w])
                    frame = cv2.rectangle(
                        frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                if frameCount == framerate:
                    # start a new second
                    frameCount = 0
                writeToDetectionQ({"detections": detections, 'frame': frame})
                notifyCondition.notify_all()
    jobIsDone = True
    cap.release()
    cv2.destroyAllWindows()
