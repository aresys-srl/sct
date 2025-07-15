.. _sct_supported_missions:

SCT Product Format Plugins
==========================

The SCT software itself does not natively support any specific format of Level 1 SAR products. Instead, it has been
designed to abstract away the dependency on the input format, relying solely on a generic Python protocol.
Once this protocol is satisfied, it enables the execution of all implemented analyses regardless of the type of input
product.

To handle the implementation of the methods and properties defined by the protocol, custom Python packages are used,
each dedicated to a particular sensor or format. These packages, managed as plugins by the software, are solely
responsible for assembling the information read from the product in its specific format, processing it, and ensuring that
all the functionalities required by the protocol are implemented.

The format reader itself does not necessarily have to be included within the plugin, it can be an external dependency for
the plugin python package.

Several plugins for some of the most common SAR products and sensors are already available.

.. note::

    To use the functionalities of SCT for a specific product, it is necessary to install, in addition to SCT,
    the corresponding plugin. Plugins are Python packages that can be discovered automatically by SCT once installed, because
    they are named sct_*_reader


Supported Missions and Products
===============================

The list of supported product types, a.k.a. missions and formats, that can be used as inputs for the SCT analyses
features is herein reported:

* **Aresys**: proprietary Product Folder.
* **Sentinel-1**: SAFE products.
* **ICEYE**: official stripmap and topsar products.
* **NovaSAR-1**: official stripmap and topsar products.
* **SAOCOM**: official stripmap and topsar products.
* **EOS-04**: official stripmap and topsar products.
* **COSMO SkyMed**: official stripmap and topsar products.
* **RADARSAT-2**: official stripmap and scansar products.
* **ENVISAT/ERS**: official ASAR products.

.. note::

    Support for **L1 products only** (both L1-A and L1-B) for each of these formats is available.

Installation and Usage
======================

To install a specific plugin for SCT using ``pip``:

.. code-block:: bash

    $ pip install name_of_sct_plugin

Then the software can discover automatically all the installed plugins and perform analyses on the products for which the
format plugin has been installed.
