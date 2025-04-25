from ultralytics import YOLO
import torch

class PeopleDetector:
    def __init__(self, model_path="C:\\Users\\fa15s\\OneDrive\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\models\\best.pt", conf_threshold=0.35):
        # Set device configuration for GPU acceleration if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        # Load model with device specification
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        # Set confidence threshold for detection
        self.conf_threshold = conf_threshold
    
    def detect(self, frame):
        # Run inference with optimized settings
        results = self.model(
            frame, 
            verbose=False,
            conf=self.conf_threshold,  # Only process confident detections
            classes=0,                 # Only detect person class (class 0)
            max_det=20                 # Limit maximum detections
        )[0]
        
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            if cls_id == 0:  # class 0 usually corresponds to 'person' in COCO
                detections.append((x1.item(), y1.item(), x2.item(), y2.item(), conf))
        
        return detections