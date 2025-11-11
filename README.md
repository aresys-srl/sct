[![Docs](https://img.shields.io/badge/docs-online-blue)](https://aresys-srl.github.io/sct/)

# SAR Calibration Toolbox (SCT)

Sar Calibration Toolbox (SCT) is the official Aresys Python toolbox for SAR quality data processing.
This software provides several features to perform a quality analysis of SAR L1 products (both SLC and GRD).

Supported product formats:

- Aresys Product Folder
- Sentinel-1 SAFE
- ICEYE
- NovaSAR-1
- EOS-04
- SAOCOM

Heritage missions:

- ENVISAT/ERS in ASAR format

Supported analyses:

- Point Target Analysis
- Radiometric Analyses: Noise Equivalent Sigma Zero (NESZ), Average Elevation Profiles, Scalloping Profiles
- Interferometric Coherence Analysis

This project derives from the original [SAR Calibration Tool](https://github.com/aresys-srl/sar-calibration-tool) developed
by Aresys since 2021 and it's aimed at expanding and refining its codebase and main algorithms, extending the support to
several other missions and sensors with an architecture that is well suited for new features additions.

## Official Documentation

Check out the [official documentation](https://aresys-srl.github.io/sct/) for more information, such as installation
instructions, tutorials, user guides, and API reference.

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

## Heritage Missions Support

Envisat and ERS heritage missions are supported in ASAR format using third party libraries that are published under the **GPL-3.0 license** requiring a change of the current **MIT license** for SCT software. To avoid unnecessary issues, the installation of heritage support is optional so that, if not needed, the software license remains unaltered.

To install SCT with heritage mission support:

    $ pip install .[heritage]


## E2E Dataset

A dataset for end to end tests is available at the following link and can be downloaded to assess the correct functionalities of the SCT tool.

> Download link:\
> [SCT E2E Tests Dataset](https://we.tl/t-JF1Hn9iwpE)

This dataset contains Sentinel-1A and NovaSAR products that let the users quantitatively test and verify all the main functionalities of SCT, namely
Point Target Analysis (on Surat Basin calibration site), Rain Forest and NESZ radiometric analyses and interferometric coherence
computation.

Once downloaded, follow the **sct_e2e_tests_instructions** that can be found inside the *end_to_end_tests* directory of this repo.

> [!IMPORTANT]
> An End User License Agreement (EULA) is included within the .zip archive dataset related to the usage of NovaSAR data.\
> When downloading this dataset, the user accepts the content of this EULA, that are summarized below.
> Regarding Sentinel-1 data, the access and use of Copernicus Sentinel data is available on a free, full and open basis and shall
> be governed by the [Legal Notice on the use of Copernicus Sentinel Data and Service](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice).

### NovaSAR EULA Summary

>"Accepting the EULA, the user may analyze, process and display the licensed SSTL Data (NovaSAR), make results available to employees of its organization and only reproduce SSTL Data (NovaSAR) in print or internet display including one of the copyright notices listed within the EULA. The End User and licensed entities shall not sell, rent, lease or loan the data. For a full list of restrictions, permitted uses and others on SSTL Data (NovaSAR) definitions and license, the user shall refer to the EULA."
