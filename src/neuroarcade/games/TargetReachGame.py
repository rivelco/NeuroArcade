import random
import time
import numpy as np
import cv2

from neuroarcade.games.base import BaseGame
from neuroarcade.core.direction import Direction


class TargetReachGame(BaseGame):
    """
    Simple familiarization game:
    Move from a random start position to a random target.
    Measures time and steps taken.
    """

    def __init__(self, grid_w=20, grid_h=15, cell=30):
        super().__init__()
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.cell = cell
        self.reset()

    # --------------------------------------------------

    def reset(self):
        self.player = self._random_pos()
        self.target = self._random_pos(exclude=self.player)

        self.steps = 0
        self.start_time = None
        self.end_time = None

    # --------------------------------------------------

    def start(self):
        super().start()
        self.start_time = time.time()
        self.end_time = None

    # --------------------------------------------------

    def update(self, direction: Direction | None):
        if not self.is_running() or direction is None:
            return

        x, y = self.player

        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1

        # keep inside bounds
        x = max(0, min(self.grid_w - 1, x))
        y = max(0, min(self.grid_h - 1, y))

        new_pos = (x, y)

        if new_pos != self.player:
            self.player = new_pos
            self.steps += 1

        # Check win condition
        if self.player == self.target:
            self.end_time = time.time()
            self.stop()

    # --------------------------------------------------

    def render(self) -> np.ndarray:
        img = np.zeros(
            (self.grid_h * self.cell, self.grid_w * self.cell, 3),
            dtype=np.uint8
        )

        # draw grid
        for i in range(self.grid_w + 1):
            cv2.line(
                img,
                (i * self.cell, 0),
                (i * self.cell, self.grid_h * self.cell),
                (40, 40, 40),
                1
            )
        for j in range(self.grid_h + 1):
            cv2.line(
                img,
                (0, j * self.cell),
                (self.grid_w * self.cell, j * self.cell),
                (40, 40, 40),
                1
            )

        # draw target
        tx, ty = self.target
        cv2.rectangle(
            img,
            (tx * self.cell, ty * self.cell),
            ((tx + 1) * self.cell, (ty + 1) * self.cell),
            (0, 0, 255),
            -1
        )

        # draw player
        px, py = self.player
        cv2.rectangle(
            img,
            (px * self.cell, py * self.cell),
            ((px + 1) * self.cell, (py + 1) * self.cell),
            (0, 255, 0),
            -1
        )

        # draw stats
        if self.start_time:
            elapsed = (
                (self.end_time or time.time()) - self.start_time
            )
            text = f"Steps: {self.steps}   Time: {elapsed:0.2f}s"
            cv2.putText(
                img, text, (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2, cv2.LINE_AA
            )
            
        # --- Game over message
        if not self.is_running() and self.end_time is not None:
            cv2.putText(
                img, "YOU WIN",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 0, 255), 3, cv2.LINE_AA
            )

        return img

    # --------------------------------------------------

    def _random_pos(self, exclude=None):
        while True:
            pos = (
                random.randint(0, self.grid_w - 1),
                random.randint(0, self.grid_h - 1),
            )
            if pos != exclude:
                return pos

    # --------------------------------------------------

    def get_config_schema(self) -> dict:
        return {
            "grid_w": {
                "name": "Grid width",
                "min": 5,
                "max": 50,
                "default": 20,
                "description": "Number of cells horizontally"
            },
            "grid_h": {
                "name": "Grid height",
                "min": 5,
                "max": 50,
                "default": 15,
                "description": "Number of cells vertically"
            },
            "cell": {
                "name": "Cell size",
                "min": 10,
                "max": 60,
                "default": 30,
                "description": "Pixel size of each grid cell"
            },
        }
