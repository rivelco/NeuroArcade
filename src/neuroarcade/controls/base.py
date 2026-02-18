from abc import ABC, abstractmethod
from neuroarcade.core.direction import Direction
import numpy as np

class BaseControl(ABC):
    """
        Abstract base class for all game input controllers.

        A BaseControl implementation is responsible for producing movement
        decisions during each iteration of the main game loop. Subclasses
        may represent human input, AI agents, scripted behavior, or
        machine-learning based controllers.

        The `update()` method is called once per game tick and must return
        the desired movement direction along with optional auxiliary data
        (e.g., model outputs, debug arrays, or feature maps).
        
        The `get_config_schema()` method is called once every time the control
        is loaded and must return a dict with the parameters of the controller.
        This dict is used to setup the controller parameters box.
        
        The `get_instructions()` method is called once every time the control
        is loaded and must return a text containing the instructions. This info
        is shown to the user in a separate window when the  "Show instructions"
        button is pressed.

        Subclasses must implement the `update()`, `get_config_schema()` and
        the `get_instructions()` methods.
    """
    @abstractmethod
    def update(self) -> tuple[Direction | None, np.ndarray | None]:
        """Execute one control step.

        This method is invoked by the main game loop at every update cycle.
        It should determine the next action to perform.

        Returns:
            tuple[Direction | None, np.ndarray | None]:
                - Direction: The selected movement direction. If no action
                  is chosen during this tick, return None.
                - np.ndarray:
                    An optional visualization frame (e.g., camera image,
                    annotated landmarks, or model overlay) to be displayed
                    in the UI. Return None if the controller does not
                    provide a visual output.
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> dict:
        """Parameters that the UI can expose dynamically. The parameters are defined in
        a dictionary, containing a unique key for each parameter and another dictionary as a value.
        
        The key of each parameter will be passed to the __init__ function of the subclasses, so
        those keys should match the name of the parameters expected by the constructor.
        
        The parameters may look like:
        
        Example:
        
            .. code-block:: python
            
                {
                    "camera": {
                        # The label of the input field
                        "name": "Index of camera device",
                        # Shows as a tooltip in the UI
                        "description": "The index of camera device",
                        # An appropriated input widget is used from the type of the default value
                        # This is also the default value in the UI
                        "default": 0,
                        # Use "min" and "max" to stablish the allowed range for the numeric inputs.
                        "min": 0,
                        "max": 50
                    },
                    "gest_up": {
                        # The label of the input field
                        "name": "Gesture for Up",
                        # Shows as a tooltip in the UI
                        "description": "Gesture to make to move up",
                        # Set the "type": "enum" field to load a list of selectable options
                        "type": "enum",
                        # options field containing the elements to be listed
                        "options": ["eyeBlinkLeft","eyeBlinkRight","browInnerUp"],
                        # Default value, must be in the options list
                        "default": "browInnerUp",
                    },
                    "draw_lands": {
                        "name": "Draw face landmarks",
                        "description": "Check to show the landmarks in the face",
                        # The boolean parameters will be shown ad check boxes and no other fields are needed
                        "default": True,
                    },
                    "obj_right": {
                        "name": "Gesture for Right",
                        "description": "Object to show to move right",
                        # The text inputs only needs the string with the default values
                        "default": "tarantula",
                    },
                }

        Returns:
            dict: Dictionary with the parameters and their options.
        """
        pass
    
    @abstractmethod
    def get_instructions(self) -> str:
        """Return instructions the UI should expose, as HTML formatted text.
        Include the `INSTRUCTIONS_HEAD` variable from the `neuroarcade.ui.instructions_html`
        to load the styles.
        
        Example:

            .. code-block:: python
            
                \"""<html>
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
                </html>\"""

        Returns:
            str: String containing HTML formatted text to show the instructions of the
            control. 
        """
        pass