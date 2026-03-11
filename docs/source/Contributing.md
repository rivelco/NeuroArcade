# Contributing

Thank you for your interest in contributing to **NeuroArcade**!

NeuroArcade is an open platform for exploring **motor learning, neuroplasticity, and human-computer interaction** through arcade-style experiments. Contributions from students, developers, researchers, and experimenters are highly encouraged.

This document explains how to extend the platform and contribute improvements.

---

## Philosophy

NeuroArcade is designed around a **modular architecture** that allows new functionality to be added without modifying the core system.

Most extensions can be implemented as new modules in one of the following categories:

* **Controllers** - define how user input is obtained
* **Transforms** - modify or reinterpret controller outputs
* **Games** - interactive environments for training or experiments
* **Visualizers** - display control signals or game information
* **Utilities** - helper tools and infrastructure

If you want to experiment with new ideas, you usually only need to add a new module in the appropriate folder.

---

## Project Structure

```
src/
|
├─ main.py
|
├─ controls/
|   ├─ base.py
|   └─ FaceTracker.py
|
├─ transforms/
|   ├─ base.py
|   └─ Identity.py
|
├─ games/
|   ├─ base.py
|   └─ MazeRunner.py
|
├─ core/
|   ├─ direction.py
|   └─ SoundManager.py
|
├─ assets/
|
├─ visualizers/
|
├─ ui/
|
├─ utils/
|
└─ sounds/
```

Modules for controls, games and transforms are **automatically discovered and loaded at runtime** using dynamic loading. This means new components can be added simply by placing them in the appropriate directory. It is not necessary to manually add those to the `main.py` file.

---

## Adding new components

### Creating a new game

To add a new game:

1. Create a new file in:

```
src/games/
```

Example:

```
src/games/MyNewGame.py
```

2. Create a class that inherits from `BaseGame`. This class must have the same name as the file you just created.

Example:

```python
from neuroarcade.games.base import BaseGame
from neuroarcade.core.direction import Direction
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

class MyNewGame(BaseGame):
    def __init__(self):
        pass

    def reset(self):
        pass

    def update(self, direction: Direction | None):
        pass

    def render(self):
        pass

    def get_config_schema(self):
        pass

    def get_instructions(self):
        pass
```

It's vital that the file and the class share the exact same name, this allows for the dynamic loading that gives the NeuroArcade its "plug and play" style.

Once the file exists, NeuroArcade will automatically detect it and make it available in the UI. It's recommended to check out the available games to get ideas about the implementation of each function. The documentation illustrates the use of each function.

---

### Creating a new controller

Controllers convert **sensor data or input signals into directional commands**.

1. Create a new file in:

```
src/controls/
```

Example:

```
src/controls/MyController.py
```

2. Create a class that inherits from `BaseControl`. This class should have the same name as the file you just created.

Example:

```python
from neuroarcade.core.direction import Direction
from neuroarcade.controls.base import BaseControl
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

class MyController():
    def __init__(self):
        pass

    def update(self):
        pass

    def get_config_schema(self):
        pass
    
    def get_instructions(self):
        pass
```


The `update` function should return `(Direction | None, visualization_frame | None)`. Consider that while not mandatory, the visualization frame is shown in the UI to help users understand how the controller behaves. This is why I highly recommend including that one in the `update` method.

Controllers can use any input modality, for example:

* webcam tracking
* motion sensors
* EMG
* EEG
* external hardware
* etc, get creative!

---

### Creating a new transform

Transforms modify the direction produced by a controller before it reaches the game.

Examples include:

* axis inversion
* nonlinear mappings
* experimental perturbations

1. Create a file in:

```
src/transforms/
```

Example:

```
src/transforms/MyTransform.py
```

2. Create a class that inherits from `BaseTransform`. This class should have the same name as the file you just created.

```python
from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

class MyTransform(BaseTransform):
    def apply(self, direction: Direction):
        pass
    
    def get_config_schema(self):
        pass
    
    def get_instructions(self):
        pass
```

---

## Configuration system

Controllers, transforms, and games can expose parameters dynamically through:

```
get_config_schema()
```

The UI automatically builds configuration widgets from this schema.

Example:

```python
{
    "speed": {
        "name": "Player speed",
        "description": "Movement speed of the player",
        "default": 5,
        "min": 1,
        "max": 10
    }
}
```

This code will generate a spin box widget with a label saying "Player speed", with a tooltip that says "Movement speed of the player". The default value for the widget will be 5 and will only accept values from 1 to 10, inclusive. 

No UI code is required to add new parameters. Check the schema from other controllers and games to have a better idea.

---

## Documentation

All core classes include detailed **docstrings**.

Full API documentation is available through the project's **Sphinx documentation site**.

When adding new functionality:

* Write clear docstrings
* Follow the style used in existing modules
* Document parameters and return values

This ensures the Sphinx documentation remains useful.

---

## Sound effects and music

Sound assets live in:

```
src/sounds/
```

Naming conventions:

```
effect_<name>.wav
music_<name>.wav
```

As suggested by the conventions, the sounds with the "effect_" prefix will be available for the games as sound effects. The "music_" prefix should be used for longer sound files, and will be looped across all the games. The rest of the text, after the prefixes is the name of the music or effect.  Effects are loaded by the base game class by running the `initialize_sounds` method. All the sound effects are available for all the games.

### Adding music

Just copy the `.wav` file into the `src/sounds/` directory and name it "music_&lt;music_name&gt;.wav". The music will be available for selection at the dropdown widget in the UI with the name you specified in the filename. No further modification to the code is needed.

Only `.wav` files are supported for now.

### Adding sound effects to games

Copy the `.wav` file with the sound effect to `src/sounds/`. Name the file "effect_&lt;effect_name&gt;.wav", where `effect_name` is the name you want to use to call your effect in the games.

Once you have added the sound effect file you need to initialize the sound manager in your game. This is achieved by calling the `initialize_sounds` method of the `BaseGame` class inside the game where you want to add the effect. For example:

```python
class MyNewGame(BaseGame):
    def __init__(self, grid_w=24, grid_h=18):
        super().__init__()

        self.grid_w = grid_w
        self.grid_h = grid_h
        
        self.initialize_sounds()
```

When you run this function the game will import all the sound effects and after that you can call any sound in any part of your game using the name of the effect (i.e. the name of the audio file without the "effect_" prefix).

For example adding the following code to some part of your game will play the `effect_eat.wav` file:

```python
if self.player == self.target:
    self.sounds.play("eat")
```

The sound effects are played once, only when they are called.

---

## Coding Guidelines

Please try to follow these general guidelines:

* Use clear and descriptive variable names
* Keep functions focused and readable
* Prefer simple designs over complex abstractions
* Write docstrings for public classes and functions
* Avoid introducing heavy dependencies unless necessary

---

## User interface

The user interface uses [PyQt6 for python](https://doc.qt.io/qtforpython-6/). It is advisable to make modifications to the `src/neuroarcade/ui/MainWindow.ui` using the PyQt6 Designer app. Launch the designer with:

```bash
pyqt6-tools designer
```

## Submitting contributions

Typical workflow:

1. Fork the repository
2. Create a new branch
3. Clone the repository to your machine.
4. Create a new python environment for your contribution, for example using conda:

```bash
conda create -n neuroarcade_dev python=3.10
```

5. Install the NeuroArcade in editable mode. For this go to the place were you have cloned your repo, then activate your environment and install the arcade:

```bash
cd {{path_to_the_repo}}
conda activate neuroarcade_dev
pip install -e .[all]
```

Note that you can install NeuroArcade using the optional dependencies where:

* `[dev]` - Installs also the `pyqt6-tools` module to use the designer.
* `[docs]` - Install additional dependencies for adding documentation
* `[all]` - Installs both the `dev` and `docs` modules.

6. Implement your feature or improvement
7. Add documentation if needed
8. Submit a pull request

When possible, include:

* a short description of the feature
* example usage
* screenshots for games or controllers

---

## Ideas for contributions

Some areas where contributions would be especially valuable:

* New experimental games
* New control paradigms
* Alternative visualizers
* Support for additional sensors
* Experimental transforms for motor adaptation
* Improvement or correction to the documentation
* New functionalities for the arcade

NeuroArcade is intended to be a **playground for exploring motor learning and human-machine interaction**, so creative ideas are welcome.

---

## Questions

If you are unsure where something should go, open an issue or discussion in the repository.

We are happy to help new contributors get started.

---

Thank you for helping improve NeuroArcade!
