import numpy as np
import cv2

from neuroarcade.controls.base import BaseControl
from neuroarcade.core.direction import Direction


class KeyboardControl(BaseControl):
    def __init__(self):
        self.last_direction = None
        self.size = 300

    # called by Qt
    def set_direction(self, direction: Direction | None):
        self.last_direction = direction

    def get_config_schema(self) -> dict:
        return {}

    def update(self):
        frame = self._render_keyboard()
        return self.last_direction, frame

    # ---------------------------------------------

    def _render_keyboard(self) -> np.ndarray:
        img = np.zeros((self.size, self.size, 3), dtype=np.uint8)

        center = self.size // 2
        offset = 60

        positions = {
            Direction.UP: (center, center - offset),
            Direction.DOWN: (center, center + offset),
            Direction.LEFT: (center - offset, center),
            Direction.RIGHT: (center + offset, center),
        }

        for direction, (x, y) in positions.items():
            color = (0, 200, 0) if direction == self.last_direction else (80, 80, 80)

            cv2.rectangle(img, (x-30, y-30), (x+30, y+30), color, -1)
            cv2.putText(img, direction.name, (x-28, y+8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1, cv2.LINE_AA)

        return img
