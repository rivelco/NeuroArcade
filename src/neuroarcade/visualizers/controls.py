import numpy as np
import cv2
from neuroarcade.controls.base import BaseControl
from neuroarcade.core.direction import Direction

class InputVisualization():
    def __init__(self, size=300, offset=60):
        """Visualization object to display the behavior of a controller or transform.
        
        Creates a frame depicting keyboard arrows that is updated with each change 
        in the controller or transformer.

        Args:
            size (int, optional): Size of the visualizer. Defaults to 300.
            offset (int, optional): Offset of the buttons with the text inside them. Defaults to 60.
        """
        self.size = size
        self.offset = offset
        self.img = np.zeros((size, size, 3), dtype=np.uint8)
        self.center = size // 2
        self.last_direction = None

        self.positions = {
            Direction.UP: (self.center, self.center - self.offset),
            Direction.DOWN: (self.center, self.center + self.offset),
            Direction.LEFT: (self.center - self.offset, self.center),
            Direction.RIGHT: (self.center + self.offset, self.center),
        }

    def update(self, new_direction: Direction) -> np.ndarray:
        """Function called every game tick to update the visualization
        based in the response of the controller or the transform.

        Args:
            new_direction (Direction): Direction received, to be highlighted.

        Returns:
            np.ndarray: New frame showing the updated visualization.
        """
        for direction, (x, y) in self.positions.items():
            color = (0, 200, 0) if direction == new_direction else (80, 80, 80)
            half_off = self.offset//2
            cv2.rectangle(self.img, (x-half_off, y-half_off), (x+half_off, y+half_off), color, -1)
            cv2.putText(self.img, direction.name, (x-half_off+2, y+half_off//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                        (255, 255, 255), 1, cv2.LINE_AA)
        return self.img