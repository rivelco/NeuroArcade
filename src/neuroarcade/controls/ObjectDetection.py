import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

from importlib.resources import files

def draw_top_text(frame, text,
                  font=cv2.FONT_HERSHEY_SIMPLEX,
                  font_scale=1.0,
                  thickness=2,
                  text_color=(255, 255, 255),
                  bg_color=(0, 0, 0),
                  margin=20,
                  alpha=0.6):
    """
    Draw short text centered at the top of a frame.

    Parameters
    ----------
    frame : np.ndarray
        OpenCV BGR image.
    text : str
        Short text to draw.
    font : int
        OpenCV font.
    font_scale : float
        Font scale factor.
    thickness : int
        Text thickness.
    text_color : tuple
        BGR color for text.
    bg_color : tuple
        BGR color for background rectangle.
    margin : int
        Margin from top and sides.
    alpha : float
        Background transparency (0=transparent, 1=solid).

    Returns
    -------
    np.ndarray
        Frame with text overlay.
    """

    output = frame.copy()
    h, w = output.shape[:2]

    # Get text size
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    # Center horizontally
    x = (w - text_w) // 2
    y = margin + text_h

    # Background rectangle coords
    rect_x1 = x - 10
    rect_y1 = y - text_h - 10
    rect_x2 = x + text_w + 10
    rect_y2 = y + baseline + 10

    # Create overlay for transparency
    overlay = output.copy()
    cv2.rectangle(overlay,
                  (rect_x1, rect_y1),
                  (rect_x2, rect_y2),
                  bg_color,
                  -1)

    # Blend overlay
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    # Draw text
    cv2.putText(output,
                text,
                (x, y),
                font,
                font_scale,
                text_color,
                thickness,
                cv2.LINE_AA)

    return output


class ObjectDetection(BaseControl):
    def __init__(self, camera=0, model_version="lite0-8", num_objects = 10,
                 obj_up = "bald eagle", obj_down = "axolotl", obj_left = "scorpion", obj_right = "tarantula"):
        self.cap = cv2.VideoCapture(camera)
        self.obj_up = obj_up
        self.obj_down = obj_down
        self.obj_left = obj_left
        self.obj_right = obj_right
        
        if model_version == "lite0-8":
            model_version = "efficientnet_lite0.tflite"
        if model_version == "lite2-8":
            model_version = "efficientnet_lite2.tflite"
        
        model_path = str(files("neuroarcade.assets").joinpath(model_version))
        
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )
        options = vision.ImageClassifierOptions(
            base_options=base_options, max_results=num_objects)

        self.classifier = vision.ImageClassifier.create_from_options(options)

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

        result = self.classifier.classify(mp_image)
        direction = None

        if result.classifications:
            top_category = result.classifications[0].categories[0]
            frame = draw_top_text(frame, top_category.category_name)
            
            objs_up = self.obj_up.split(", ")
            objs_left = self.obj_left.split(", ")
            objs_right = self.obj_right.split(", ")
            objs_down = self.obj_down.split(", ")
            
            if top_category.category_name in objs_up:
                # Both arms rise
                direction = Direction.UP
            elif top_category.category_name in objs_left:
                # Left hand rise
                direction = Direction.LEFT
            elif top_category.category_name in objs_right:
                # Right hand rise
                direction = Direction.RIGHT
            elif top_category.category_name in objs_down:
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
            "num_objects": {
                "name": "Number of objects",
                "description": "Number of objects to identify in the frame",
                "default": 10,
                "min": 1,
                "max": 1000
            },
            "model_version": {
                "name": "Pose model",
                "description": "The lite0-8 model is faster, the lite2-8 the most accurate",
                "default": "lite0-8",
                "type": "enum",
                "options": ["lite0-8", "lite2-8"]
            },
            "obj_up": {
                "name": "Object for Up",
                "description": "Object to show to move up",
                "default": "bald eagle",
            },
            "obj_down": {
                "name": "Gesture for Down",
                "description": "Object to show to move down",
                "default": "axolotl",
            },
            "obj_left": {
                "name": "Gesture for Left",
                "description": "Object to show to move left",
                "default": "scorpion",
            },
            "obj_right": {
                "name": "Gesture for Right",
                "description": "Object to show to move right",
                "default": "tarantula",
            },
        }

    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>
            <h1>Object Detection</h1>

            <div class="section">
                <p>
                    Show different items to the camera feed to produce a specific movement in the game.
                </p>
                <p>
                    <span class="highlight">The camera data never leaves your device nor is used to train another model and no video is recorded.</span>
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>This control is constantly capturing a video (a bunch of frames) and pass those to a local ML model.</li>
                    <li>The model recognizes a limited amount of objects in the frame and those are classified.</li>
                    <li>Then will select the predicted "main" object shown and will check if that object is related to a movement.</li>
                    <li>The "main" object in the frame will be displayed on top of the video feed.</li>
                    <li>The model recognizes over 1000 different objects, so better check how the model recognizes 
                        the objects you want to use and use those names in the parameters box.</li>
                    <li>Increase the number of objected identified per frame to increase stability at the cost of speed.</li>
                </ul>
            </div>
        </body>
        </html>
        """