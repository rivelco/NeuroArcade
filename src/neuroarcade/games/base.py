from abc import ABC, abstractmethod
import numpy as np
from importlib.resources import files
from neuroarcade.core.direction import Direction
from neuroarcade.core.SoundManager import SoundManager

class BaseGame(ABC):
    def __init__(self):
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def is_running(self) -> bool:
        return self._running
    
    def initialize_sounds(self, volume=0.4):
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