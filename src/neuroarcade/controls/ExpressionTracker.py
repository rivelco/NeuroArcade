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

class ExpressionTracker(BaseControl):
    """
    Creates a mediapipe based controller that uses and tracks the facial gestures
    made by the user to return a direction.
    
    For this controller to work a camera is needed.
    """
    def __init__(self, camera=0,
                 gest_up = "rise_eyebrows", gest_down = "mouth_open", gest_left = "left_smile", gest_right = "right_smile",
                 prob_up = 0.4, prob_down = 0.4, prob_left = 0.4, prob_right = 0.4,
                 draw_lands = True, complete_lands=False, highlight_lands=True):
        """Initializes an Expression Identifier mediapipe based controller.
        
        The function initializes a mediapipe detector using the `face_landmarker.task` model.

        Args:
            camera (int, optional): Index of the camera device to use. Defaults to 0.
            gest_up (str, optional): Key name of the gesture to use to move UP. Defaults to "rise_eyebrows".
            gest_down (str, optional): Key name of the gesture to use to move DOWN. Defaults to "mouth_open".
            gest_left (str, optional): Key name of the gesture to use to move left. Defaults to "left_smile".
            gest_right (str, optional): Key name of the gesture to use to move RIGHT. Defaults to "right_smile".
            prob_up (float, optional): Threshold probability to identify the gesture for UP. Defaults to 0.4.
            prob_down (float, optional): Threshold probability to identify the gesture for DOWN. Defaults to 0.4.
            prob_left (float, optional): Threshold probability to identify the gesture for LEFT. Defaults to 0.4.
            prob_right (float, optional): Threshold probability to identify the gesture for RIGHT. Defaults to 0.4.
            draw_lands (bool, optional): Whether or not to show landmarks in the camera feed. Defaults to True.
            complete_lands (bool, optional): Whether or not to show the complete landmarks on the camera feed. Defaults to False.
            highlight_lands (bool, optional): Whether or not to show the highlighted landmarks. Defaults to True.
        """
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
    def update(self) -> tuple[Direction, np.ndarray]:
        """
        A frame is acquired by the camera and processed by the mediapipe model.
        The face landmarks are extracted and a gesture is identified using the 
        probability threshold of each one.
        
        If the user has selected the drawing of the landmarks then those are added
        to the frame
        
        Returns:
            tuple[Direction | None, np.ndarray | None]:
                - Direction: The selected movement direction. If no action
                  is chosen during this tick, return None.
                - np.ndarray: The camera image with annotated landmarks.
        """
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
    
    def paint_landmarks(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Paints landmarks in a frame if those are requested.

        Args:
            frame (np.ndarray): Frame where to paint the landmarks
            landmarks (result.face_landmarks): landmarks from the mediapipe detector

        Returns:
            np.ndarray: New frame with the landmarks drawn.
        """
        
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
        """Extract normalized landmark coordinates to array of pixel coordinates.

        Args:
            landmarks (list[NormalizedLandmark]): Landmarks from the mediapipe detector.
            width (int): Width in pixels of the frame
            height (int): Height in pixels of the frame

        Returns:
            np.ndarray: Numpy array with the scaled coordinates of the landmarks.
        """
        xyz = [(lm.x, lm.y, lm.z) for lm in landmarks]
        return np.multiply(xyz, [width, height, width]).astype(int)

    # -------------------------------------------------
    def get_config_schema(self) -> dict:
        """Configurable options for the controller. 
        Also lists all the different types of gestures.

        Returns:
            dict: Configuration dictionary.
        """
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
            },
            "complete_lands": {
                "name": "Draw complete landmarks",
                "description": "Check for more points in the face, uncheck for faster drawing",
                "default": False,
            },
            "highlight_lands": {
                "name": "Highlight eyes and nose",
                "description": "Check to highlight eyes and nose",
                "default": True,
            },
        }

    def get_instructions(self) -> str:
        """Instructions for the controller.
        
        Returns:
            str: Text containing the HTML code to use for the instructions window.
        """
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>
            <h1>Expression Tracker</h1>

            <div class="section">
                <p>
                    Make different facial gestures to control the movement in the game. You need a working camera connected for this control to work.
                </p>
                <p>
                    <span class="highlight">The camera data never leaves your device nor is used to train another model and no video is recorded.</span>
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>This control is constantly capturing a video (a bunch of frames) and pass those to a local ML model.</li>
                    <li>The model recognizes key landmarks in your face and extract the coordinates of those points.</li>
                    <li>You can visualize key landmarks of your face using the parameters box. Some key-key landmarks are shown in different colors.</li>
                    <li>The model identifies the specific distribution of landmarks to identify a gesture.</li>
                    <li>The model reports a probability of you doing a specific gesture.</li>
                    <li>If the probability is high enough then the gesture is parsed to a specific movement direction.</li>
                    <li>You can tune this probabilities parameter and a list of available recognizable gestures in the parameters box.</li>
                </ul>
            </div>
        </body>
        </html>
        """