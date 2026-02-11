import random
import numpy as np
import cv2

from neuroarcade.games.base import BaseGame
from neuroarcade.core.direction import Direction

class SnakeGame(BaseGame):
    def __init__(self, grid_w=32, grid_h=24, cell=20):
        self.cell = cell
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.reset()

    # ---------------- BaseGame API ----------------
    def reset(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = Direction.RIGHT
        self.food = self._random_food()
        self.score = 0
        self.game_over = False

    def update(self, new_direction: Direction | None):
        if self.game_over:
            return

        # Prevent 180 reversal
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        if new_direction and new_direction != opposite[self.direction]:
            self.direction = new_direction

        x, y = self.snake[0]

        if self.direction == Direction.UP:
            y -= 1
        elif self.direction == Direction.DOWN:
            y += 1
        elif self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.RIGHT:
            x += 1

        new_head = (x, y)

        # Collision
        if (
            x < 0 or x >= self.grid_w or
            y < 0 or y >= self.grid_h or
            new_head in self.snake
        ):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self._random_food()
        else:
            self.snake.pop()

    def render(self) -> np.ndarray:
        img = np.zeros(
            (self.grid_h * self.cell, self.grid_w * self.cell, 3),
            dtype=np.uint8
        )

        # Snake
        for x, y in self.snake:
            cv2.rectangle(
                img,
                (x * self.cell, y * self.cell),
                ((x + 1) * self.cell, (y + 1) * self.cell),
                (0, 255, 0),
                -1
            )

        # Food
        fx, fy = self.food
        cv2.rectangle(
            img,
            (fx * self.cell, fy * self.cell),
            ((fx + 1) * self.cell, (fy + 1) * self.cell),
            (0, 0, 255),
            -1
        )

        return img

    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {
            "grid_w": {"type": "int", "min": 10, "max": 60, "default": 32},
            "grid_h": {"type": "int", "min": 10, "max": 60, "default": 24},
            "cell": {"type": "int", "min": 10, "max": 40, "default": 20},
        }

    # ---------------- Internal helpers ----------------

    def _random_food(self):
        return (
            random.randint(0, self.grid_w - 1),
            random.randint(0, self.grid_h - 1)
        )
