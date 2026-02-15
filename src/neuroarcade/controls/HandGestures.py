import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

from importlib.resources import files

def draw_landmarks_on_image(rgb_image, detection_result):
    mp_hands = mp.tasks.vision.HandLandmarksConnections
    mp_drawing = mp.tasks.vision.drawing_utils
    mp_drawing_styles = mp.tasks.vision.drawing_styles
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)
    
    MARGIN = 10  # pixels
    FONT_SIZE = 1
    FONT_THICKNESS = 1
    HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        mp_drawing.draw_landmarks(
            annotated_image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image

class HandGestures(BaseControl):
    def __init__(self, camera=0, gest_up="Pointing_Up", gest_down="Thumb_Down", gest_left="Open_Palm", gest_right="Closed_Fist"):
        self.gest_up = gest_up
        self.gest_down = gest_down
        self.gest_left = gest_left
        self.gest_right = gest_right
        
        self.cap = cv2.VideoCapture(camera)
        model_path = str(files("neuroarcade.assets").joinpath("gesture_recognizer.task"))
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        self.detector = vision.GestureRecognizer.create_from_options(options)

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

        direction = None
        
        recognition_result = self.detector.recognize(mp_image)
        
        frame = draw_landmarks_on_image(frame, recognition_result)

        # Directions
        if len(recognition_result.gestures):
            gesture = recognition_result.gestures[0][0].category_name
            if gesture == self.gest_up:
                direction = Direction.UP
            elif gesture == self.gest_down:
                direction = Direction.DOWN
            elif gesture == self.gest_left:
                direction = Direction.LEFT
            elif gesture == self.gest_right:
                direction = Direction.RIGHT

        return direction, frame

    # -------------------------------------------------
    def get_config_schema(self):
        available_gestures = ["Closed_Fist",
                            "Open_Palm",
                            "Pointing_Up",
                            "Thumb_Down",
                            "Thumb_Up",
                            "Victory"]
                            #"ILoveYou"]
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
                "default": "Pointing_Up"
            },
            "gest_down": {
                "name": "Gesture for Down",
                "description": "Gesture to make to move down",
                "type": "enum",
                "options": available_gestures,
                "default": "Thumb_Down"
            },
            "gest_left": {
                "name": "Gesture for Left",
                "description": "Gesture to make to move left",
                "type": "enum",
                "options": available_gestures,
                "default": "Open_Palm"
            },
            "gest_right": {
                "name": "Gesture for Right",
                "description": "Gesture to make to move right",
                "type": "enum",
                "options": available_gestures,
                "default": "Victory"
            },
        }

    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>
            <h1>Hand Gestures Tracker</h1>

            <div class="section">
                <p>
                    Make different gestures using your hands to move in the game. This version needs and will use the data of only one hand at the time.
                </p>
                <p>
                    <span class="highlight">The camera data never leaves your device nor is used to train another model and no video is recorded.</span>
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>This control is constantly capturing a video (a bunch of frames) and pass those to a local ML model.</li>
                    <li>The model recognizes hands in the frame, keeps only one hand and then identify key landmarks in that hand.</li>
                    <li>Those key landmarks will be shown in the camera feed and will be used to predict a hand gesture.</li>
                    <li>You can tune the hand gesture using the parameters box.</li>
                    <li>Change between gestures to change the movement. You can move your hand out of the frame to stay still.</li>
                </ul>
            </div>
        </body>
        </html>
        """