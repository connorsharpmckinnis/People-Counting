import cv2
from ultralytics import YOLO
import numpy as np
from ultralytics.utils.plotting import Annotator, colors



class DetectionResult:
    def __init__(self, boxes, scores, class_ids, meta=None):
        self.boxes = boxes
        self.scores = scores
        self.class_ids = class_ids
        self.meta = meta or {}
        self.class_names = self.meta.get("class_names", [])

class DetectionEngine:
    def __init__(self, model_path, confidence_threshold=0.3, device="cpu", use_slicing=False):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.class_names = self.model.names

    
    def detect(self, image, classes_to_detect=None):
        results = self.model.predict(
            image,
            conf=self.confidence_threshold,
            device=self.device
        )[0]

        boxes, scores, class_ids = [], [], []

        for box, score, cls in zip(results.boxes.xyxy, results.boxes.conf, results.boxes.cls):
            class_id = int(cls)
            if classes_to_detect and class_id not in classes_to_detect:
                continue

            boxes.append(box.tolist())     # xyxy format
            scores.append(float(score))
            class_ids.append(class_id)

        boxes = np.array(boxes, dtype=float)
        scores = np.array(scores, dtype=float)
        class_ids = np.array(class_ids, dtype=int)
        
        class_names = [self.class_names[cid] for cid in class_ids]
        

        meta = {
            "num_detections": len(boxes),
            "model_name": self.model.model,
            "device": self.device,
        }

        return DetectionResult(boxes, scores, class_ids, meta | {"class_names": class_names})
    
class AnnotationEngine:
    def __init__(self):
        pass  # No config needed yet, could add font/line width overrides later

    def annotate(self, image, detection_result):
        annotated_img = image.copy()
        annotator = Annotator(annotated_img, line_width=2)

        boxes = detection_result.boxes
        scores = detection_result.scores
        class_ids = detection_result.class_ids
        names = detection_result.meta.get("class_names", [])

        for i in range(len(boxes)):
            bbox = boxes[i]
            cls_id = class_ids[i]
            conf = scores[i]
            name = names[i]
            label = f"{name} {conf:.2f}"

            annotator.box_label(bbox, label, color=colors(cls_id))

        return annotator.result()
    

class Orchestrator:
    def __init__(self, engine, annotator): 
        self.engine = engine
        self.annotator = annotator
        pass
    
    def analyze_image(self, image, classes_to_detect=None):
        image = cv2.imread(image)
        
        result = self.engine.detect(image, classes_to_detect)
        annotated = self.annotator.annotate(image, result)
        
        cv2.imshow("Annotated", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return annotated
    
    def analyze_video(self, video_path, classes_to_detect=None):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            result = self.engine.detect(frame, classes_to_detect)
            annotated = self.annotator.annotate(frame, result)
            cv2.imshow("Annotated", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        pass

    
    
    
    
def main():
    engine = DetectionEngine("yolo11n.pt")        
    annotator = AnnotationEngine()

    orchestrator = Orchestrator(engine, annotator)

    orchestrator.analyze_video("4791734-hd_1920_1080_30fps.mp4")



if __name__ == "__main__": 
    model = YOLO("yolo11n.pt")
    image_path = "people.jpg"
    main()