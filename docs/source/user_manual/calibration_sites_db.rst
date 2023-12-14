.. _sct_cal_sites_db:

Internal Calibration Sites Database
===================================

SCT provides an internal Calibration Sites database containing information about selected calibration sites on
Earth with their location, number of targets, target types and many other data that are needed to properly process a
Point Target Analysis.

Data are stored in a *SQLite* database that can be queried automatically by the tool base on given user inputs. These data
are up to date with the latest measurements campaigns occurred before this tool release.

As of now, the following calibration sites have been implemented:


+--------------------+------------------------------------+---------------------+
| Calibration Site   | Location                           | Database Table Name |
+====================+====================================+=====================+
| **Surat Basin**    | Queensland, Australia              | ``surat_basin``     |
+--------------------+------------------------------------+---------------------+
| **Rosamond**       | Rosamond Dry Lakebed, California   | ``rosamond``        |
+--------------------+------------------------------------+---------------------+
