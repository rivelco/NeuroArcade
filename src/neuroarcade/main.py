# Standard
import sys
import time
import argparse
import importlib.metadata
from importlib.resources import files

import cv2

# Qt
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QSlider, QSpinBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

# NeuroArcade core
from neuroarcade.core.direction import Direction
from neuroarcade.controls.QrTrack import QRTracker
from neuroarcade.transforms.Identity import IdentityTransform
from neuroarcade.games.SnakeGame import SnakeGame


# Utility OpenCV image to Qt
def cv_to_qt(img):
    if img is None:
        return QPixmap()

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg)

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = str(files("neuroarcade.ui").joinpath("MainWindow.ui"))
        loadUi(ui_path, self)
        self.setWindowTitle('NeuroArcade')
        self.control = QRTracker()
        self.transform = IdentityTransform()

        # ---- UI widgets ----
        self.game_label = QLabel()
        self.cam_label = QLabel()

        self.start_btn = QPushButton("Start")
        self.reset_btn = QPushButton("Reset")

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(120)

        self.grid_spin = QSpinBox()
        self.grid_spin.setRange(10, 60)
        self.grid_spin.setValue(32)

        self._layout()

        # ---- Timing ----
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(30)

        self.last_tick = time.time()

        # ---- Signals ----
        self.start_btn.clicked.connect(self.start_game)
        self.reset_btn.clicked.connect(self.reset_game)

    # --------------------------------------------------

    def _layout(self):
        views = QHBoxLayout()
        views.addWidget(self.game_label)
        views.addWidget(self.cam_label)

        controls = QHBoxLayout()
        controls.addWidget(self.start_btn)
        controls.addWidget(self.reset_btn)
        controls.addWidget(QLabel("Speed"))
        controls.addWidget(self.speed_slider)
        controls.addWidget(QLabel("Grid"))
        controls.addWidget(self.grid_spin)

        main = QVBoxLayout()
        main.addLayout(views)
        main.addLayout(controls)
        self.setLayout(main)

    # --------------------------------------------------

    def start_game(self):
        self.game.start()

    def reset_game(self):
        self.game = SnakeGame(
            grid_w=self.grid_spin.value(),
            grid_h=24
        )

    # --------------------------------------------------

    def loop(self):
        # Get control input
        direction, cam_frame = self.control.update()

        # Transform control paradigm
        direction = self.transform.apply(direction)

        # Update game on its own clock
        speed = self.speed_slider.value() / 1000.0
        if time.time() - self.last_tick > speed:
            self.game.update(direction)
            self.last_tick = time.time()

        # Render game
        game_frame = self.game.render()

        # Show everything
        self.game_label.setPixmap(cv_to_qt(game_frame))
        self.cam_label.setPixmap(cv_to_qt(cam_frame))


# Entry point
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()

    if args.version:
        print(importlib.metadata.version("neuroarcade"))
        return

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
