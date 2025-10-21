from ultralytics import YOLO
import cv2
import time
import datetime
import sqlite3

model = YOLO("yolov11n.pt")

def search_for_cameras():
    cameras = []
    dev_port = 0
    
    while True: 
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            break
        else: 
            is_reading, img = camera.read()
            if is_reading:
                cameras.append(dev_port)
            camera.release()
            dev_port += 1
    return cameras


def take_picture(camera):
    cam = camera
    ret, img = cam.read()  # capture a single frame
    if not ret:
        print("Camera capture failed")
        return None
    return img  # returns a NumPy array in memory


def count_people(camera, confidence_threshold=0.6):
    img = take_picture(camera)
    if img is None:
        return 0

    results = model.predict(img, conf=confidence_threshold, verbose=False)

    people = sum(int(cls) == 0 for cls in results[0].boxes.cls)


    return people

def add_count_to_db(location: str, count: int):
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = count
    location = location

    # Insert a step to send the results to whatever server or save results to a local server for testing purposes. 
    conn = sqlite3.connect("people_counts.db")
    cursor = conn.cursor()
    
    cursor.execute("""
                    INSERT INTO counts (location, timestamp, count)
                    VALUES (?, ?, ?)
                    """, (location, timestamp, count))
    
    conn.commit()
    conn.close()
    print('Saved entry')
        

def main(confidence_value, sleep_time, location_name, camera_index):
    confidence = confidence_value
    sleep_time = sleep_time
    location = location_name
    camera_index = camera_index
    cam = cv2.VideoCapture(camera_index)

    try:
        while True: 
            
            people = count_people(camera=cam, confidence_threshold=confidence)
            print(f"{people} people in the image")
            add_count_to_db(location, people)
            
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print('Exiting...')
    
    finally: 
        cam.release()
    
    cam.release()
    
        
if __name__ == "__main__":
    main(0.6, 5, "Innovation Office", 1)