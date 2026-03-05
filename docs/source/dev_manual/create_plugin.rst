Creating a New Format Plugin
============================

SCT supports multiple satellite product formats through a **plugin-based architecture**.
Instead of embedding format-specific logic directly in the core library, input products are handled by **external plugin packages**
that implement a common interface.

This page explains how to create and distribute a new **Input Product Plugin** for SCT.

Overview
--------

An SCT input product plugin is a **separate Python package** that:

1. Implements the :py:class:`~sct.plugins.protocols.InputProductPluginProtocol`.
2. Exposes the plugin class through a **Python entry point** in the ``sct.input_products`` namespace.
3. Is installed alongside SCT so it can be **automatically discovered**.

Once installed, SCT will detect the plugin at runtime and make it available to the analysis pipeline.

.. note::

    The plugin itself does not necessarily need to implement all the low-level logic required to read the input product.
    In many cases, existing plugins rely on external libraries, which are not part of the core SCT package, to handle the
    parsing and loading of the native product format. The plugin acts primarily as an adapter layer: it uses external
    tools or libraries to access the product data and then reorganizes and exposes the relevant information so that it
    conforms to the SCT internal data model required by the analyses.


Plugin Package Structure
------------------------

A minimal plugin package may look like the following:

.. code-block:: text

    root
    ├── src/
    │   └── sct_<product_name>_reader/
    │       ├── __init__.py
    │       ├── interface.py
    │       └── reader.py
    ├── pyproject.toml
    └── README.md

Typical responsibilities:

- ``interface.py``: defines the plugin class implementing the protocol.
- ``reader.py``: contains the product parsing logic.
- ``pyproject.toml``: declares the plugin entry point.

.. note::

    Substitute ``<product_name>`` with the name of the product.


Implementing the Plugin Interface
---------------------------------

Every plugin must implement the :py:class:`~sct.plugins.protocols.InputProductPluginProtocol`.

A minimal implementation looks like the following:

.. code-block:: python

    from sct.plugins.protocols import InputProductPluginProtocol
    from sct_<product_name>_reader import __version__


    class ProductNamePlugin(InputProductPluginProtocol):

        version = __version__

        @classmethod
        def get_manager(cls) -> type[SCTInputProduct]:
            """Return the class of the input product manager."""

        @classmethod
        def get_detector(cls) -> Callable[[str | Path], bool]:
            """Return a function that returns True if the given product can be read by this plugin."""

        @classmethod
        def get_ale_corrector(cls) -> ALECorrectionFunctionType:
            """Return the function that corrects the ALE errors in the product, if any."""

The plugin is responsible for:

- Determining whether a product belongs to the supported format
- Creating a reader object capable of exposing the required data
- Adapting the native product structure to the format expected by SCT analyses

The ``version`` attribute should contain the version of the plugin package. This is typically imported from the package init.

Keeping track of the plugin version helps SCT:

- ensure compatibility between plugins and the core framework
- improve reproducibility of analysis results
- assist debugging and reporting

.. note::

    Substitute ``<ProductName>`` with the name of the product.

The Input Product Manager
~~~~~~~~~~~~~~~~~~~~~~~~~

The :py:meth:`~sct.plugins.protocols.InputProductPluginProtocol.get_manager` method must return a class implementing
the :py:class:`~sct.io.extended_protocols.SCTInputProduct` protocol.

The returned class is the **input product manager**, which is responsible for:

- opening the product files
- parsing the native product structure
- exposing the product data through the **standard SCT data model**

The manager therefore acts as an **adapter layer** between the product format and the analysis modules.

Conceptually:

.. code-block:: text

    Native Product Format
            │
            │  (plugin reader)
            ▼
    Input Product Manager (SCTInputProduct)
            │
            │  standardized interface
            ▼
        SCT Analyses

Internal Data Model
~~~~~~~~~~~~~~~~~~~

All analyses in SCT expect their inputs to follow a **common internal data model**. This model is defined through the
:py:class:`~sct.io.extended_protocols.SCTInputProduct` protocol and related protocol definitions.

The manager returned by :py:meth:`~sct.plugins.protocols.InputProductPluginProtocol.get_manager` must therefore implement
all the attributes and methods required by these protocols.

This ensures that:

- analyses can run **independently of the original product format**
- different satellite products can be processed using the **same analysis code**
- new product formats can be supported simply by providing a compatible manager

In practice, the input product manager translates the native product data into the structures required by SCT analyses.

Registering the Plugin
----------------------

To allow SCT to discover the plugin automatically, the plugin class must be registered through a **Python entry point**.

In your ``pyproject.toml`` file:

.. code-block:: toml

    [project.entry-points."sct.input_products"]
    myproduct = "sct_<product_name>_reader.interface:<ProductName>Plugin"

Where:

- ``sct.input_products`` is the **entry point namespace** used by SCT.
- ``<product_name>`` is the plugin identifier.
- ``sct_<product_name>_reader.interface:<ProductName>Plugin`` is the import path to the plugin class.

When SCT starts, the plugin loader will scan this namespace using ``stevedore`` and automatically import all available
plugins.

Example
-------

Below is a simplified example similar to existing plugins:

.. code-block:: toml

    [project.entry-points."sct.input_products"]
    aresys = "sct_eos04_reader.interface:EOS04ProductPlugin"

This registers the class ``EOS04ProductPlugin`` as a plugin for SCT.

Plugin Discovery
----------------

At runtime, SCT uses ``stevedore`` to discover and load plugins:

.. code-block:: python

    from stevedore import ExtensionManager

    manager = ExtensionManager(
        namespace="sct.input_products",
        invoke_on_load=True,
    )

All installed packages exposing entry points in the ``sct.input_products`` namespace are loaded automatically.

No manual registration is required.

Installation
------------

Once the plugin package has been created, it can be installed using ``pip``:

.. code-block:: bash

    pip install sct-<product_name>-reader

After installation, SCT will automatically detect the plugin during startup.

Testing the Plugin
------------------

After installing the plugin, you can verify that it has been detected by SCT
by checking the plugin registry:

.. code-block:: python

    from sct.plugins import available_plugins

    print(available_plugins)

Your plugin should appear in the list of available input product handlers.

Best Practices
--------------

When developing a plugin:

- Keep **product-specific logic isolated** inside the plugin package.
- Avoid introducing dependencies into the core SCT package.
- Follow the interfaces defined in :py:mod:`sct.plugins.protocols`.
- Provide **unit tests** using representative product samples.
- Clearly document the supported product version and sensor.

Distribution
------------

Plugins can be distributed independently from SCT via PyPI or internal/local package repositories.

This allows users to install only the plugins required for the specific products they want to analyze.
