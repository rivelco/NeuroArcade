from abc import ABC, abstractmethod
import numpy as np
from importlib.resources import files
from neuroarcade.core.direction import Direction

class BaseGame(ABC):
    def __init__(self):
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def is_running(self) -> bool:
        return self._running
    
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
    
    @abstractmethod
    def get_instructions(self) -> dict:
        """Return instructions the UI should expose"""
        pass