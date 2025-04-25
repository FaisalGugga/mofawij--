from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np

class PersonTracker:
    def __init__(self, max_age=30, n_init=3, max_cosine_distance=0.2):
        """
        Initialize the DeepSort tracker
        
        Args:
            max_age: How many frames a track can be missing before it's deleted
            n_init: How many detections needed before a track is confirmed
            max_cosine_distance: Threshold for feature similarity matching
        """
        # Create the DeepSort tracker
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            max_cosine_distance=max_cosine_distance
        )
        # Dictionary to store movement history for each tracked person
        self.track_history = {}
        
    def track(self, detections, frame):
        """
        Process detections and return tracked objects with IDs
        
        Args:
            detections: List of tuples ([x1, y1, width, height], confidence, class_id)
            frame: Current video frame
            
        Returns:
            List of tuples (track_id, x1, y1, x2, y2)
        """
        try:
            # Update tracks with DeepSort
            tracked_objects = self.tracker.update_tracks(detections, frame=frame)
            
            results = []
            for obj in tracked_objects:
                # Only use confirmed tracks
                if not obj.is_confirmed():
                    continue
                    
                track_id = obj.track_id
                
                # Get bounding box coordinates
                ltwh = obj.to_ltwh()  # left, top, width, height
                l, t, w, h = ltwh
                x1, y1, x2, y2 = l, t, l + w, t + h  # Convert to x1,y1,x2,y2 format
                
                # Store y-position history for movement analysis
                if track_id not in self.track_history:
                    self.track_history[track_id] = []
                
                # Record y-position
                center_y = (y1 + y2) / 2
                self.track_history[track_id].append(center_y)
                
                # Keep history limited to recent positions
                if len(self.track_history[track_id]) > 10:
                    self.track_history[track_id] = self.track_history[track_id][-10:]
                    
                # Add this track to results
                results.append((track_id, x1, y1, x2, y2))
            
            return results
            
        except Exception as e:
            print(f"Error in tracking: {e}")
            return []
        
    def is_track_moving_down(self, track_id, min_samples=5):
        """
        Check if a track is moving downward consistently
        
        Args:
            track_id: ID of the track to analyze
            min_samples: Minimum number of history points needed
            
        Returns:
            True if the track is moving downward, False otherwise
        """
        history = self.track_history.get(track_id, [])
        
        # Need enough history to determine direction
        if len(history) < min_samples:
            return False
        
        # Get recent positions
        recent = history[-min_samples:]
        
        # Calculate slope using linear regression
        x = np.arange(len(recent))
        y = np.array(recent)
        slope, _ = np.polyfit(x, y, 1)
        
        # Positive slope means moving down in image coordinates
        return slope > 0