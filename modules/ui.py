import cv2

class UI:
    def draw_info(self, frame, people_count, congestion_level, gate_zone, density, alert_triggered, gate_status, crossed_count):
        # Define colors
        colors = {
            "LOW": (0, 255, 0),    # Green
            "MEDIUM": (0, 255, 255), # Yellow
            "HIGH": (0, 0, 255),     # Red
            "alert": (0, 0, 255)     # Red for alerts
        }
        
        # Draw semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Get current color based on congestion level
        current_color = colors.get(congestion_level, (255, 255, 255))
        
        # Prepare text lines with color coding
        lines = [
            (f"Gate: {gate_zone} | People: {people_count} | Congestion: {congestion_level}", current_color),
            (f"Density: {density:.2f} p/m²", (255, 255, 255)),
            (f"ALERT: {alert_triggered}", colors["alert"] if "High Congestion" in alert_triggered else (255, 255, 255)),
            (f"Gate Status: {gate_status}", (255, 255, 255)),
            (f"People Crossed Line: {crossed_count}", (255, 255, 255))
        ]

        # Draw each line with appropriate color
        for i, (text, color) in enumerate(lines):
            y = 30 + (i * 25)
            cv2.putText(frame, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return frame