import cv2
from neuroarcade.controls.base import BaseControl
from neuroarcade.core.direction import Direction


class QRTracker(BaseControl):
    def __init__(self, camera_index=0, downscale=0.5):
        self.cap = cv2.VideoCapture(camera_index)
        self.detector = cv2.QRCodeDetector()
        self.downscale = downscale

        # Optional smoothing (prevents jittery direction flips)
        self.last_direction = None

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
            self.last_direction = direction

        return direction, frame

    # --------------- Cleanup ----------------

    def release(self):
        if self.cap.isOpened():
            self.cap.release()

