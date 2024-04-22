.. _sct_cli_utils:

Secondary CLI Utilities
=======================

Alongside the main CLI tool, several secondary CLI utilities have been added to perform secondary tasks that can be useful
to the user.


Convert Rosamond point target dataset to SCT compliant .csv
-----------------------------------------------------------

.. code-block:: bash

   sct-rosamond-data-to-csv -s "rosamond_dataset" -d "date" -out "output_dir"


Download of Ionospheric TEC Maps
--------------------------------

.. code-block:: bash

   sct-ionospheric-maps-download -d "date" -c "analysis_center" -e "authentication_cddis_email" -out "output_dir"


Download of Tropospheric VMF3 Products
--------------------------------------

.. code-block:: bash

   sct-tropospheric-maps-download -d "date" -r "grid_resolution" -out "output_dir"