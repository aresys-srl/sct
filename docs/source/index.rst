.. _sct_docs_mainpage:

#############################
SAR Calibration Toolbox (SCT)
#############################

.. toctree::
    :maxdepth: 2
    :hidden:

    install  
    reference/api/index
    documentation/index
    dev_manual/index
    changelog

Sar Calibration Toolbox (SCT) is the official Aresys Python toolbox for SAR quality data processing.
This software provides several features to perform a quality analysis of SAR L1-B products (both SLC and GRD).

.. figure:: _static/images/projects.png
    :align: center

SCT is an open source tool developed in the framework of **EDAP** (Earthnet Data Assessment Project) and **SAR MPC**
(Mission Performance Cluster) projects. For more details please visit:

- EDAP webpage: `https://earth.esa.int/eogateway/activities/edap <https://earth.esa.int/eogateway/activities/edap>`_
- EDAP SAR missions: `https://earth.esa.int/eogateway/activities/edap/sar-missions <https://earth.esa.int/eogateway/activities/edap/sar-missions>`_
- SAR MPC webpage: `https://sar-mpc.eu/ <https://sar-mpc.eu/>`_


To check if the mission or product type to be analyzed is currently supported by this tool, please refer
to the :ref:`related section <sct_supported_missions>`.

A detailed list of currently supported analyses can be found :ref:`here <sct_analyses>`. 


.. grid:: 4

    .. grid-item-card::
        :img-top: _static/icons/api_icon.svg

        **API Documentation**
        ^^^^^^^^^^^^^^^^^^^^^

        Full documentation of modules, functions and objects available in SCT.
        References are automatically generated from docstrings.

        +++

        .. button-ref:: reference/api/index
            :expand:
            :color: secondary
            :click-parent:

            API Documentation

    .. grid-item-card::
        :img-top: _static/icons/user_manual_icon.svg

        **User Manual**
        ^^^^^^^^^^^^^^^

        In-depth information on the key concepts of SCT, with useful explanations and reference
        documentation detailing analyses processes and other information. 

        +++

        .. button-ref:: documentation/index
            :expand:
            :color: secondary
            :click-parent:

            User Manual

    .. grid-item-card::
        :img-top: _static/icons/tutorials_icon.svg

        **Implemented Analyses**
        ^^^^^^^^^^^^^^^^^^^^^^^^

        Section dedicated to the implemented analyses, with
        detailed description, usage and tutorials to help
        the user.

        +++

        .. button-ref:: documentation/analyses/index
            :expand:
            :color: secondary
            :click-parent:

            Getting started

    .. grid-item-card::
        :img-top: _static/icons/plugins_icon.svg

        **Product Format Plugins**
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^

        Documentation on how to install, use and create dedicated
        plugins for reading specific SAR product formats in order to
        process these products using the core analyses and functionalities
        of SCT.

        +++

        .. button-ref:: documentation/supported_missions
            :expand:
            :color: secondary
            :click-parent:

            Supported Formats
