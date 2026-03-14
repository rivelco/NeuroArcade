from abc import ABC, abstractmethod
from neuroarcade.core.direction import Direction

class BaseTransform(ABC):
    """
    A transform remaps a canonical Direction into another Direction.

    This is the core of the visuomotor remapping logic.
    """

    @abstractmethod
    def apply(self, direction: Direction) -> Direction:
        """Return the remapped direction. This is like "the controller says left
        but I say right".

        Args:
            direction (Direction): Direction passed by the controller.

        Returns:
            Direction: Direction returned by the transformer, may be different.
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> dict:
        """
        Return a configuration schema for the transformer.

        The UI uses this schema to dynamically generate configuration controls 
        (e.g., sliders, dropdowns).
        The key of each parameter will be passed to the __init__ function of the subclasses, so
        those keys should match the name of the parameters expected by the constructor.
        
        Returns:
            dict: A structured description of configurable parameters.
        """
        pass
    
    @abstractmethod
    def get_instructions(self) -> dict:
        """
        Return instructions the UI should expose, as HTML formatted text.
        Include the `INSTRUCTIONS_HEAD` variable from the `neuroarcade.ui.instructions_html`
        to load the styles.

        The UI displays this information to explain:

            - Transform logic
            - Controls equivalencies

        Returns:
            str: Instructions for presentation in the UI.
        """
        pass