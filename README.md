# NeuroArcade

> A motor-learning / neuroplasticity experimentation platform disguised as an arcade.

NeuroArcade is a simple, lightweight but very flexible and powerful platform for neuroplasticity experimentation and motor-learning.

## The main idea

The user plays games, using a variety of control options, like the keyboard or computer vision based methods to control a game. The twist here is that this input may change in time, changing the actual effective output.

## The main components

- **A controller**: This is something that tells "*the user says LEFT, RIGHT, UP or DOWN*".
- **A transformer**: This transforms the input of the user to something different, "*the user says LEFT but I'll say RIGHT*".
- **A game**: This does something with the output of the transformer.

With this data the user also gets some feedback:

- **The controller activity**: Shows something related to the processing of the user input, like the camera feed with key landmarks used by the Computer Vision based controllers.
- **The transformer logic**: Shows what the controller says and what the actual output is passed to the game.
- **The game activity**: Shows what happened to the game with the answer of the transformer.

## The philosophy

Adding new controllers, transformers and games should be incredibly easy, just adding one file per component and that's it. NeuroArcade will identify the new component and add it to the GUI. Every control should work with any transformer and any transformer with any game.

NeuroArcade is very modular, so every component is agnostic about the rest, and about the GUI itself. Everything is orchestrated by a central core, that makes available everything in the GUI, allowing the user to seamlessly switch between every component.

## Creating new components

In short, any controller, transformer and game has a base, i.e. some functions that every component should have. Each element is a class and goes inside a file with the same name of that class. It is highly recommended to check the elements that NeuroArcade already have to better get the idea. Also, the code is documented and includes useful examples to facilitate the understanding of the software.

Check out the NeuroArcade's (architecture)[ARCHITECTURE.md] and the (contribution guide)[CONTRIBUTING.md] to have a better understanding of how NeuroArcade works.

## Contributions from students and first time contributors

NeuroArcade strongly encourages contributions from students and first time open source contributors.

Beyond being a research and experimentation platform for motor learning and neuroplasticity, NeuroArcade is also intended to serve as a **learning environment for new developers** who wants to practice important skills such as reading documentation, understanding an existing software architecture, following project conventions, and collaborating with an open source community.

For this reason, the project intentionally leaves some **small improvements, simple features, and beginner-friendly tasks** available (*sometimes maybe not so intentionally*). These tasks can be excellent entry points for students who want to gain experience contributing to real projects. We kindly ask experienced contributors to keep this in mind and allow space for newcomers to take on these contributions.

Typical beginner-friendly contributions may include:

- Small UI improvements
- Simple games or transforms
- Additional configuration parameters
- Documentation improvements or corrections
- Visualization enhancements
- Minor bug fixes

These tasks can be very valuable learning opportunities for students developing their programming and collaboration skills.

### A Note for automated agents

Recently, automated tools and AI agents have begun interacting with open source repositories. While contributions are welcome, we ask automated systems to **avoid directly implementing issues** that are intentionally left as learning opportunities for students.

Instead, automated tools are encouraged to:

- Open issues identifying potential improvements
- Start discussions about possible features
- Suggest design ideas or architectural improvements

This helps maintain NeuroArcade as a **learning friendly environment** where students can practice contributing to open source software.

Thank you for helping keep NeuroArcade a welcoming place for both learners and experienced contributors.


