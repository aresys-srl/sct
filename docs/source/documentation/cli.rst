.. _sct_cli:

Command Line Interface (CLI)
============================

A command line interface has been developed to be used directly from a shell prompt to access SCT functionalities with an
easy to use approach. All the main functionalities are supported with a dedicated command with its help documentation.

The main command line tool that can be accessed using the ``sct`` command in your favorite shell.

Another set of companion CLI utilities has been developed aside from the main CLI tool and can be accessed using specific
commands :ref:`that are listed here<sct_cli_utils>`

Each implemented analysis has a dedicated command that can be specified to perform the operation of choice. See the
:ref:`available analyses <sct_analyses>` documentation to learn more about each analysis and its command.

SCT CLI
-------

SCT command line can be invoked in the terminal session as:

.. code-block:: bash

   sct [--version] [--config/-cfg] [--help/-h]

This is the entry point for the console script. The configuration needed to perform the analysis must be provided
using the ``--config/-cfg`` argument. The available analysis have been implemented as commands of this parent CLI but the
above command alone won't perform any kind of operation.
To select the operation of choice, use the available commands that can be listed using the `--help/-h` option.
