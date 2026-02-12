import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.containers import NormalizedLandmark

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl

from importlib.resources import files

class ExpressionTracker(BaseControl):
    def __init__(self, camera=0,
                 gest_up = "rise_eyebrows", gest_down = "mouth_open", gest_left = "left_smile", gest_right = "right_smile",
                 prob_up = 0.4, prob_down = 0.4, prob_left = 0.4, prob_right = 0.4,
                 draw_lands = True, complete_lands=False, highlight_lands=True):
        self.cap = cv2.VideoCapture(camera)
        self.gest_up = gest_up
        self.gest_down = gest_down
        self.gest_left = gest_left
        self.gest_right = gest_right
        self.prob_up = prob_up
        self.prob_down = prob_down
        self.prob_left = prob_left
        self.prob_right = prob_right
        self.draw_complete_landmarks = complete_lands
        self.highlight_lands = highlight_lands
        self.draw_lands = draw_lands
        
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

            gest_up = self._get_blend(blends, self.gest_up)
            gest_down = self._get_blend(blends, self.gest_down)
            gest_right = self._get_blend(blends, self.gest_left)
            gest_left = self._get_blend(blends, self.gest_right)
            
            if gest_down > self.prob_down:
                direction = Direction.DOWN
            elif gest_left > self.prob_left:
                direction = Direction.LEFT
            elif gest_right > self.prob_right:
                direction = Direction.RIGHT
            elif gest_up > self.prob_up:
                direction = Direction.UP
        
        return direction, frame

    def _get_blend(self, blendshapes, name):
        for b in blendshapes:
            if b.category_name == name:
                return b.score
        return 0.0
    
    def paint_landmarks(self, frame, landmarks):
        h, w, _ = frame.shape
        coords = self.get_landmark_coords(landmarks, w, h)
        if self.draw_lands:
            if self.draw_complete_landmarks:
                for (x, y, _) in coords:
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
                if False:   # Draw the landmarks index, useful for debug
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
            else:
                for i in range(0, len(coords), 2):  # draw every 3rd point
                    x, y, _ = coords[i]
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
        if self.highlight_lands:
            nose = coords[1]
            cv2.circle(frame, (nose[0], nose[1]), 6, (0, 0, 255), -1)
            #left_eye = coords[33]
            #right_eye = coords[263]
            left_eyebrow = coords[52]
            right_eyebrow = coords[282]
            up_lip = coords[11]
            down_lip = coords[17]
            smile_left = coords[57]
            smile_right = coords[432]
            cv2.circle(frame, (left_eyebrow[0], left_eyebrow[1]), 5, (255, 255, 0), -1)
            cv2.circle(frame, (right_eyebrow[0], right_eyebrow[1]), 5, (255, 255, 0), -1)
            cv2.circle(frame, (up_lip[0], up_lip[1]), 5, (255, 255, 0), -1)
            cv2.circle(frame, (down_lip[0], down_lip[1]), 5, (255, 255, 0), -1)
            cv2.circle(frame, (smile_left[0], smile_left[1]), 5, (255, 255, 0), -1)
            cv2.circle(frame, (smile_right[0], smile_right[1]), 5, (255, 255, 0), -1)
        
        return frame

    def get_landmark_coords(self, landmarks: list[NormalizedLandmark], width: int, height: int) -> np.ndarray:
        """Extract normalized landmark coordinates to array of pixel coordinates."""
        xyz = [(lm.x, lm.y, lm.z) for lm in landmarks]
        return np.multiply(xyz, [width, height, width]).astype(int)

    # -------------------------------------------------
    def get_config_schema(self):
        available_gestures = [
            "browDownLeft",     "browDownRight",        "browInnerUp",      "browOuterUpLeft",
            "browOuterUpRight", "cheekPuff",            "cheekSquintLeft",  "cheekSquintRight",
            "eyeBlinkLeft",     "eyeBlinkRight",        "eyeLookDownLeft",  "eyeLookDownRight",
            "eyeLookInLeft",    "eyeLookInRight",       "eyeLookOutLeft",   "eyeLookOutRight",
            "eyeLookUpLeft",    "eyeLookUpRight",       "eyeSquintLeft",    "eyeSquintRight",
            "eyeWideLeft",      "eyeWideRight",         "jawForward",       "jawLeft",
            "jawOpen",          "jawRight",             "mouthClose",       "mouthDimpleLeft",
            "mouthDimpleRight", "mouthFrownLeft",       "mouthFrownRight",  "mouthFunnel",
            "mouthLeft",        "mouthLowerDownLeft",   "mouthLowerDownRight", "mouthPressLeft",
            "mouthPressRight",  "mouthPucker",          "mouthRight",       "mouthRollLower",
            "mouthRollUpper",   "mouthShrugLower",      "mouthShrugUpper",  "mouthSmileLeft",
            "mouthSmileRight",  "mouthStretchLeft",     "mouthStretchRight","mouthUpperUpLeft",
            "mouthUpperUpRight","noseSneerLeft",        "noseSneerRight"
        ]
        return {
            "camera": {
                "name": "Index of camera device",
                "description": "The index of camera device",
                "default": 0,
                "min": 0,
                "max": 50
            },
            "gest_up": {
                "name": "Gesture for Up",
                "description": "Gesture to make to move up",
                "type": "enum",
                "options": available_gestures,
                "default": "browInnerUp",
            },
            "gest_down": {
                "name": "Gesture for Down",
                "description": "Gesture to make to move down",
                "type": "enum",
                "options": available_gestures,
                "default": "jawOpen",
            },
            "gest_left": {
                "name": "Gesture for Left",
                "description": "Gesture to make to move left",
                "type": "enum",
                "options": available_gestures,
                "default": "mouthSmileLeft",
            },
            "gest_right": {
                "name": "Gesture for Right",
                "description": "Gesture to make to move right",
                "type": "enum",
                "options": available_gestures,
                "default": "mouthSmileRight",
            },
            "prob_up": {
                "name": "Threshold for up",
                "description": "The probability threshold for identifying up expression",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0,
            },
            "prob_left": {
                "name": "Threshold for left",
                "description": "The probability threshold for identifying left expression",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0,
            },
            "prob_right": {
                "name": "Threshold for right smile",
                "description": "The probability threshold for identifying right expression",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0,
            },
            "prob_down": {
                "name": "Threshold for mouth",
                "description": "The probability threshold for identifying down expression",
                "default": 0.4,
                "min": 0.000001,
                "max": 1.0,
            },
            "draw_lands": {
                "name": "Draw face landmarks",
                "description": "Check to show the landmarks in the face",
                "default": True,
                "min": 0,
                "max": 1,
            },
            "complete_lands": {
                "name": "Draw complete landmarks",
                "description": "Check for more points in the face, uncheck for faster drawing",
                "default": False,
                "min": 0,
                "max": 1,
            },
            "highlight_lands": {
                "name": "Highlight eyes and nose",
                "description": "Check to highlight eyes and nose",
                "default": True,
                "min": 0,
                "max": 1,
            },
        }

