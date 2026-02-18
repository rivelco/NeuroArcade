Architecture Overview
=====================

NeuroArcade is structured around five core abstractions:

- BaseGame
- BaseControl
- BaseTransform
- Direction
- SoundManager

Execution Flow
--------------

1. Controller produces a Direction
2. Transform modifies it
3. Game updates state
4. Game renders frame
5. UI displays visualization
