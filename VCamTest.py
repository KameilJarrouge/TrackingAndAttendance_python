import cv2

cap = cv2.VideoCapture(2)

if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    ret, frame = cap.read()
    cv2.imwrite('VCAM.png', frame)
