from abc import ABC, abstractmethod
from neuroarcade.core.direction import Direction

class BaseTransform(ABC):
    """
    A transform remaps a canonical Direction into another Direction.

    This is the core of the visuomotor remapping logic.
    """

    @abstractmethod
    def apply(self, direction: Direction) -> Direction:
        """Return the remapped direction"""
        raise NotImplementedError
    
    @abstractmethod
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        pass
    
    @abstractmethod
    def get_instructions(self) -> dict:
        """Return instructions the UI should expose"""
        pass