import cv2
import numpy as np 

cap = cv2.VideoCapture("rtsp://192.168.248.54:9000/live")

while True:
    _, frame = cap.read()
    
    cv2.imshow("frame", frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()