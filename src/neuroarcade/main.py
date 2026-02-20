# Standard
import sys
import time
import argparse
import importlib.metadata
from importlib.resources import files
import importlib.metadata
import qdarktheme
import cv2
import numpy as np

# Qt
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget,
    QLabel, QPushButton
)
from PyQt6.QtCore import QTimer, Qt, QEvent, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon

# NeuroArcade core
from neuroarcade.core.direction import Direction
from neuroarcade.controls.KeyboardControl import KeyboardControl
from neuroarcade.utils.loader import discover_classes
from neuroarcade.ui.configurator import update_box_options, read_config
from neuroarcade.visualizers.controls import InputVisualization
from neuroarcade.ui.InstructionsWindow import InstructionsWindow
from neuroarcade.core.SoundManager import MusicManager


def set_cv_image(label: QLabel, img: np.ndarray):
    """Draw and scales a OpenCV image to a Qt label widget, so the image don't break
    the layout in PyQt.

    Args:
        label (QLabel): PyQt6 QLabel widget that'll contain the image
        img (np.ndarray): OpenCV image to show
    """
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
    """Main NeuroArcade window.

    Args:
        QMainWindow (QMainWindow): PyQt6 QMainWindow object.
    """
    def __init__(self):
        """Initializes the program, dynamically discover and load games, controls, transforms, sounds
        and links each button to the corresponding actions.

        Raises:
            RuntimeError: If no games are available
            RuntimeError: If no controls are available
            RuntimeError: If no transforms are available
        """
        super().__init__()
        # ---- Styling ----
        ui_path = str(files("neuroarcade.ui").joinpath("MainWindow.ui"))
        loadUi(ui_path, self)
        arcade_version = str(importlib.metadata.version("neuroarcade"))
        self.setWindowTitle(f'NeuroArcade v{arcade_version}')
        icon = str(files("neuroarcade.ui.icons").joinpath("NeuroArcade.ico"))
        self.setWindowIcon(QIcon(icon))
        self.switch_dark_mode()
        
        # ---- Discover and load elements ----
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
        initial_control = "KeyboardControl"
        self.control_selector_combo.setCurrentText(initial_control)
        initial_transform = list(self.transforms.keys())[0]
        
        self.change_selected_game(initial_game)
        self.change_selected_control(initial_control)
        self.change_selected_transform(initial_transform)
        
        # ---- Visualization components for controls and transforms ----
        self.user_input_vis = InputVisualization(size=120, offset=35)
        self.trans_output_vis = InputVisualization(size=120, offset=35)
        
        # ---- Speed controllers ----
        self.game_speed_slider.setRange(1, 300)
        self.game_speed_slider.setValue(120)
        self.game_speed_slider.setToolTip("Lower values decreases game speed.")
        
        # ---- Timing for the game loop ----
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(30)    # The loop repeats every 30ms
        self.last_tick = time.time()
        
        # ---- Sounds ----
        self.initialize_music()
        self.music_selector_combo.currentTextChanged.connect(self.change_music)
        self.music_volume_slider.valueChanged.connect(self.change_music_volume)
        self.music_volume_slider.setValue(40)
        self.change_music_volume(40)

        # ---- Signals ----
        self.start_game_button.clicked.connect(self.start_game)
        self.reset_game_button.clicked.connect(self.reset_game)
        
        self.game_selector_combo.currentTextChanged.connect(self.change_selected_game)
        self.control_selector_combo.currentTextChanged.connect(self.change_selected_control)
        self.transformer_selector_combo.currentTextChanged.connect(self.change_selected_transform)
        self.dark_check.stateChanged.connect(self.switch_dark_mode)
        
        # ---- Signals for instruction windows ----
        self.control_instructions_button.clicked.connect(self.show_control_instructions)
        self.transform_instructions_button.clicked.connect(self.show_transform_instructions)
        self.game_instructions_button.clicked.connect(self.show_game_instructions)

    # --------------------------------------------------

    def start_game(self):
        """Starts the currently selected game. If one is running then nothing happens.
        """
        self.game.start()

    def reset_game(self):
        """Reloads the current game, like starting all over. 
        Also, applies any changes to the game parameters.
        """
        self.change_selected_game(self.current_game)
        
    def reset_control(self):
        """Reloads the selected control and applies the current parameters.
        """
        self.change_selected_control(self.current_control)
    
    def reset_transform(self):
        """Reloads the selected transform and applies the current parameters.
        """
        self.change_selected_control(self.current_control)
    
    def change_selected_game(self, game_name: str):
        """Changes the selected game as triggered by `self.game_selector_combo`

        Args:
            game_name (str): Name of the game to load. This name must match with
                the name of the file and the class of the game.
        """
        configs = self.games[game_name].get_config_schema(self.games[game_name])
        if self.current_game != game_name:
            # If the selected game is a different game then the parameters box is updated
            update_box_options(configs, self.game_parameters_box)
            self.current_game = game_name
        params = read_config(self.game_parameters_box)
        self.game = self.games[game_name](**params)
        
    def change_selected_control(self, control_name: str):
        """Changes the selected control as triggered by `self.control_selector_combo`.

        Args:
            control_name (str): Name of the control, must match the name of the file
                and class name of the control.
        """
        configs = self.controls[control_name].get_config_schema(self.controls[control_name])
        if self.current_control != control_name:
            # If the selected control is different from current then the parameters box is updated
            update_box_options(configs, self.control_parameters_box, set_function=self.reset_control)
            self.current_control = control_name
        params = read_config(self.control_parameters_box)
        self.control = self.controls[control_name](**params)
        
    def change_selected_transform(self, transform_name: str):
        """Changes the selected transform as triggered by `self.transformer_selector_combo`.

        Args:
            transform_name (str): Name of the transformer, must match the name of the file
                and class name of the transformer.
        """
        configs = self.transforms[transform_name].get_config_schema(self.transforms[transform_name])
        if self.current_control != transform_name:
            # If the selected transform is different from current then the parameters box is updated
            update_box_options(configs, self.transform_parameters_box, set_function=self.reset_transform)
            self.current_transform = transform_name
        params = read_config(self.transform_parameters_box)
        self.transform = self.transforms[transform_name](**params)
        
    # --------------------------------------------------
    
    def show_game_instructions(self):
        """Opens a new window showing the instructions of the current game.
        """
        html = self.games[self.current_game].get_instructions(self.games[self.current_game])
        dialog = InstructionsWindow(html, self)
        dialog.exec()
    
    def show_transform_instructions(self):
        """Opens a new window showing the instructions of the current transform.
        """
        html = self.transforms[self.current_transform].get_instructions(self.transforms[self.current_transform])
        dialog = InstructionsWindow(html, self)
        dialog.exec()
        
    def show_control_instructions(self):
        """Opens a new window showing the instructions of the current control.
        """
        html = self.controls[self.current_control].get_instructions(self.controls[self.current_control])
        dialog = InstructionsWindow(html, self)
        dialog.exec()

    # --------------------------------------------------

    def loop(self):
        """Main game loop. this function is repeated and controlled by the `self.timer`.
        Loads the controls, updates controls visualizations, transforms, updates the game
        accordingly and update all the visualizations.
        """
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
    def event(self, event: QEvent):
        """Event function triggered automatically by the PyQt6 logic every time 
        an event is detected. The idea is to intercept some events to identify
        the keyboard usage.

        Args:
            event (QEvent): Event detected by PyQt6.

        Returns:
            QEvent: Returns the same event.
        """
        if event.type() == QEvent.Type.ShortcutOverride:
            # Many keys are detected by PyQt6 as a ShortcutOverride
            self.key_here(event)
            return False
        return QWidget.event(self, event)
    
    def key_here(self, event: QEvent):
        """This function identify specific keyboard presses and runs different 
        functions accordingly, like resetting a game, or passing info to the
        keyboard controller.

        Args:
            event (QEvent): PyQt6 event related to a keyboard press.
        """
        # Handle reset and start keys
        if event.key() == Qt.Key.Key_Escape:
            self.reset_game()
        if event.key() == Qt.Key.Key_Space:
            if self.game.is_running():
                self.reset_game()
            else:
                self.start_game()
            
        # Special case for the KeyboardControl, only assigned
        # if the KeyboardControl is in use
        if isinstance(self.control, KeyboardControl):
            if event.key() == Qt.Key.Key_Up:
                self.control.set_direction(Direction.UP)
            elif event.key() == Qt.Key.Key_Down:
                self.control.set_direction(Direction.DOWN)
            elif event.key() == Qt.Key.Key_Left:
                self.control.set_direction(Direction.LEFT)
            elif event.key() == Qt.Key.Key_Right:
                self.control.set_direction(Direction.RIGHT)
            
    def keyReleaseEvent(self, event: QEvent):
        """Automatic event function used by PyQt6 to identify the release of a key.

        Args:
            event (QEvent): PyQt6 event related to the release of a key press.
        """
        if not isinstance(self.control, KeyboardControl):
            return
        self.control.set_direction(None)
    
    # ---- Related to the theme switch ----
    def switch_dark_mode(self):
        """Switches the theme dark/light. Also updates the corresponding
        versions of the icons.
        """
        instructions_buttons = [self.control_instructions_button,
                                self.transform_instructions_button,
                                self.game_instructions_button]
        icon = ""
        if self.dark_check.isChecked():
            icon = str(files("neuroarcade.ui.icons").joinpath("help_question_fdark.svg"))
            qdarktheme.setup_theme()
        else:
            icon = str(files("neuroarcade.ui.icons").joinpath("help_question_flight.svg"))
            qdarktheme.setup_theme("light")
        
        for ins_button in instructions_buttons:
            self.set_svg_icon(ins_button, icon)
            
    def set_svg_icon(self, button: QPushButton, path: str, size=24):
        """Set the icon in the path location to a QPushButton widget.

        Args:
            button (QPushButton): Button that gets the icon.
            path (str): Location of the icon file
            size (int, optional): Size of the icon. Defaults to 24.
        """
        button.setText("")
        button.setIcon(QIcon(path))
        button.setIconSize(QSize(size, size))
        button.setFixedSize(size + 12, size + 12)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

    def initialize_music(self):
        """Discovers music files and initializes the sounds manager for the background music.
        """
        self.sounds = MusicManager()
        available_music = []
        sounds_package = files("neuroarcade.sounds")

        for file in sounds_package.iterdir():
            if not file.is_file():
                continue
            filename = file.name
            # Only WAV files starting with "music_" are considered for background music
            if filename.startswith("music_") and filename.endswith(".wav"):
                # Remove prefix and extension to get the name of the song
                music_name = filename[len("music_"):-4]
                available_music.append(music_name)
                path = str(file)
                self.sounds.load(
                    name=music_name,
                    path=path
                )
        # Add the identified songs to the selector.
        self.music_selector_combo.addItems(available_music)
        self.sounds.play(available_music[0])
    
    def change_music(self, name: str):
        """Plays the song with the name in `name`

        Args:
            name (str): Name of the song, is the name of the file minus
                the "music\_" prefix and the ".wav" end.
        """
        self.sounds.play(name)
        
    def change_music_volume(self, volume: int):
        """Sets the volume of the background music to a percentage level.

        Args:
            volume (int): Percentage of the volume of the background music.
        """
        self.sounds.set_volume_percent(volume)
        
# Entry point
def main():
    """Main function to start running the game from the console.
    """
    
    # Parse argument to get the version of the arcade
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()

    if args.version:
        print(importlib.metadata.version("neuroarcade"))
        return

    # Initializes and opens the window
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()