# modules/tracking.py

from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=30)

    def track(self, detections, frame):
        """
        Takes detections and returns tracked object IDs and bounding boxes.
        detections: list of [x1, y1, x2, y2, confidence]
        Returns: list of (track_id, x1, y1, x2, y2)
        """
        tracked_objects = self.tracker.update_tracks(detections, frame=frame)

        results = []
        for obj in tracked_objects:
            if not obj.is_confirmed():
                continue
            track_id = obj.track_id
            ltrb = obj.to_ltrb()  # left, top, right, bottom
            results.append((track_id, *ltrb))

        return results
