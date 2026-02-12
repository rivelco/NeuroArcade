import random
import time
import numpy as np
import cv2

from neuroarcade.core.direction import Direction
from neuroarcade.games.base import BaseGame


class MemoryPath(BaseGame):
    def __init__(self, grid_w=24, grid_h=18, cell=25, path_length=8, show_time=0.6, pause_time=0.25):
        super().__init__()

        self.grid_w = grid_w
        self.grid_h = grid_h
        self.cell = cell

        self.path_length = path_length
        self.show_time = show_time
        self.pause_time = pause_time

        self.reset()

    # -------------------------------------------------
    # BaseGame API
    # -------------------------------------------------
    def reset(self):
        self.player = self._random_pos()

        self.path = self._generate_path(self.path_length)
        self.user_path = [self.player]

        self.state = "showing"  # showing | playing | win | lose
        self.show_index = 0
        self.last_show_switch = time.time()
        self.flash_on = True

        self.steps = 0

    def update(self, direction: Direction | None):
        if not self.is_running():
            return

        now = time.time()

        if self.state == "showing":
            self._update_showing(now)
            return

        if self.state != "playing":
            return

        # ----------------- movement -----------------
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

            new_pos = (x, y)

            if new_pos != self.player:
                self.player = new_pos
                self.user_path.append(new_pos)
                self.steps += 1

                self._check_progress()

    def render(self) -> np.ndarray:
        img = np.zeros(
            (self.grid_h * self.cell, self.grid_w * self.cell, 3),
            dtype=np.uint8
        )

        # Draw user path trail
        for (x, y) in self.user_path:
            cv2.rectangle(
                img,
                (x * self.cell, y * self.cell),
                ((x + 1) * self.cell, (y + 1) * self.cell),
                (80, 80, 80),
                -1,
            )

        # Draw player
        px, py = self.player
        cv2.rectangle(
            img,
            (px * self.cell, py * self.cell),
            ((px + 1) * self.cell, (py + 1) * self.cell),
            (0, 255, 0),
            -1,
        )

        # Show the memory sequence (flashing cells)
        if self.state == "showing" and self.flash_on:
            x, y = self.path[self.show_index]
            cv2.rectangle(
                img,
                (x * self.cell, y * self.cell),
                ((x + 1) * self.cell, (y + 1) * self.cell),
                (0, 0, 255),
                -1,
            )

        self._draw_stats(img)
        return img

    def get_config_schema(self) -> dict:
        return {
            "grid_w": {
                "name": "Grid width",
                "description": "Width of the grid",
                "min": 10,
                "max": 100,
                "default": 24,
            },
            "grid_h": {
                "name": "Grid height",
                "description": "Height of the grid",
                "min": 10,
                "max": 100,
                "default": 18,
            },
            "cell": {
                "name": "Cell size",
                "description": "Pixel size of each grid cell",
                "min": 15,
                "max": 40,
                "default": 25,
            },
            "path_length": {
                "name": "Path length",
                "description": "Path length",
                "min": 3,
                "max": 25,
                "default": 8,
            },
            "show_time": {
                "name": "Flash time (s)",
                "description": "Number of seconds each square is on screen while showing",
                "min": 0.2,
                "max": 10.0,
                "default": 0.6,
            },
            "pause_time": {
                "name": "Pause between flashes (s)",
                "description": "Number of seconds between each square display",
                "min": 0.1,
                "max": 10.0,
                "default": 0.25,
            },
        }

    # Showing phase
    def _update_showing(self, now):
        if self.flash_on and now - self.last_show_switch > self.show_time:
            self.flash_on = False
            self.last_show_switch = now
        elif not self.flash_on and now - self.last_show_switch > self.pause_time:
            self.show_index += 1
            self.last_show_switch = now
            self.flash_on = True

            if self.show_index >= len(self.path):
                self.state = "playing"

    # Game logic
    def _check_progress(self):
        idx = len(self.user_path) - 1

        # If deviates from path then lose
        if idx >= len(self.path) or self.user_path[idx] != self.path[idx]:
            self.state = "lose"
            return

        # If completed correctly then win
        if idx == len(self.path) - 1:
            self.state = "win"

    def _generate_path(self, length):
        path = [self.player]
        idxs = []
        for _ in range(length - 1):
            x, y = path[-1]
            neighbors = [
                (x + 1, y),
                (x, y + 1),
                (x - 1, y),
                (x, y - 1),
            ]
            neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h]
            # Simple trick to avoid "back and forth" movements
            new_idx = random.choice(range(len(neighbors)))
            invalid = len(idxs) > 0
            while invalid:
                if new_idx % 2 == idxs[-1] % 2:
                    new_idx = random.choice(range(len(neighbors)))
                else:
                    invalid = False
            path.append(neighbors[new_idx])
            idxs.append(new_idx)
        return path

    def _random_pos(self):
        return (
            random.randint(0, self.grid_w - 1),
            random.randint(0, self.grid_h - 1),
        )

    # HUD
    def _draw_stats(self, img):
        corr = 0
        if self.state == 'lose':
            corr = 1
        text = f"Progress: {len(self.user_path)-corr}/{len(self.path)}   "
        if self.state in ['showing', 'playing'] and self.is_running():
            text += f"{self.state.upper()}"

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
        
        if self.state == 'win':
            cv2.putText(
                img, "YOU WIN",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 255, 0), 3, cv2.LINE_AA
            )
        elif self.state == 'lose':
            cv2.putText(
                img, "GAME OVER",
                (self.cell * 3, self.cell * 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 0, 255), 3, cv2.LINE_AA
            )
