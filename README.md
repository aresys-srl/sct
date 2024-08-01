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

## Package Installation

This package depends on several python packages that can be found on the [public Aresys github page](https://github.com/aresys-srl) that must be installed before SCT itself. To do so, follow the procedure listed below.

After cloning all the repositories of the following Aresys packages, ``cd`` in each of them and locally install the packages
following this order:

- [Arepytools](https://github.com/aresys-srl/arepytools)
- [Arepyextras - Iers Solid Tides](https://github.com/aresys-srl/arepyextras-iers_solid_tides)
- [Arepyextras - Perturbations](https://github.com/aresys-srl/arepyextras-perturbations)
- [Arepyextras - EO Products](https://github.com/aresys-srl/arepyextras-eo_products)
- [Arepyextras - Quality](https://github.com/aresys-srl/arepyextras-quality)

using with ``pip``:

    $ pip install .

> [!NOTE]
> Arepyextras - Quality comes with graphical functionalities that can be installed using the **[graphs]** option, as shown
> in the snippet below for the SCT installation.

After all these packages have been installed in the same Python environment, do the same with the SCT project:

    $ pip install .[cli,graphs]

> [!NOTE]
> This package comes with Command Line Interface (CLI) functionalities that can be installed specifying the **[cli]** option.\
> It can also generate graphs for the available analyses by installing the package using the **[graphs]** option.
