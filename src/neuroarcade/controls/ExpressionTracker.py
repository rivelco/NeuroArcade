import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl

from importlib.resources import files

class ExpressionTracker(BaseControl):
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
        self.mode = "head_pose"
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

        if result.face_landmarks and result.face_blendshapes:
            landmarks = result.face_landmarks[0]
            blends = result.face_blendshapes[0]

            h, w, _ = frame.shape
            nose = landmarks[1]
            nx, ny = int(nose.x * w), int(nose.y * h)

            if self.neutral is None:
                self.neutral = (nx, ny)

            dx = nx - self.neutral[0]
            dy = ny - self.neutral[1]

            thresh = 25

            # ---------------- MODES ----------------
            if self.mode == "head_pose":
                if dy < -thresh:
                    direction = Direction.UP
                elif dy > thresh:
                    direction = Direction.DOWN
                elif dx < -thresh:
                    direction = Direction.LEFT
                elif dx > thresh:
                    direction = Direction.RIGHT

            elif self.mode == "eyebrows":
                brow = self._get_blend(blends, "browInnerUp")
                if brow > 0.4:
                    direction = Direction.UP

            elif self.mode == "mouth":
                mouth = self._get_blend(blends, "jawOpen")
                if mouth > 0.5:
                    direction = Direction.DOWN

            elif self.mode == "smile":
                left = self._get_blend(blends, "mouthSmileLeft")
                right = self._get_blend(blends, "mouthSmileRight")

                if left > 0.4:
                    direction = Direction.LEFT
                elif right > 0.4:
                    direction = Direction.RIGHT

            elif self.mode == "gaze":
                up = self._get_blend(blends, "eyeLookUpLeft")
                down = self._get_blend(blends, "eyeLookDownLeft")
                left = self._get_blend(blends, "eyeLookOutLeft")
                right = self._get_blend(blends, "eyeLookInLeft")

                if up > 0.4:
                    direction = Direction.UP
                elif down > 0.4:
                    direction = Direction.DOWN
                elif left > 0.4:
                    direction = Direction.LEFT
                elif right > 0.4:
                    direction = Direction.RIGHT
        
        return direction, frame

    def _get_blend(self, blendshapes, name):
        for b in blendshapes:
            if b.category_name == name:
                return b.score
        return 0.0

    # -------------------------------------------------
    def get_config_schema(self):
        return {}

