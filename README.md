# NeuroArcade

> A motor-learning / neuroplasticity experimentation platform disguised as an arcade.

NeuroArcade is a simple, lightweight but very flexible and powerful platform for neuroplasticity experimentation and motor-learning.

## The main idea

The user plays games, using a variety of control options, like the keyboard or computer vision based methods to control a game. The twist here is that this input may change in time, changing the actual effective output.

## The main components

- **A controller**: This is something that tells "*the user says LEFT, RIGHT, UP or DOWN*".
- **A transformer**: This transforms the input of the user to something different, "*the user says LEFT but I'll say RIGHT*".
- **A game**: This does something with the input the user has given.

With this data the user also gets some feedback:

- **The controller activity**: Shows something related to the processing of the user input, like the camera feed used by the Computer Vision based controllers.
- **The transformer logic**: Shows what the controller says and what the actual output is passed to the game.
- **The game activity**: Shows what happened to the game with the answer of the transformer.

## The philosophy

Adding new controllers, transformers and games should be incredibly easy, just adding one file per component and that's it. NeuroArcade will identify the new component and add it to the GUI. Every control should work with any transformer and any transformer with any game.

NeuroArcade is very modular, so every component is agnostic about the rest, and about the GUI itself. Everything is orchestrated by a central core, that makes available everything in the GUI, allowing the user to seamlessly switch between every component.

## How to contribute

In short, any controller, transformer and game has a base, some functions that every component should have. Each element is a class and goes inside a file with the same name as that class.

### Controllers

Key functions:

- `__init__`: Like any class, the constructor of the game, it can accept any necessary and customizable parameters passed as argument.
- `update`: This functions does not receive anything, but it's frequently called in order to get an answer. This function essentially should say "UP", "DOWN", "LEFT", "RIGHT" or None, depending on its internal logic.
- `get_config_schema`: Function that defines a dictionary with the parameters used to customize the game, each parameter defines some properties like the name of the parameter (as expected by the `__init__`), name for the user, description, default value and expected ranges.


