import random
import time
import numpy as np
import cv2

from neuroarcade.core.direction import Direction
from neuroarcade.games.base import BaseGame
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD


class ReactionTarget(BaseGame):
    def __init__(self, grid_w=24, grid_h=18, cell=25, target_timeout=10.0, target_hits=10, death_misses=10):
        super().__init__()

        self.grid_w = grid_w
        self.grid_h = grid_h
        self.cell = cell
        self.target_timeout = target_timeout
        self.target_hits = target_hits
        self.death_misses = death_misses
        
        self.initialize_sounds()

        self.reset()

    # BaseGame API
    def reset(self):
        self.player = self._random_pos()
        self.target = None

        self.steps = 0
        self.hits = 0
        self.misses = 0
        self.remaining = 0.0

        self.target_spawn_time = None
        self.target_deadline = None

    def update(self, direction: Direction | None):
        if not self.is_running():
            return

        now = time.time()

        # Spawn first or next target
        if self.target is None:
            self.sounds.play("click")
            self._spawn_target(now)

        # Move player
        if direction is not None:
            x, y = self.player

            if direction == Direction.UP:
                y -= 1
            elif direction == Direction.DOWN:
                y += 1
            elif direction == Direction.LEFT:
                x -= 1
            elif direction == Direction.RIGHT:
                x += 1

            x = max(0, min(self.grid_w - 1, x))
            y = max(0, min(self.grid_h - 1, y))

            self.player = (x, y)
            self.steps += 1

        # Check hit
        if self.player == self.target:
            self.sounds.play("eat")
            self.hits += 1
            if self.hits == self.target_hits:
                self.sounds.play("win")
                self.stop()
            self._spawn_target(now)
            self.sounds.play("click")
            return

        # Check timeout (miss)
        if now > self.target_deadline:
            self.misses += 1
            self.sounds.play("miss")
            if self.misses == self.death_misses:
                self.sounds.play("fail")
                self.stop()
            self._spawn_target(now)

    def render(self) -> np.ndarray:
        img = np.zeros(
            (self.grid_h * self.cell, self.grid_w * self.cell, 3),
            dtype=np.uint8
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

        # Target
        if self.target is not None:
            tx, ty = self.target
            cv2.rectangle(
                img,
                (tx * self.cell, ty * self.cell),
                ((tx + 1) * self.cell, (ty + 1) * self.cell),
                (0, 0, 255),
                -1
            )
            
        self._draw_stats(img)

        # Game over message
        if not self.is_running() and self.hits == self.target_hits:
            cv2.putText(
                img, "YOU WIN",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 255, 0), 3, cv2.LINE_AA
            )
        
        if not self.is_running() and self.misses == self.death_misses:
            cv2.putText(
                img, "GAME OVER",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 0, 255), 3, cv2.LINE_AA
            )

        return img

    # Internal logic
    def _spawn_target(self, now):
        self.target = self._random_pos()
        self.target_spawn_time = now
        self.target_deadline = now + self.target_timeout

    def _random_pos(self):
        return (
            random.randint(0, self.grid_w - 1),
            random.randint(0, self.grid_h - 1),
        )

    # HUD
    def _draw_stats(self, img):
        if self.is_running():
            self.remaining = 0.0
            if self.target_deadline:
                self.remaining = max(0.0, self.target_deadline - time.time())

        text = (
            f"Steps: {self.steps}   "
            f"Hits: {self.hits}   "
            f"Misses: {self.misses}   "
            f"Time left: {self.remaining:4.2f}s"
        )

        #cv2.rectangle(img, (0, 0), (img.shape[1], 40), (30, 30, 30), -1)
        cv2.putText(
            img,
            text,
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    # -------------------------------------------------
    
    def get_config_schema(self) -> dict:
        return {
            "grid_w": {
                "name": "Grid width",
                "min": 10,
                "max": 100,
                "default": 24,
                "description": "Width of the grid",
            },
            "grid_h": {
                "name": "Grid height",
                "min": 10,
                "max": 100,
                "default": 18,
                "description": "Height of the grid",
            },
            "cell": {
                "name": "Cell size",
                "min": 15,
                "max": 40,
                "default": 25,
                "description": "Pixel size of each grid cell",
            },
            "target_timeout": {
                "name": "Target timeout (s)",
                "min": 0.5,
                "max": 600.0,
                "default": 10.0,
                "description": "How long the target stays before disappearing",
            },
            "target_hits": {
                "name": "Hits to win",
                "min": 1,
                "max": 1000,
                "default": 10,
                "description": "How many hits are needed to win",
            },
            "death_misses": {
                "name": "Misses to lose",
                "min": 1,
                "max": 1000,
                "default": 10,
                "description": "How many misses are needed to lose",
            },
        }
        
    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>

            <h1>Reaction Target</h1>

            <div class="section">
                <p>
                    A red target appears at a random position. Go to that position before the time finishes.
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>A red target appears at a random position.</li>
                    <li>You must reach that target before the time ends.</li>
                    <li>If you don't reach the target in time the target will move to a different location and will be marked as a miss.</li>
                </ul>
            </div>

            <h2>Winning</h2>
            <p>
                If you make the specified number of hits, you <span class="highlight">win</span>.
            </p>

            <h2>Losing</h2>
            <p class="warning">
                If you fail to reach the target in time the specified number of times, you lose.
            </p>

        </body>
        </html>
        """