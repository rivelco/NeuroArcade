import random
import time
import numpy as np
import cv2

from neuroarcade.core.direction import Direction
from neuroarcade.games.base import BaseGame


class MazeRunner(BaseGame):
    def __init__(self, grid_w=24, grid_h=18, cell=25, wall_density=0.18):
        super().__init__()

        self.grid_w = grid_w
        self.grid_h = grid_h
        self.cell = cell
        self.wall_density = wall_density

        self.reset()

    # -------------------------------------------------
    # BaseGame API
    # -------------------------------------------------
    def reset(self):
        self.maze = self._generate_maze()
        self.player = self._random_empty()
        self.goal = self._random_empty()

        self.start_time = None
        self.end_time = None
        self.steps = 0
        self.path = [self.player]

    def update(self, direction: Direction | None):
        if not self.is_running():
            return

        if self.start_time is None:
            self.start_time = time.time()
            self.end_time = None

        if direction is None:
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

        if self._is_free(x, y):
            self.player = (x, y)
            self.steps += 1
            self.path.append(self.player)

        if self.player == self.goal:
            self.end_time = time.time()
            self.stop()

    def render(self) -> np.ndarray:
        img = np.zeros(
            (self.grid_h * self.cell, self.grid_w * self.cell, 3),
            dtype=np.uint8
        )

        # Draw walls
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if self.maze[y, x] == 1:
                    cv2.rectangle(
                        img,
                        (x * self.cell, y * self.cell),
                        ((x + 1) * self.cell, (y + 1) * self.cell),
                        (70, 70, 70),
                        -1
                    )

        # Goal
        gx, gy = self.goal
        cv2.rectangle(
            img,
            (gx * self.cell, gy * self.cell),
            ((gx + 1) * self.cell, (gy + 1) * self.cell),
            (0, 0, 255),
            -1
        )

        # Player
        px, py = self.player
        cv2.rectangle(
            img,
            (px * self.cell, py * self.cell),
            ((px + 1) * self.cell, (py + 1) * self.cell),
            (0, 255, 0),
            -1
        )

        # HUD stats
        if self.start_time:
            self._draw_stats(img)
        
        # Game over message
        if not self.is_running() and self.end_time is not None:
            cv2.putText(
                img, "YOU WIN",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 255, 0), 3, cv2.LINE_AA
            )

        return img

    def get_config_schema(self) -> dict:
        return {
            "grid_w": {
                "name": "Grid width",
                "min": 10,
                "max": 100,
                "default": 24,
                "description": "Width of the maze",
            },
            "grid_h": {
                "name": "Grid height",
                "min": 10,
                "max": 100,
                "default": 18,
                "description": "Height of the maze",
            },
            "cell": {
                "name": "Cell size",
                "min": 15,
                "max": 40,
                "default": 25,
                "description": "Pixel size of each grid cell",
            },
            "wall_density": {
                "name": "Wall density",
                "min": 0.05,
                "max": 0.95,
                "default": 0.30,
                "description": "How cluttered the maze is",
            },
        }

    # Maze logic
    def _generate_maze(self):
        maze = np.zeros((self.grid_h, self.grid_w), dtype=np.uint8)

        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if random.random() < self.wall_density:
                    maze[y, x] = 1

        return maze

    def _random_empty(self):
        while True:
            x = random.randint(0, self.grid_w - 1)
            y = random.randint(0, self.grid_h - 1)
            if self._is_free(x, y):
                return (x, y)

    def _is_free(self, x, y):
        if x < 0 or x >= self.grid_w or y < 0 or y >= self.grid_h:
            return False
        return self.maze[y, x] == 0

    # Stats overlay
    def _draw_stats(self, img):
        elapsed = 0
        if self.start_time:
            elapsed = (self.end_time or time.time()) - self.start_time

        text = f"Time: {elapsed:5.2f}s   Steps: {self.steps}"

        #cv2.rectangle(img, (0, 0), (img.shape[1], 40), (30, 30, 30), -1)
        cv2.putText(
            img,
            text,
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
