## For use on Raspberry Pi


from picamera2 import Picamera2
import time

camera = Picamera2()
camera.start()
time.sleep(1)

image_array = camera.capture_array("main")
print(f"Captured array: {image_array}")