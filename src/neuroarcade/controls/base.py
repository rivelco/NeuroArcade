from abc import ABC, abstractmethod
from neuroarcade.core.direction import Direction
import numpy as np

class BaseControl(ABC):
    @abstractmethod
    def update(self) -> tuple[Direction | None, np.ndarray | None]:
        """Return (direction, view_frame)"""
        pass