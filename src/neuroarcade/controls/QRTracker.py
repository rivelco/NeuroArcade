import cv2
from neuroarcade.controls.base import BaseControl
from neuroarcade.core.direction import Direction


class QRTracker(BaseControl):
    def __init__(self, camera_index=0, downscale=0.5, frames_threshold=3):
        self.cap = cv2.VideoCapture(camera_index)
        self.detector = cv2.QRCodeDetector()
        self.downscale = downscale
        self.frames_threshold = frames_threshold

        # Optional smoothing (prevents jittery direction flips)
        self.last_direction = None
        self.last_directions = []

    # --------------- BaseControl API ----------------

    def update(self) -> tuple[Direction | None, "cv2.Mat"]:
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)

        # Downscale for speed
        small = cv2.resize(frame, None, fx=self.downscale, fy=self.downscale)
        _, pts, _ = self.detector.detectAndDecode(small)

        direction = None

        if pts is not None:
            # Scale points back to original resolution
            pts = pts[0] / self.downscale

            cx = int(pts[:, 0].mean())
            cy = int(pts[:, 1].mean())
            h, w, _ = frame.shape

            # Visual marker
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

            # Direction zones (thirds)
            if cy < h / 3:
                direction = Direction.UP
            elif cy > 2 * h / 3:
                direction = Direction.DOWN
            elif cx < w / 3:
                direction = Direction.LEFT
            elif cx > 2 * w / 3:
                direction = Direction.RIGHT

        # Simple smoothing: avoid flicker when QR disappears for 1 frame
        if direction is None:
            direction = self.last_direction
        else:
            if direction != self.last_direction:
                self.last_directions = [direction]
            else:
                self.last_directions.append(direction)
            if len(self.last_directions) >= 3:
                self.last_direction = direction
            else:
                direction = self.last_direction

        return direction, frame
    
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {
            "camera_index": {
                "name": "Camera index", 
                "description": "Index of the camera to use", 
                "min": 0, 
                "max": 60, 
                "default": 0
                },
            "downscale": {
                "name": "Downscale factor", 
                "description": "Downscale factor for the camera image. Smaller values increases speed but reduce recognition", 
                "min": 0.00001, 
                "max": 1, 
                "default": 0.5
                },
            "frames_threshold": {
                "name": "Frames threshold", 
                "description": "Number of consecutive frames that the QR must be in a place to mark it as effective.", 
                "min": 1, 
                "max": 10000, 
                "default": 3
                },
        }

    # --------------- Cleanup ----------------

    def release(self):
        if self.cap.isOpened():
            self.cap.release()

