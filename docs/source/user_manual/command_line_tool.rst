.. _sct_cli:

Command Line Interface (CLI) tool
=================================

A command line interface has been developed to be used directly from a shell prompt to access SCT functionalities with an
easy to use approach. All the main functionalities are supported with a dedicated command with its help documentation.

The main command line tool that can be accessed using the ``sct`` command in your favorite shell.

Another set of companion CLI utilities has been developed aside from the main CLI tool and can be accessed using specific
commands :ref:`that are listed here<sct_cli_utils>`


SCT CLI
^^^^^^^

SCT command line can be invoked in the terminal session as:

.. code-block:: bash

   sct [--version] [--config/-cfg] [--help/-h]

This is the entry point for the console script. The configuration needed to perform the analysis must be provided at here
using the `--config/-cfg` argument. The available analysis have been implemented as commands of this parent CLI but the
above command alone won't perform any kind of operation.
To select the operation of choice, use the available commands that can be listed using the `--help/-h` option.


Point Target Analysis
^^^^^^^^^^^^^^^^^^^^^

Point target analysis can be performed using the following command just specifying the input product and the output directory.
Obviously, an external file containing point targets locations and data must be provided in order to properly run the analysis.

.. code-block:: bash

   sct [--config "path_to_config"] target-analysis -p "product_path" -out "output_dir" -pt "point_target_file_path"

This is the basic way of performing this analysis. There are other options that can be specified for the analysis and they
can be listed using the `--help/-h` option.

.. important::

   | The external source of point targets data provided as a .csv file must be compliant with the template that can be
   | downloaded from the resources folder on GitHub.
   | :ref:`Check the related documentation for further information<sct_pt_file>`.

Radiometric Analysis
^^^^^^^^^^^^^^^^^^^^

Radiometric analysis has been implemented with a set of commands that let the user select the specific type of Radiometric
analysis to be performed, namely ``nesz``, ``gamma`` and ``scalloping``.
Further information about each of these analysis :ref:`can be found here<sct_analyses>`.

.. code-block:: bash

   sct [--config "path_to_config"] radiometric-analysis [nesz/gamma/scalloping] -p "product_path" -out "output_dir" -g "graphs_enabled"

To list all the available options use the `--help/-h` argument.
