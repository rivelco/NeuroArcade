import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.containers import NormalizedLandmark

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

from importlib.resources import files

class GazeTracker(BaseControl):
    def __init__(self, camera=0, look_up=0.4, look_down=0.4, look_left=0.4, look_right=0.4):
        self.cap = cv2.VideoCapture(camera)
        self.look_up = look_up
        self.look_down = look_down
        self.look_left = look_left
        self.look_right = look_right
        
        model_path = str(files("neuroarcade.assets").joinpath("face_landmarker.task"))
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
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

        if result.face_landmarks and result.face_blendshapes:
            landmarks = result.face_landmarks[0]
            blends = result.face_blendshapes[0]

            h, w, _ = frame.shape
            nose = landmarks[1]
            nx, ny = int(nose.x * w), int(nose.y * h)

            if self.neutral is None:
                self.neutral = (nx, ny)

            frame = self.paint_landmarks(frame, result.face_landmarks[0])
            
            up = self._get_blend(blends, "eyeLookUpLeft")
            down = self._get_blend(blends, "eyeLookDownLeft")
            right = self._get_blend(blends, "eyeLookOutLeft")
            left = self._get_blend(blends, "eyeLookInLeft")

            if up > self.look_up:
                direction = Direction.UP
            elif left > self.look_left:
                direction = Direction.LEFT
            elif right > self.look_right:
                direction = Direction.RIGHT
            elif down > self.look_down:
                direction = Direction.DOWN
        
        return direction, frame

    def _get_blend(self, blendshapes, name):
        for b in blendshapes:
            if b.category_name == name:
                return b.score
        return 0.0
    
    def paint_landmarks(self, frame, landmarks):
        h, w, _ = frame.shape
        coords = self.get_landmark_coords(landmarks, w, h)
        if False: # Draw the landmarks index, useful for debug
            for idx, (x, y, _) in enumerate(coords):
                cv2.putText(
                    frame,
                    str(idx),
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA
                )
                
        nose = coords[1]
        cv2.circle(frame, (nose[0], nose[1]), 6, (0, 0, 255), -1)
        left_eye_left = coords[471]
        left_eye_middle = coords[468]
        left_eye_right = coords[469]
        right_eye_left = coords[476]
        right_eye_middle = coords[473]
        right_eye_right = coords[474]
        cv2.circle(frame, (left_eye_left[0], left_eye_left[1]), 5, (255, 255, 0), -1)
        cv2.circle(frame, (left_eye_middle[0], left_eye_middle[1]), 5, (255, 255, 0), -1)
        cv2.circle(frame, (left_eye_right[0], left_eye_right[1]), 5, (255, 255, 0), -1)
        cv2.circle(frame, (right_eye_left[0], right_eye_left[1]), 5, (255, 255, 0), -1)
        cv2.circle(frame, (right_eye_middle[0], right_eye_middle[1]), 5, (255, 255, 0), -1)
        cv2.circle(frame, (right_eye_right[0], right_eye_right[1]), 5, (255, 255, 0), -1)
            
        return frame

    def get_landmark_coords(self, landmarks: list[NormalizedLandmark], width: int, height: int) -> np.ndarray:
        """Extract normalized landmark coordinates to array of pixel coordinates."""
        xyz = [(lm.x, lm.y, lm.z) for lm in landmarks]
        return np.multiply(xyz, [width, height, width]).astype(int)

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
            "look_up": {
                "name": "Threshold for up",
                "description": "The probability threshold for identifying up gaze",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0
            },
            "look_down": {
                "name": "Threshold for down",
                "description": "The probability threshold for identifying down gaze",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0
            },
            "look_left": {
                "name": "Threshold for left",
                "description": "The probability threshold for identifying left gaze",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0
            },
            "look_right": {
                "name": "Threshold for right",
                "description": "The probability threshold for identifying right gaze",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0
            }
        }

    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>
            <h1>Gaze Tracker</h1>

            <div class="section">
                <p>
                    Place your face in the middle of the camera frames. The idea is that when looking forward you have the camera in the center of your FOV.
                    Once in this position, move your eyes up to move up, move left to mode left, and so on. You stay still by looking to the front.
                    This is challenging to do without someone telling you where to move, because following the game with your eyes may cause involuntary movements in the game.
                </p>
                <p>
                    <span class="highlight">The camera data never leaves your device nor is used to train another model and no video is recorded.</span>
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>This control is constantly capturing a video (a bunch of frames) and pass those to a local ML model.</li>
                    <li>The model recognizes key landmarks in your face and eyes and extract the coordinates of those points.</li>
                    <li>The model estimates where you're looking at using those coordinates.</li>
                    <li>You have to make saccadic eye movements to move in the games.</li>
                </ul>
            </div>
        </body>
        </html>
        """