import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

from importlib.resources import files

class FaceTracker(BaseControl):
    def __init__(self, camera=0):
        self.cap = cv2.VideoCapture(camera)
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
        return {
            "camera": {
                "name": "Index of camera device",
                "description": "The index of camera device",
                "default": 0,
                "min": 0,
                "max": 50
            },
        }

    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>
            <h1>Expression Tracker</h1>

            <div class="section">
                <p>
                    Place your nose in different parts of the camera frame to interact with the game.
                </p>
                <p>
                    <span class="highlight">The camera data never leaves your device nor is used to train another model and no video is recorded.</span>
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>This control is constantly capturing a video (a bunch of frames) and pass those to a local ML model.</li>
                    <li>The model recognizes the nose landmark in your face and extract the coordinates of that point.</li>
                    <li>Your nose will be identified in each frame with a green point.</li>
                    <li>You have to move your face around to move in the game.</li>
                    <li>Move to the upper part of the frame to move up, to the left part of the frame to move left and so on.</li>
                </ul>
            </div>
        </body>
        </html>
        """