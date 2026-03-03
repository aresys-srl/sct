.. _sct_cli_utils:

CLI Utilities
=============

Auxiliary CLI utilities have been added to perform secondary tasks that can be useful to the user. The list of available
commands can be accessed by calling:

.. code-block:: bash

   sct auxiliary --help/-h

Convert Rosamond Point Target Dataset
-------------------------------------

This utility let the user convert a Rosamond Point Target dataset as downloaded from their site into a SCT compliant
Point Target .csv file.

.. code-block:: bash

   sct auxiliary rosamond-pt-converter -s "rosamond_dataset" -d "date" -out "output_dir"


Download of Ionospheric TEC Maps
--------------------------------

.. code-block:: bash

   sct auxiliary iono-downloader -d "date" -c "analysis_center" -e "authentication_cddis_email" -out "output_dir"


Download of Tropospheric VMF3 Products
--------------------------------------

.. code-block:: bash

   sct auxiliary tropo-downloader -d "date" -r "resolution" -out "output_dir"
