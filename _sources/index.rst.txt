NeuroArcade Documentation
=========================

.. important::
   
   A motor-learning / neuroplasticity experimentation platform disguised as an arcade.

NeuroArcade is a simple, lightweight but very flexible and powerful platform for neuroplasticity experimentation and motor-learning.

About the NeuroArcade
---------------------

NeuroArcade is an open-source platform that transforms principles from neuroscience and motor learning research into interactive arcade-style activities. By separating input sensing, signal transformation, and gameplay into modular components, the platform allows researchers, educators, and students to rapidly prototype experiments exploring sensorimotor control, adaptation, and neuroplasticity.

Because the system can integrate diverse input modalities, from computer vision and gesture recognition to external sensors, it provides a flexible environment for demonstrating how the brain learns to control actions under different constraints or perturbations. 

This makes NeuroArcade particularly valuable not only for exploratory research and rapid experimental prototyping, but also for **scientific outreach and education** because complex concepts such as neural adaptation, motor learning, and brain–machine interfaces can be experienced directly through a playful interaction.

As an open-source and extensible platform, NeuroArcade also serves as a collaborative tool where developers, students, and scientists can design new games, controllers, and transformations, turning the platform into both a research sandbox and a **public-facing demonstration of how neuroscience and technology intersect**.

.. note::
   This platform was originally inspired by public science outreach efforts at the `Instituto de Neurobiología UNAM <https://inb.unam.mx/>`__. It later evolved into a broader tool for research, education, and interactive demonstrations of neuroscience and motor learning.

The user plays games, using a variety of control options, like the keyboard or computer vision based methods to control a game. The twist here is that this input may change in time, changing the actual effective output.

.. toctree::
   :caption: The basics
   
   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/main
   api/core
   api/controls
   api/games
   api/transforms
   api/ui
   api/utils
   api/visualizers

.. toctree::
   :caption: Expanding the arcade
   
   Architecture
   Contributing