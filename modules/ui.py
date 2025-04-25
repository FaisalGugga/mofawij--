import cv2
import time

class UI:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.font_thickness = 2
        self.line_thickness = 2
        
        # Color scheme
        self.colors = {
            "LOW": (0, 255, 0),     # Green
            "MEDIUM": (0, 255, 255), # Yellow
            "HIGH": (0, 0, 255),     # Red
            "alert": (0, 0, 255),    # Red for alerts
            "tracked": (255, 0, 0),  # Blue for tracked objects
            "crossed": (255, 165, 0), # Orange for already crossed
            "text_bg": (0, 0, 0),    # Black for text background
            "white": (255, 255, 255) # White for general text
        }
        
        # Store FPS calculation variables
        self.prev_frame_time = 0
        self.curr_frame_time = 0
        
    def draw_info(self, frame, people_count, congestion_level, gate_zone, density, 
                 alert_triggered, gate_status, crossed_count):
        """Draw system status information on the frame"""
        # Calculate FPS
        self.curr_frame_time = time.time()
        fps = 1 / (self.curr_frame_time - self.prev_frame_time) if self.prev_frame_time > 0 else 0
        self.prev_frame_time = self.curr_frame_time
        
        # Draw semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 140), self.colors["text_bg"], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Get current color based on congestion level
        current_color = self.colors.get(congestion_level, self.colors["white"])
        
        # Prepare text lines with color coding
        lines = [
            (f"Gate: {gate_zone} | People in Frame: {people_count} | FPS: {fps:.1f}", self.colors["white"]),
            (f"Congestion Level: {congestion_level}", current_color),
            (f"Density: {density:.2f} p/m²", self.colors["white"]),
            (f"ALERT: {alert_triggered}", self.colors["alert"] if "High Congestion" in alert_triggered else self.colors["white"]),
            (f"Gate Status: {gate_status}", self.colors["white"]),
            (f"People Crossed Line: {crossed_count}", self.colors["crossed"])
        ]

        # Draw each line with appropriate color
        for i, (text, color) in enumerate(lines):
            y = 30 + (i * 20)
            cv2.putText(frame, text, (20, y), self.font, self.font_scale, color, self.font_thickness)

        return frame
    
    def draw_tracks(self, frame, tracks, crossed_ids=None):
        """
        Draw tracking boxes and IDs with different colors for crossed/non-crossed
        
        Args:
            frame: Video frame to draw on
            tracks: List of (track_id, x1, y1, x2, y2) tuples
            crossed_ids: Set of track IDs that have already crossed the line
        """
        if crossed_ids is None:
            crossed_ids = set()
            
        for track_id, x1, y1, x2, y2 in tracks:
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Choose color based on whether track has crossed line
            color = self.colors["crossed"] if track_id in crossed_ids else self.colors["tracked"]
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.line_thickness)
            
            # Draw track ID
            id_text = f"ID: {track_id}"
            
            # Add a small filled rectangle behind the text for better visibility
            text_size = cv2.getTextSize(id_text, self.font, self.font_scale, self.font_thickness)[0]
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + text_size[0], y1), color, -1)
            cv2.putText(frame, id_text, (x1, y1 - 5), self.font, self.font_scale, 
                       self.colors["white"], self.font_thickness)
            
        return frame
    
    def draw_congestion_line(self, frame, y_position, people_below=0):
        """Draw the congestion line with count of people who crossed"""
        # Draw the line
        cv2.line(frame, (0, y_position), (frame.shape[1], y_position), 
                self.colors["alert"], self.line_thickness)
        
        # Label the line
        cv2.putText(frame, f"Congestion Line ({people_below} crossed)", 
                   (10, y_position - 10), self.font, self.font_scale, 
                   self.colors["alert"], self.font_thickness)
        
        return frame