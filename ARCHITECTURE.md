# Architecture

NeuroArcade is designed as a **modular experimentation platform** for studying motor learning and human-computer interaction.
The architecture emphasizes **extensibility**, **simplicity**, and **rapid experimentation**.

The system separates input acquisition, signal transformation, and gameplay into independent modules that can be combined dynamically.

---

## Core design philosophy

NeuroArcade is built around three principles:

**Modularity**

New functionality should be added by creating new modules, not modifying existing code.

**Experimentation**

Researchers should be able to quickly test new control paradigms, perturbations, and training environments.

**Separation of concerns**

Different responsibilities are separated into independent components:

* Controllers capture user input
* Transforms manipulate input signals
* Games define interactive environments

---

## High level system flow

During runtime, NeuroArcade processes user interaction in a loop.

```
User Input
     ↓
Controller
     ↓
Transform
     ↓
Game Logic
     ↓
Game Rendering
     ↓
User Interface
```

Each stage operates independently and communicates through a simple interface based on **directional commands**.

---

## Direction system

The primary control signal used by NeuroArcade is the `Direction` type.

Currently the directions include:

```
UP
DOWN
LEFT
RIGHT
None
```

Controllers convert raw input signals into a direction.
Transforms can modify or reinterpret these signals before they are passed to the game.

---

## Main game loop

The central loop is implemented in `main.py`.

The loop performs the following steps:

1. Query the controller for input
2. Update the controller output visualization
3. Apply the active transform
4. Update the transform output visualization
5. Update the active game
6. Render the game frame
7. Update the UI

This architecture allows any controller, transform, or game to be swapped at runtime.

---

## Module categories

NeuroArcade modules are organized into several categories.

### Controllers

Location:

```
src/controls/
```

Controllers convert **raw sensor or input data** into directional commands.

Examples:

* Face tracking controllers
* Keyboard input
* Motion sensors
* External hardware

All controllers inherit from:

```
BaseControl
```

Controllers return both:

```
Direction
Visualization frame
```

The visualization frame helps users understand what the controller is detecting.

---

### Transforms

Location:

```
src/transforms/
```

Transforms modify controller output before it reaches the game.

Typical uses include:

* axis inversion
* delayed response
* noise injection
* nonlinear mappings
* motor perturbations

Transforms inherit from:

```
BaseTransform
```

---

### Games

Location:

```
src/games/
```

Games implement the interactive environment where training or experiments occur.

All games inherit from:

```
BaseGame
```

Required methods:

```
reset()
update(direction)
render()
get_config_schema()
get_instructions()
```

Games are responsible for maintaining their own state and generating frames for display.

---

## Dynamic module discovery

NeuroArcade uses **dynamic module loading** to discover available components.

This is implemented in:

```
src/utils/loader.py
```

At startup, the loader scans module directories and imports available classes automatically. This allows new modules to be added simply by creating a new file in the appropriate directory. This way, no core code changes are required.

---

## Configuration system

Modules can expose configurable parameters dynamically through:

```
get_config_schema()
```

The UI automatically generates configuration widgets from this schema.

This allows developers to add configurable parameters without writing UI code.

---

## Visualization system

Controller and transform outputs can be visualized in the UI.

These visualizations are implemented in:

```
src/visualizers/
```

They help users understand:

* current direction
* controller response
* transform effects

---

## Sound system

Sound effects and music are managed by the sound manager in:

```
src/core/SoundManager.py
```

Sound files are located in:

```
src/sounds/
```

Naming conventions:

```
effect_<name>.wav
music_<name>.wav
```

Games can trigger sound effects through the sound manager.

---

## User interface

The user interface uses [PyQt6 for python](https://doc.qt.io/qtforpython-6/) and its components are located in:

```
src/ui/
```

Major roles include:

* Displaying the game
* Showing controller visualizations
* Exposing module configuration
* Displaying instructions

The UI layer interacts with modules through well-defined interfaces and does not depend on specific implementations.

---

## Extending the system

The architecture allows easy extensions in several areas:

* New control paradigms
* Experimental transforms
* Novel training games
* Alternative visualizers

Most extensions require creating only a **single new module file**.

---

## Future Directions

Potential future architectural extensions include:

* Reinforcement learning agents
* Experiment logging systems
* Data recording pipelines
* Multiplayer or collaborative modes
* Hardware interfaces

The modular design of NeuroArcade should make these additions straightforward.

