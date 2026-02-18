from abc import ABC, abstractmethod
import numpy as np
from importlib.resources import files
from neuroarcade.core.direction import Direction
from neuroarcade.core.SoundManager import SoundManager

class BaseGame(ABC):
    def __init__(self):
        """
        Abstract base class for all NeuroArcade games.

        A BaseGame implementation encapsulates the full game lifecycle,
        including state management, rendering, sound effects, and
        configuration exposure.

        The expected execution flow is:

            1. initialize_sounds()
            2. reset()
            3. start()
            4. Repeatedly:
                update(direction)
                render()
            5. stop()

        Subclasses must implement all abstract methods to define
        game-specific behavior.
        """
        self._running = False

    def start(self):
        """
        Start the game loop.

        Sets the internal running flag to True.
        """
        self._running = True

    def stop(self):
        """
        Stop the game loop.

        Sets the internal running flag to False.
        """
        self._running = False

    def is_running(self) -> bool:
        """
        Useful to identify events like game over or other scenarios.
        
        Returns:
            bool: True if the game is currently running.
        """
        return self._running
    
    def initialize_sounds(self, volume=0.4):
        """
        Load and register game sound effects.

        This method automatically discovers WAV files inside the
        `neuroarcade.sounds` package that follow the naming convention:

            effect_<name>.wav

        Each valid file is registered in the SoundManager under `<name>`.

        Args:
            volume (float, optional): Initial playback volume in range [0.0, 1.0]. Defaults to 0.4.
        """
        self.sounds = SoundManager()
        sounds_package = files("neuroarcade.sounds")

        for file in sounds_package.iterdir():
            if not file.is_file():
                continue
            filename = file.name
            
            # Only WAV files starting with "effect_"
            if filename.startswith("effect_") and filename.endswith(".wav"):
                # Remove prefix and extension
                effect_name = filename[len("effect_"):-4]
                path = str(file)
                self.sounds.load(
                    name=effect_name,
                    path=path,
                    volume=volume
                )

    @abstractmethod
    def reset(self):
        """
        Reset the game state to its initial configuration.

        This method should:
            - Reloads the game parameters
            - Clear scores
            - Reset player state
            - Reinitialize game objects
            - Prepare the game for a new session
        """
        pass

    @abstractmethod
    def update(self, direction: Direction | None):
        """
        Advance the game by one tick.

        This method is called once per iteration of the main game loop.

        Args:
            direction (Direction | None):
                The movement direction provided by the active transformer.
                None indicates no movement input for this tick.

        Responsibilities typically include:
            - Updating player position
            - Advancing game objects
            - Handling collisions
            - Updating scores
            - Triggering sound effects
        """
        pass

    @abstractmethod
    def render(self) -> np.ndarray:
        """
        Render the current game state.

        Returns:
            np.ndarray:
                A frame representing the current visual state of the game.
                This frame will be displayed in the UI.
        """
        pass

    @abstractmethod
    def get_config_schema(self) -> dict:
        """
        Return a configuration schema for the game.

        The UI uses this schema to dynamically generate configuration
        controls (e.g., sliders, dropdowns).
        The key of each parameter will be passed to the __init__ function of the subclasses, so
        those keys should match the name of the parameters expected by the constructor.
        
        Example:
        
            .. code-block:: python
            
                {
                    "grid_w": {
                        # This will be shown in the label next to the editable widget
                        "name": "Grid width",
                        # Description showing the use of this parameter
                        "description": "Width of the maze",
                        # Default value for the parameter. An appropriated widget will be used depending on the type of this field.
                        "default": 24,
                        # Boundaries for numeric parameters
                        "min": 10,
                        "max": 100,
                    },
                }

        Returns:
            dict: A structured description of configurable parameters.
        """
        pass
    
    @abstractmethod
    def get_instructions(self) -> str:
        """
        Return instructions the UI should expose, as HTML formatted text.
        Include the `INSTRUCTIONS_HEAD` variable from the `neuroarcade.ui.instructions_html`
        to load the styles.

        The UI displays this information to explain:

            - Game objective
            - Controls
            - Scoring rules
            - Special mechanics

        Returns:
            str: Instructions for presentation in the UI.
        """
        pass