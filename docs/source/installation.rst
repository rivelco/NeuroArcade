Installation
============

System requirements
-------------------

Computer and a WebCam for now.

Installation of the python environment
--------------------------------------

The recommended installation method relies on `Conda <https://docs.conda.io/projects/conda/en/latest/index.html>`_ to manage your Python environments. I highly recommend using Conda for this purpose.

Installation using pip
~~~~~~~~~~~~~~~~~~~~~~

You can install NeuroArcade using pip. It's still recommended that you do this using conda or some other environment manager. If you're using conda type:

.. code-block:: console

    conda create -n neuroarcade python=3.10
    conda activate neuroarcade

The above command will create a new environment called `neuroarcade` and with python 3.10 installed. You can choose the name of the environment replacing `neuroarcade` with the name you prefer. After the environment is created it must be activated.

To install neuroarcade simply run:

.. code-block:: console

    pip install neuroarcade


Verifying the installation
--------------------------

To verify that NeuroArcade is installed correctly, run:

.. code-block:: console

    python -c "import neuroarcade; print(neuroarcade.__version__)"

Or alternatively: 

.. code-block:: console

    neuroarcade --version

If the version is printed without errors, the installation was successful.


Run the arcade
--------------

.. code-block:: console

    neuroarcade

It's also possible to launch the GUI by using:

.. code-block:: console

    python -m neuroarcade
