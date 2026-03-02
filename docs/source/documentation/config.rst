.. _sct_config:

Configuration file setup for CLI tool
=====================================

The SCT Command Line Interface (CLI) tool let the user perform quality analyses on input products using the SCT Python
package as a command line executable software. All the registered analyses have a dedicated command that can be specified
to perform the operation of choice. Refer to the :ref:`available analyses <sct_analyses>` for further information.

This commands have been developed to be run with a minimal setup and only the essential parameters to be specified, such
as input and output folders.
For an in-depth documentation on how to use the command line tool, please refer :ref:`to this page <sct_cli>`.

Nevertheless, a configuration file (TOML format) can be provided as input to tweak and tune several options and parameters
in order to fully customize each analysis.

This configuration file is designed to work with optional sections that can be specified only if that specific feature should
be altered with respect to the default behavior. In principle, if all default settings are enough for the user, this
configuration file is not necessary.

.. admonition:: Validation

    Configuration files are validated through a JSON schema when provided as input for the tool to assess compliance.


Configuration file structure
----------------------------

The .toml configuration file is organized in sections and subsections related to specific analyses.
*Every section is optional*, and should be added only if default parameters for a specific analysis are not sufficient
for the user.

The available sections of this configuration file are:

- **general**: the highest level of configuration, not related to a specific feature.

- **analyses_sections**: sections that can be used to access specific analysis configurations and parameters. Each analysis implements its own configuration section.


.. seealso::

    To better understand the implications of changing specific parameters, refer to the :ref:`documentation of the implemented
    analyses <sct_analyses>`.


Detailed description of each section
------------------------------------

A detailed description of each section, sub-section and keywords can be found in the documentation section dedicated to
the analysis of interest.


General Configuration
^^^^^^^^^^^^^^^^^^^^^

The following parameters can be configured directly under the `general` section.

.. code-block:: toml
    :linenos:

    [general]
    save_log = true                 # save analysis log to output folder
    save_config_copy = true         # save analysis config to output folder
