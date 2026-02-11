# Standard
import sys
import time
import argparse
import importlib.metadata
from importlib.resources import files
import qdarktheme
import cv2

# Qt
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget
)
from PyQt6.QtCore import QTimer, Qt, QEvent
from PyQt6.QtGui import QImage, QPixmap

# NeuroArcade core
from neuroarcade.core.direction import Direction
from neuroarcade.controls.KeyboardControl import KeyboardControl
from neuroarcade.utils.loader import discover_classes
from neuroarcade.ui.configurator import update_box_options, read_config
from neuroarcade.visualizers.controls import InputVisualization


# Utility OpenCV image to Qt scaled image
def set_cv_image(label, img):
    if img is None:
        label.clear()
        return

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape

    qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    pix = QPixmap.fromImage(qimg)

    # Scale to label size, keep aspect ratio
    scaled = pix.scaled(
        label.size(),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    label.setPixmap(scaled)
    
# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = str(files("neuroarcade.ui").joinpath("MainWindow.ui"))
        loadUi(ui_path, self)
        self.setWindowTitle('NeuroArcade')
        
        # ---- Discover elements ----
        self.games = discover_classes("neuroarcade.games")
        self.controls = discover_classes("neuroarcade.controls")
        self.transforms = discover_classes("neuroarcade.transforms")
        
        if len(self.games) == 0:
            raise RuntimeError("No games available. Check the file of the game and game class match.")
        if len(self.controls) == 0:
            raise RuntimeError("No controls available. Check the file of the control and control class match.")
        if len(self.transforms) == 0:
            raise RuntimeError("No transforms available. Check the file of the transform and transform class match.")

        # ---- Show the available elements in the comboboxes ----
        self.game_selector_combo.addItems(list(self.games.keys()))
        self.control_selector_combo.addItems(list(self.controls.keys()))
        self.transformer_selector_combo.addItems(list(self.transforms.keys()))
        
        # ---- Engine components ----
        self.current_game = ""
        self.current_control = ""
        self.current_transform = ""
        
        initial_game = list(self.games.keys())[0]
        initial_control = list(self.controls.keys())[0]
        initial_transform = list(self.transforms.keys())[0]
        
        self.change_selected_game(initial_game)
        self.change_selected_control(initial_control)
        self.change_selected_transform(initial_transform)
        
        # Visualization components
        self.user_input_vis = InputVisualization(size=120, offset=35)
        self.trans_output_vis = InputVisualization(size=120, offset=35)
        
        # ---- UI widgets ----
        self.game_speed_slider.setRange(50, 300)
        self.game_speed_slider.setValue(120)

        self.global_timer.setRange(10, 600)
        self.global_timer.setValue(30)

        # ---- Timing ----
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(self.global_timer.value())

        self.last_tick = time.time()

        # ---- Signals ----
        self.start_game_button.clicked.connect(self.start_game)
        self.reset_game_button.clicked.connect(self.reset_game)
        
        self.game_selector_combo.currentTextChanged.connect(self.change_selected_game)
        self.control_selector_combo.currentTextChanged.connect(self.change_selected_control)
        self.transformer_selector_combo.currentTextChanged.connect(self.change_selected_transform)

    # --------------------------------------------------

    def start_game(self):
        self.game.start()

    def reset_game(self):
        self.change_selected_game(self.current_game)
    
    def change_selected_game(self, game_name):
        configs = self.games[game_name].get_config_schema(self.games[game_name])
        if self.current_game != game_name:
            update_box_options(configs, self.game_parameters_box)
            self.current_game = game_name
        params = read_config(self.game_parameters_box)
        self.game = self.games[game_name](**params)
        
    def change_selected_control(self, control_name):
        configs = self.controls[control_name].get_config_schema(self.controls[control_name])
        if self.current_control != control_name:
            update_box_options(configs, self.control_parameters_box)
            self.current_control = control_name
        params = read_config(self.control_parameters_box)
        self.control = self.controls[control_name](**params)
        
    def change_selected_transform(self, transform_name):
        configs = self.transforms[transform_name].get_config_schema(self.transforms[transform_name])
        if self.current_control != transform_name:
            update_box_options(configs, self.transform_parameters_box)
            self.current_transform = transform_name
        params = read_config(self.transform_parameters_box)
        self.transform = self.transforms[transform_name](**params)

    # --------------------------------------------------

    def loop(self):
        # Get control input
        direction, cam_frame = self.control.update()
        
        # Update the user input visualization
        user_input_frame = self.user_input_vis.update(direction)
        
        # Transform control paradigm
        direction = self.transform.apply(direction)
        
        # Update the transform output visualization
        trans_output_frame = self.trans_output_vis.update(direction)

        # Update game on its own clock
        speed = self.game_speed_slider.value() / 1000.0
        if time.time() - self.last_tick > speed:
            self.game.update(direction)
            self.last_tick = time.time()

        # Render game
        game_frame = self.game.render()

        # Show everything
        set_cv_image(self.game_feed_lbl, game_frame)
        set_cv_image(self.control_feed_lbl, cam_frame)
        set_cv_image(self.user_input_visualization_lbl, user_input_frame)
        set_cv_image(self.transform_output_visualization_lbl, trans_output_frame)
        
    # ---- Helpers to detect key events for Keyboard control ----
    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride:
            self.key_here(event)
            return False
        return QWidget.event(self, event)
    
    def key_here(self, event):#keyPressEvent(self, event):
        # Handle reset and start keys
        if event.key() == Qt.Key.Key_Escape:
            self.reset_game()
        if event.key() == Qt.Key.Key_Space:
            self.start_game()
            
        # Special case for the KeyboardControl
        if isinstance(self.control, KeyboardControl):
            if event.key() == Qt.Key.Key_Up:
                self.control.set_direction(Direction.UP)
            elif event.key() == Qt.Key.Key_Down:
                self.control.set_direction(Direction.DOWN)
            elif event.key() == Qt.Key.Key_Left:
                self.control.set_direction(Direction.LEFT)
            elif event.key() == Qt.Key.Key_Right:
                self.control.set_direction(Direction.RIGHT)
            
    def keyReleaseEvent(self, event):
        if not isinstance(self.control, KeyboardControl):
            return
        self.control.set_direction(None)

# Entry point
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()

    if args.version:
        print(importlib.metadata.version("neuroarcade"))
        return

    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
