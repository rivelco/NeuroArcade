import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

from importlib.resources import files

from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles

def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  pose_landmark_style = drawing_styles.get_default_pose_landmarks_style()
  pose_connection_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2)

  for pose_landmarks in pose_landmarks_list:
    drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=pose_landmarks,
        connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
        landmark_drawing_spec=pose_landmark_style,
        connection_drawing_spec=pose_connection_style)

  return annotated_image

class PostureTracker(BaseControl):
    def __init__(self, camera=0, model_version="lite"):
        self.cap = cv2.VideoCapture(camera)
        
        if model_version == "lite":
            model_version = "pose_landmarker_lite.task"
        if model_version == "full":
            model_version = "pose_landmarker_full.task"
        if model_version == "heavy":
            model_version = "pose_landmarker_heavy.task"
        
        model_path = str(files("neuroarcade.assets").joinpath(model_version))
        
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)

        self.detector = vision.PoseLandmarker.create_from_options(options)

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
        
        h, w, _ = frame.shape

        result = self.detector.detect(mp_image)
        direction = None

        if result.pose_landmarks:
            frame = draw_landmarks_on_image(frame, result)
            nose = result.pose_landmarks[0][0]
            right_shoulder = result.pose_landmarks[0][11]
            right_hip = result.pose_landmarks[0][23]
            right_hand = result.pose_landmarks[0][15]
            left_shoulder = result.pose_landmarks[0][12]
            left_hip = result.pose_landmarks[0][24]
            left_hand = result.pose_landmarks[0][16]
            
            right_shoulder_hip = (left_hip.y + left_shoulder.y) / 2
            left_shoulder_hip = (right_hip.y + right_shoulder.y) / 2
            
            if left_hand.y < nose.y and right_hand.y < nose.y:
                # Both arms rise
                direction = Direction.UP
            elif left_hand.y < left_shoulder_hip and left_hand.x < left_shoulder.x:
                # Left hand rise
                direction = Direction.LEFT
            elif right_hand.y < right_shoulder_hip and right_hand.x > right_shoulder.x:
                # Right hand rise
                direction = Direction.RIGHT
            elif right_hand.y > right_hip.y and right_hand.y > right_hip.y:
                # Both arms down
                direction = Direction.DOWN
        
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
            "model_version": {
                "name": "Pose model",
                "description": "The lite model is faster, the heavy the most accurate",
                "default": "lite",
                "type": "enum",
                "options": ["lite", "full", "heavy"]
            }
        }

    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>
            <h1>Posture Tracker</h1>

            <div class="section">
                <p>
                    Change your body posture to change the movement in the game. In the current version only one body will be recognized.
                </p>
                <p>
                    <span class="highlight">The camera data never leaves your device nor is used to train another model and no video is recorded.</span>
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>This control is constantly capturing a video (a bunch of frames) and pass those to a local ML model.</li>
                    <li>The model recognizes how many bodies there are and will select one to place key landmarks.</li>
                    <li>Each landmark will be shown in the video feed and is associated to a different body part.</li>
                    <li>Using the body parts coordinates the program will estimate your current posture.</li>
                    <li>To move up rise both hands above your nose level and within your shoulders width.</li>
                    <li>To move down left both hands hanging down, below your hips.</li>
                    <li>To move left rise your left hand to the side, above the hips and below the left shoulder.</li>
                    <li>To move right rise your right hand to the side, above the hips and below the right shoulder.</li>
                    <li>To stay still keep your hands close to your chest, between your shoulders.</li>
                </ul>
            </div>
        </body>
        </html>
        """
