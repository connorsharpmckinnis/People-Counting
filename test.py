## For use on Raspberry Pi


from engine import DetectionEngine, AnnotationEngine, Orchestrator
import cv2
import time
import numpy as np

model_path = "yolo11n.pt"
mode = "PC"

if mode == "PI":
    from picamera2 import Picamera2
    camera = Picamera2()
    camera.set_controls({"AfMode": 2})

    camera.start()
    time.sleep(1)
elif mode == "PC":
    camera = cv2.VideoCapture(0)
    
orch = Orchestrator(DetectionEngine(model_path, 0.3, "cpu", False), AnnotationEngine())

def take_picture():
    if mode == "PI":
        image = camera.capture_array("main")
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        return image
    elif mode == "PC":
        ok, image = camera.read()
        if ok: 
            return image

while True: 
    image = take_picture()
    annotated_image = orch.analyze_image(image)
    cv2.imshow("test", annotated_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break   
    time.sleep(5) 

cv2.destroyAllWindows()