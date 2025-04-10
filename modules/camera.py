import cv2

class Camera:
    #source can be chnaged into video.mp4
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release()
        cv2.waitKey(1)
        cv2.destroyAllWindows()