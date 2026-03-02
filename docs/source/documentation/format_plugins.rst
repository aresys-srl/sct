.. _sct_format_plugins:

Product Format Plugins
======================

Several plugins for some of the most common SAR products and sensors are already available.

.. note::

    To use the functionalities of SCT for a specific product, it is necessary to install, in addition to SCT,
    the corresponding plugin. Plugins are Python packages that can be discovered automatically by SCT once installed, because
    they are named sct_*_reader

Installation and Usage
======================

To install a specific plugin for SCT using ``pip``:

.. code-block:: bash

    $ pip install name_of_sct_plugin

Then the software can discover automatically all the installed plugins and perform analyses on the products for which the
format plugin has been installed.
