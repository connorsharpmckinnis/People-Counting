from ultralytics import YOLO
import cv2
import time
import datetime
import sqlite3
import requests
#from picamera2 import Picamera2

model = YOLO("yolov11n.pt")
SERVER_IP = "10.9.81.124"
SERVER_URL = f"http://{SERVER_IP}:8000"
LOCAL_DB = "offline_cache.db"

def take_picture(camera, mode):
    if mode == "PI":
        #img = cam.capture_array("main")
        #return img
        pass
    
    cam = camera
    for _ in range(3):
        ret, img = cam.read()
    
    ret, img = cam.read()  # capture a single frame
    if not ret:
        print("Camera capture failed")
        return None
    return img  # returns a NumPy array in memory


def count_people(camera, confidence_threshold=0.6, mode=None):
    img = take_picture(camera, mode)
    if img is None:
        return 0

    results = model.predict(img, conf=confidence_threshold, verbose=False)

    people = sum(int(cls) == 0 for cls in results[0].boxes.cls)

    return people


def save_locally(location, timestamp, count):
    """Save record locally if network fails."""
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute("INSERT INTO local_cache (location, timestamp, count) VALUES (?, ?, ?)",
              (location, timestamp, count))
    conn.commit()
    conn.close()
    print("Saved locally (offline):", location, timestamp, count)


def upload_local_cache():
    """Try uploading cached data once online."""
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute("SELECT id, location, timestamp, count FROM local_cache")
    rows = c.fetchall()
    if not rows:
        conn.close()
        return

    print(f"Uploading {len(rows)} cached records...")
    for row in rows:
        record_id, location, timestamp, count = row
        payload = {"location": location, "timestamp": timestamp, "count": count}
        try:
            response = requests.post(f"{SERVER_URL}/add_count", json=payload, timeout=3)
            if response.status_code == 200:
                c.execute("DELETE FROM local_cache WHERE id = ?", (record_id,))
        except Exception:
            # Don’t delete anything if upload fails midway
            print("Upload failed — will retry later.")
            break

    conn.commit()
    conn.close()

def server_is_reachable():
    try:
        r = requests.get(f"{SERVER_URL}/ping", timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def add_count_to_db(location: str, count: int):
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = count
    location = location

    payload = {
        "location": location,
        "timestamp": timestamp,
        "count": count
    }
            
    if server_is_reachable():
        try:
            upload_local_cache()  # push any stored data now that we're online

            response = requests.post(f"{SERVER_URL}/add_count", json=payload, timeout=3)
            print(response.json())
        except Exception as e:
            print("Upload failed, saving locally:", e)
            save_locally(location, timestamp, count)
    else:
        print("Server offline. Saving locally")
        save_locally(location, timestamp, count)

def main(confidence_value, sleep_time, location_name, camera_index, mode="USB"):
    confidence = confidence_value
    sleep_time = sleep_time
    location = location_name
    camera_index = camera_index
    mode = mode
    if mode == "USB":   
        cam = cv2.VideoCapture(camera_index)
    elif mode == "PI":
        #cam = Picamera2()
        pass

    try:
        while True: 
            
            people = count_people(camera=cam, confidence_threshold=confidence, mode = mode)
            print(f"{people} people in the image")
            add_count_to_db(location, people)
            
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print('Exiting...')
    
    finally: 
        if mode == "USB":
            cam.release()
        elif mode == "PI":
            #cam.close()
            pass    
        
if __name__ == "__main__":
    main(0.6, 5, "Innovation Office", 1)