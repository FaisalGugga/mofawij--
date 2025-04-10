from modules.camera import Camera
from modules.detection import PeopleDetector
from modules.tracking import PersonTracker
from modules.data_manager import DataManager
from modules.ui import UI
from modules.alerts import AlertSystem
from modules.export_to_data import export_logs_to_excel
import cv2
import os
from datetime import datetime
import time



# Initialize components Gate A = Test66, Gate B = Test55, Gate C = Test88, 
camera = Camera(source="C:\\Users\\fa15s\\OneDrive\\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\Test88.mp4")
detector = PeopleDetector()
tracker = PersonTracker()
database = DataManager()
ui = UI()
alerts = AlertSystem()

last_screenshot_time = datetime.now()
SCREENSHOT_INTERVAL = 4  
last_reset_time = time.time()
# Define gate
CONGESTION_LINE_Y = 500 # Gate A = 400, Gate B,C  = 500
gate_zone = "Gate_C"
screenshot_dir = os.path.join("screenshots", gate_zone)
os.makedirs(screenshot_dir, exist_ok=True)


people_below_line = 0 
recorded_detections = set()

def save_congestion_screenshot(frame, detection, timestamp):
    """Save screenshot of specific detection crossing the line"""
    x1, y1, x2, y2, _ = detection
    # Capture area around the detection (50px padding)
    padding = 50
    top = max(0, int(y1) - padding)
    bottom = min(frame.shape[0], int(y2) + padding)
    left = max(0, int(x1) - padding)
    right = min(frame.shape[1], int(x2) + padding)
    
    crop_img = frame[top:bottom, left:right]
    filename = f"crossing_{timestamp}.jpg"
    path = os.path.join(screenshot_dir, filename)
    cv2.imwrite(path, crop_img)

# Only remove comment for Gate B
playback_speed = 4.0 
while True:
    
    target_frame_pos = int(camera.cap.get(cv2.CAP_PROP_POS_FRAMES) + playback_speed)
    camera.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_pos)
    frame = camera.get_frame()
    if frame is None:
        break
    
    frame = cv2.resize(frame, (960, 960))
    if time.time() - last_reset_time >180:
        people_below_line = 0 
        recorded_detections = set()  
        last_reset_time = time.time()
        
        
    # Detect people
    detections = detector.detect(frame)
    current_frame_crossings = set()

    # Count people
    people_count = len(detections)

    for detection in detections:  # Changed to iterate properly
        x1, y1, x2, y2, conf = detection
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f"person {conf:.2f}", (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Create signature for THIS detection (moved inside loop)
        detection_signature = f"{x1:.1f}_{y1:.1f}_{x2:.1f}_{y2:.1f}"
        
    if y2 > CONGESTION_LINE_Y:
        current_frame_crossings.add(detection_signature)
        if detection_signature not in recorded_detections:
            people_below_line += 1
            recorded_detections.add(detection_signature)
            print(f"New crossing! Total: {people_below_line}")   
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            save_congestion_screenshot(frame.copy(), detection, timestamp)  # Direct call
    
    # Draw congestion line
    cv2.line(frame, (0, CONGESTION_LINE_Y), (frame.shape[1], CONGESTION_LINE_Y), (0, 0, 255), 2)
    cv2.putText(frame, "Congestion Line", (10, CONGESTION_LINE_Y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Congestion logic
    congestion_level = "LOW"
    if people_below_line > 250:
        congestion_level = "HIGH"
    elif people_below_line > 150:
        congestion_level = "MEDIUM"

    # Calculate density
    density = people_count / 100

    # Check alerts and gate status
    alert_triggered, gate_status = alerts.check_congestion(people_count)

    # Save to database
    database.log_data(people_count, congestion_level, gate_zone, density, alert_triggered, gate_status, people_below_line)

    # Track and optionally screenshot people
    formatted_detections = [
    ([x1, y1, x2, y2], conf, 0) for (x1, y1, x2, y2, conf) in detections
    ]
    
    tracked_people = tracker.track(formatted_detections, frame)
    
    
    def save_person_crop(img, path):
        cv2.imwrite(path, img)
    
    
    
            
    # Annotate and display
    frame = ui.draw_info(frame, people_count, congestion_level, gate_zone, density, alert_triggered, gate_status, people_below_line)
    cv2.imshow(f"Mofawij - {gate_zone}", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
database.close()
export_logs_to_excel()
