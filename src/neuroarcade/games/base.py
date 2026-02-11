from abc import ABC, abstractmethod
import numpy as np
from neuroarcade.core.direction import Direction

class BaseGame(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def update(self, direction: Direction | None):
        pass

    @abstractmethod
    def render(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_config_schema(self) -> dict:
        """Return parameters the UI should expose"""
        pass