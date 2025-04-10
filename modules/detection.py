
from ultralytics import YOLO

class PeopleDetector:
    def __init__(self, model_path="C:\\Users\\fa15s\\OneDrive\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\models\\yolo11n.pt"):  # Default to yolov8n
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            if cls_id == 0:  # class 0 usually corresponds to 'person' in COCO
                detections.append((x1.item(), y1.item(), x2.item(), y2.item(), conf))
        return detections
