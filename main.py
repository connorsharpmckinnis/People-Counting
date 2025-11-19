from ultralytics import YOLO
import cv2
import time
import datetime
import sqlite3
import requests
from picamera2 import Picamera2
import paho.mqtt.client as mqtt


model = YOLO("yolo11n.pt")
SERVER_IP = "10.9.81.124"
SERVER_URL = f"http://{SERVER_IP}:8000"
LOCAL_DB = "offline_cache.db"

def take_picture(camera, mode):
    cam = camera

    if mode == "PI":
        img = cam.capture_array("main")
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        return img
    
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
    
def test_camera_view(camera_index=0, mode="USB"):
    """
    Shows a live preview of what the camera sees. Press 'q' to exit.
    """
    if mode == "USB":
        cam = cv2.VideoCapture(camera_index)
    elif mode == "PI":
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_preview_configuration())
        cam.set_controls({"AfMode": 2})  # continuous autofocus
        cam.start()

    print("Starting camera test. Press 'q' to quit.")
    
    try:
        while True:
            if mode == "USB":
                ret, frame = cam.read()
            elif mode == "PI":
                frame = cam.capture_array("main")
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                ret = True

            if not ret:
                print("Failed to grab frame")
                break

            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        if mode == "USB":
            cam.release()
        elif mode == "PI":
            cam.close()
        cv2.destroyAllWindows()
        print("Camera test ended.")



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
        
def publish_count(count: int, topic: str, client: mqtt.Client):
    client.publish(topic, count)


def main(confidence_value, sleep_time, location_name, camera_index, mode="USB", online=True):
    confidence = confidence_value
    sleep_time = sleep_time
    location = location_name
    camera_index = camera_index
    mode = mode
    
    BROKER = "h114ad14.ala.us-east-1.emqxsl.com"
    PORT = 8883
    USERNAME = "username"
    PASSWORD = "password"
    TOPIC = f"sensors/{location}"

    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()  # Keep TLS; required by your broker
    client.connect(BROKER, PORT)    
    
    
    if mode == "USB":   
        cam = cv2.VideoCapture(camera_index)
    elif mode == "PI":
        cam = Picamera2()
        cam.set_controls({"AfMode": 2})
        cam.start()
        pass

    try:
        while True: 
            
            people = count_people(camera=cam, confidence_threshold=confidence, mode = mode)
            print(f"{people} people in the image")
            #add_count_to_db(location, people)
            if online: 
                publish_count(people, TOPIC, client)
            else:
                now_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_locally(location, now_timestamp, people)
            
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print('Exiting...')
    
    finally: 
        if mode == "USB":
            cam.release()
        elif mode == "PI":
            cam.close()
            pass    
        
if __name__ == "__main__":
    #test_camera_view(mode="PI")
    main(
        confidence_value=0.6, 
        sleep_time=5, 
        location_name="Node X", 
        camera_index=1, 
        mode="PI",
        online=True
    )