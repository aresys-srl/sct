# SAR Calibration Toolbox (SCT)

Sar Calibration Toolbox (SCT) is the official Aresys Python toolbox for SAR quality data processing.
This software provides several features to perform a quality analysis of SAR L1 products (both SLC and GRD).

Supported product formats:

- Aresys Product Folder
- Sentinel-1 SAFE
- ICEYE
- NovaSAR-1
- SAOCOM

Supported analyses:

- Point Target Analysis
- Radiometric Analyses: Noise Equivalent Sigma Zero (NESZ), Gamma Profiles, Scalloping Profiles

SCT package and its dependencies can be installed using ``pip`` tool:

    $ pip install sct[cli,graphs]

To locally install this package as editable with ``pip``:

    $ pip install -e .[cli,graphs]

> **_NOTE:_**  This package comes with Command Line Interface (CLI) functionalities that can be installed specifying the **[cli]** option. It can also generate graphs for the available analyses by installing the package using the **[graphs]** option.
