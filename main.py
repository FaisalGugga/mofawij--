from modules.camera import Camera
from modules.detection import PeopleDetector
from modules.tracking import PersonTracker
from modules.ui import UI
from modules.data_manager import DataManager
from modules.alerts import AlertSystem
import cv2
import time
from datetime import datetime

# Initialize components
video_path = r"C:\Users\fa15s\OneDrive\Documents\Visual-Projects\PythonProjects\SAF_Project_Mofawij\Test6.mp4"
camera = Camera(source=video_path)
detector = PeopleDetector()
tracker = PersonTracker()
ui = UI()
data_manager = DataManager()  # Initialize data manager from the imported module
alert_system = AlertSystem()  # Initialize alert system

# Define settings
# Use int() to ensure the congestion line Y position is an integer
CONGESTION_LINE_Y = int(550 * 0.75)  # Adjust for new resolution
gate_zone = "Gate A"

# Define gate capacity settings
TARGET_NUMBER = 35  # Target number for the gate
GATE_LIMIT = 65    # Gate limit for congestion

# Initialize counters
people_below_line = 0
crossed_track_ids = set()  # Set to store IDs of people who crossed the line

# Performance optimization variables
frame_count = 0
skip_frames = 2  # Process every 3rd frame
process_width, process_height = 640, 640  # Lower resolution for processing
display_width, display_height = 960, 960  # Keep display resolution higher if needed

# FPS calculation variables
fps = 0
frame_times = []
start_time = time.time()

# Database logging settings
log_interval = 5  # Log data every 5 seconds
last_log_time = time.time()

# Initialize tracks list
tracks = []

try:
    # Main processing loop
    while True:
        # Get next frame
        frame = camera.get_frame()
        if frame is None:
            print("End of video reached")
            break
        
        # FPS calculation
        current_time = time.time()
        frame_times.append(current_time)
        # Only keep the last 30 frame times for FPS calculation
        if len(frame_times) > 30:
            frame_times.pop(0)
        if len(frame_times) > 1:
            fps = len(frame_times) / (frame_times[-1] - frame_times[0])
        
        # Skip frames to improve performance
        frame_count += 1
        
        # Always resize for display
        display_frame = cv2.resize(frame, (display_width, display_height))
        
        # Process only every nth frame for detection and tracking
        if frame_count % (skip_frames + 1) == 0:
            # Resize frame for processing - smaller resolution is faster
            process_frame = cv2.resize(frame, (process_width, process_height))
            
            # 1. DETECT - Use YOLO to find people in the current frame
            detection_results = detector.detect(process_frame)
            
            # 2. FORMAT - Convert YOLO format to DeepSort format
            detections_for_tracker = []
            for x1, y1, x2, y2, confidence in detection_results:
                # DeepSort expects [left, top, width, height]
                width = x2 - x1
                height = y2 - y1
                bbox = [float(x1), float(y1), float(width), float(height)]
                detections_for_tracker.append((bbox, float(confidence), 0))  # 0 = person class
            
            # 3. TRACK - Update tracks with DeepSort
            tracks = tracker.track(detections_for_tracker, process_frame)
        
        # Scale tracks to display resolution (if tracks exist)
        display_tracks = []
        for track_id, x1, y1, x2, y2 in tracks:
            scale_x = display_width / process_width
            scale_y = display_height / process_height
            display_tracks.append((
                track_id,
                int(x1 * scale_x),  # Convert to int
                int(y1 * scale_y),  # Convert to int
                int(x2 * scale_x),  # Convert to int
                int(y2 * scale_y)   # Convert to int
            ))
        
        # Process each track for line crossing (still maintain this for statistics)
        for track_id, x1, y1, x2, y2 in display_tracks:
            # Check if person has crossed the line
            currently_below_line = y2 > CONGESTION_LINE_Y
            
            # Only count people crossing the line once (using their unique track_id)
            if currently_below_line and track_id not in crossed_track_ids:
                # Check if they were previously above the line (real crossing)
                history = tracker.track_history.get(track_id, [])
                # Scale history y-coordinates to display resolution
                scaled_history = [y * display_height / process_height for y in history]
                has_been_above = any(y < CONGESTION_LINE_Y for y in scaled_history)
                is_moving_down = tracker.is_track_moving_down(track_id)
                
                if has_been_above and is_moving_down:
                    # Valid crossing detected
                    people_below_line += 1
                    crossed_track_ids.add(track_id)
                    print(f"Person ID {track_id} crossed the line! Total crossed: {people_below_line}")
        
        # Draw visualizations
        display_frame = ui.draw_tracks(display_frame, display_tracks, crossed_track_ids)
        display_frame = ui.draw_congestion_line(display_frame, CONGESTION_LINE_Y, people_below_line)
        
        # Calculate congestion level based on TOTAL PEOPLE IN FRAME
        total_people_in_frame = len(display_tracks)
        
        # Get alert message from AlertSystem
        alert_message, gate_recommendation = alert_system.check_congestion(total_people_in_frame)
        
        # Determine congestion level based on total people in frame
        if total_people_in_frame < TARGET_NUMBER:
            congestion_level = "LOW"
            congestion_message = "No congestion"
            action_message = "Keep gate open"
            gate_status = "OPEN"
            alert_triggered = "NONE"
            congestion_ratio = total_people_in_frame / GATE_LIMIT  # For visualization
        elif total_people_in_frame >= TARGET_NUMBER and total_people_in_frame < GATE_LIMIT:
            congestion_level = "MEDIUM"
            congestion_message = "Moderate congestion"
            action_message = "Monitor closely"
            gate_status = "OPEN"
            alert_triggered = "WARNING"
            congestion_ratio = total_people_in_frame / GATE_LIMIT  # For visualization
        else:  # total_people_in_frame >= GATE_LIMIT
            congestion_level = "HIGH"
            congestion_message = "High congestion"
            action_message = "Consider closing gate"
            gate_status = "CLOSING"
            alert_triggered = "CRITICAL"
            congestion_ratio = 1.0  # Max ratio for visualization
        
        # Log data to database at specified intervals
        if current_time - last_log_time >= log_interval:
            try:
                data_manager.log_data(
                    total_people_in_frame,  # People count
                    congestion_level,       # Congestion level
                    gate_zone,              # Gate zone 
                    congestion_ratio,       # Density
                    alert_triggered,        # Alert triggered
                    gate_status,            # Gate status
                    people_below_line       # People below line
                )
                last_log_time = current_time
                print(f"Data logged to database at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as db_error:
                print(f"Database error: {db_error}")
        
        # Display counts and information
        display_frame = ui.draw_info(
            display_frame, 
            total_people_in_frame,  # Total people currently in frame
            congestion_level, 
            gate_zone, 
            congestion_ratio,  # Normalized between 0 and 1
            alert_message,     # Using alert message from AlertSystem
            gate_recommendation,  # Using gate recommendation from AlertSystem
            people_below_line  # Keep tracking of crossed people as additional info
        )
        
        # Add gate capacity information
        cv2.putText(
            display_frame, 
            f"Target: {TARGET_NUMBER} | Limit: {GATE_LIMIT}", 
            (10, 150), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (255, 255, 255), 
            2
        )
        
        # Add database logging indicator
        seconds_until_next_log = max(0, int(log_interval - (current_time - last_log_time)))
        cv2.putText(
            display_frame, 
            f"DB Log in: {seconds_until_next_log}s", 
            (10, 180), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (0, 255, 255), 
            2
        )
        
        # Display the result
        cv2.imshow(f"Mofawij - {gate_zone}", display_frame)
        
        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error in main loop: {e}")

finally:
    # Clean up resources
    print("Cleaning up resources...")
    camera.release()
    cv2.destroyAllWindows()
    data_manager.close()  # Close database connection
    print("Application terminated.")