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
Obviously, a calibration site or external point target file must be provided in order to properly run the analysis.

If the user wants to use the internal Calibration Sites database, a simple string with the location of interest can be specified
using the ``-cal`` option. Please check that the input string belongs to the available calibration sites by :ref:`checking the
*Database Table Name* on this documentation page<sct_cal_sites_db>`.


.. code-block:: bash

   python -m sct [--config "path_to_config"] target_analysis -p "product_path" -out "output_dir" [-cal "site_name"]

If the user wants to use its own calibration target data, this can be easily done by providing the path to the file to the
command line tool using the option ``-pt``.

.. important::

   An external source of point targets data can be provided as a .csv file that must be compliant with the template that
   can be downloaded from the resources folder on GitHub.
