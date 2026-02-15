from abc import ABC, abstractmethod
from neuroarcade.core.direction import Direction
import numpy as np

class BaseControl(ABC):
    @abstractmethod
    def update(self) -> tuple[Direction | None, np.ndarray | None]:
        """Return (direction, view_frame)"""
        pass
    
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