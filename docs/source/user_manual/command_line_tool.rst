.. _sct_cli:

Command Line Interface (CLI) tool
=================================

CLI tutorials and examples.

Operating Modes
---------------

To facilitate the use of the SCT tool, several pre-defined `Operating Modes` have been configured based on most common
use scenarios. 

.. admonition:: Configuration file

   | A configuration file can be provided to edit the defaults parameters or enable/disable specific features.
   | :ref:`Check this page<sct_config>` to properly setup a valid configuration file.

OM1: Point Target Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^

Point target analysis can be performed using the following command just specifying the input product and the output directory.
Obviously, an external file containing point targets locations and data must be provided in order to properly run the analysis.

.. code-block:: bash

   python -m sct [--config "path_to_config"] target_analysis -p "product_path" -out "output_dir" -pt "point_target_file_path"


.. important::

   The external source of point targets data provided as a .csv file must be compliant with the template that
   can be downloaded from the resources folder on GitHub. :ref:`Check the related documentation for further information<sct_pt_file>`.
