import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl

from importlib.resources import files

class FaceTracker(BaseControl):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        model_path = str(files("neuroarcade.assets").joinpath("face_landmarker.task"))
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )

        self.detector = vision.FaceLandmarker.create_from_options(options)
        self.neutral = None

    # -------------------------------------------------
    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.detector.detect(mp_image)
        direction = None

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            h, w, _ = frame.shape

            nose = landmarks[1]
            nx, ny = int(nose.x * w), int(nose.y * h)

            cv2.circle(frame, (nx, ny), 5, (0, 255, 0), -1)

            # Direction zones (thirds)
            if ny < h / 3:
                direction = Direction.UP
            elif ny > 2 * h / 3:
                direction = Direction.DOWN
            elif nx < w / 3:
                direction = Direction.LEFT
            elif nx > 2 * w / 3:
                direction = Direction.RIGHT

        return direction, frame

    # -------------------------------------------------
    def get_config_schema(self):
        return {}
