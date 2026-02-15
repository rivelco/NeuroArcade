import random
import numpy as np
import cv2
import time

from neuroarcade.games.base import BaseGame
from neuroarcade.core.direction import Direction
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

class SnakeGame(BaseGame):
    def __init__(self, grid_w=32, grid_h=24, cell=20):
        super().__init__()
        self.cell = cell
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.reset()

    # ---------------- BaseGame API ---------------- 
    def start(self):
        super().start()
        self.start_time = time.time()
        self.end_time = None

    def reset(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = Direction.RIGHT
        self.food = self._random_food()
        self.score = 0

        self.start_time = None
        self.end_time = None

    def update(self, new_direction: Direction | None):
        if not self.is_running():
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
            self.end_time = time.time()
            self.stop()  # Game over
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

        # grid
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

        # HUD stats
        if self.start_time:
            elapsed = (self.end_time or time.time()) - self.start_time
            hud = f"Score: {self.score}   Time: {elapsed:0.2f}s"
            cv2.putText(
                img, hud, (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2, cv2.LINE_AA
            )

        # Game over message
        if not self.is_running() and self.end_time is not None:
            cv2.putText(
                img, "GAME OVER",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 0, 255), 3, cv2.LINE_AA
            )

        return img

    # ---------------- Internal helpers ----------------

    def _random_food(self):
        return (
            random.randint(0, self.grid_w - 1),
            random.randint(0, self.grid_h - 1)
        )

    # -------------------------------------------------
    
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {
            "grid_w": {
                "name": "Grid width",
                "description": "Grid width", 
                "min": 10, 
                "max": 100, 
                "default": 32
                },
            "grid_h": {
                "name": "Grid height",
                "description": "Grid height", 
                "min": 10, 
                "max": 100, 
                "default": 24
                },
            "cell": {
                "name": "Cell", 
                "description": "Cell size in pixels", 
                "min": 10, 
                "max": 40, 
                "default": 20
                },
        }
        
    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>

            <h1>Snake</h1>

            <div class="section">
                <p>
                    Classic snake game. Move the snake across the field to eat the red targets and grow.
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>You're the green snake moving across the field and has to reach each red target.</li>
                    <li>Collect as many targets as possible without colliding with a wall.</li>
                </ul>
            </div>

            <h2>Winning</h2>
            <p>
                You're winning all the time because you're eating as much as you can so <span class="highlight">win as long as you can.</span>.
            </p>

            <h2>Losing</h2>
            <p class="warning">
                If you collide with the bounds of the field, you lose.
            </p>

        </body>
        </html>
        """