---
icon: lucide/history
title: "Changelog"
tags:
    - changelog
    - release notes
---

# Changelog

## v2.1.2

**Bug Fixing**

- Fixing testing interface logging issue
- Fixing testing interface return codes

## v2.1.1

**Incompatible Changes**

- Changed plugin infrastructure using **Stevedore**

**Other Changes**

- Command Line Interface: switched from Click to Typer
- Command Line Interface: moved testing CLI command to ``testing`` CLI group
- Command Line Interface: moved secondary CLI utilities commands to ``auxiliary`` CLI group
- Analyses Configurations: improved validation, now analysis config validation fails if no analysis-related parameters are provided

## v2.1.0

**Incompatible Changes**

- Code refactoring to support multiple analyses as self-registering plugins
- Documentation updated to reflect the new plugin architecture

## v2.0.9

**Other Changes**

- Testing module improved: added registry mechanism to support multiple analyses

## v2.0.8

**Other Changes**

- Command Line Interface: imports deferred to speed up CLI loading
- Fixing NetCDF Antenna Pattern reader following latest change in hierarchy structure
- Fixing RCS Error computation from PERSEO Quality by subtracting the Theoretical RCS

## v2.0.7

**Bug Fixing**

- Fixed bug in Rosamond Corner Reflector conversion to SCT compliant Point Target .csv dataset format

**Other Changes**

- Dropping support for Python 3.10

## v2.0.6

**Other Changes**

- Improved overall testing module for clarity and consistency
- Improved full implementation management of available analyses

## v2.0.5

**Additional Features**

- Adding Elevation Notch Analysis feature

## v2.0.4

**Other Changes**

- Improving CLI graceful exit when an exception is raised
- Improving Point Target Source management error handling
- Improving SCT Testing module adding analyses testing via SCT CLI tool

**Bug Fixing**

- Fixed a bug in Radiometric Analysis CLI when saving the config to the output folder
- Fixed a bug in Interferometric Analysis CLI when saving the config to the output folder
- Fixed CLI input allowing Point Target source to be a directory

## v2.0.3

**Additional Features**

- Adding Distributed Spectral Analysis and corresponding CLI command

**Other Changes**

- Grouped Point Target and Distributed Spectral Analysis under the main ``spectral-analysis`` command
- Improved ``InvalidProductType`` exception handling when loading products without having installed their dedicated format plugins
- Changed ``elevation_profile`` radiometric analysis cli command to ``elevation-profile``
- Updated radiometric analysis graphs generation inputs to match latest perseo-quality\
- Testing: changed KPI statistics tolerance for integration tests validation

**Bug Fixing**

- Fixed bug in `testing` module when performing Rain Forest and NESZ analyses with a single channel

## v2.0.2

**Additional Features**

- Adding GeoJSON format support for Point Target input sources

**Other Changes**

- Updating Spectral Analysis following changes in Perseo-Quality

**Incompatible Changes**

- Removing graphical output from Point Target Analysis functions, using those in Perseo Quality directly

## v2.0.1

**Other Changes**

- Dropping support for Aresys internal Point Target source (Point Target .xml file, Point Target Binary folder)
- Adding a dedicated script for converting Aresys internal Point target sources to SCT .csv compliant dataset
- Substituting Arepytools.io point target dataclass dependency with new PERSEO-Quality internal model
- Changing package layout to ``src``

## v2.0.0

**Other Changes**

- Substituted Arepyextras-Quality dependency with PERSEO-Quality package
- RCS Theoretical Computation moved to PERSEO-Quality
- Substituted Arepyextras-Perturbations dependency with newer PERSEO-Perturbations package

## v1.1.4

**Other Changes**

- Saving additional Corner Reflector info in Point Target Analysis output results .csv
- Saving radiometric statistics .csv when computing radiometric analysis using CLI tool

## v1.1.3

**Bug Fixing**

- Point Target Analysis: fixing bug in updating corrections config based on ALE corrections
- fixing PointTargetXML and PointTargetBinary conversion to unified default point target dataframe structure

## v1.1.2

**Incompatible Changes**

- Changed plugin interface for ALE corrections
- Removed ETAD support, moved to dedicated Sentinel-1 plugin

**Other Changes**

- Introduced graphs plotting option into testing module CLI/API and general improvement
- Adding dedicated logging module

## v1.1.1

**Other Changes**

- Changed tolerances and validation variables grouping in testing module

## v1.1.0

**Incompatible Features**

- Product Format python plugins supported with autodiscovery, removed all custom products implementations from IO module
- Removed automatic analysis, moved to SCAT

**Other Changes**

- Added log of detected plugins into testing module CLI
- Disabled integration tests, moved to dedicated plugins' CI

## v1.0.5

**Additional Features**

- IO: introduced support for ENVISAT/ERS ASAR product format
- Adding SCt testing module and secondary CLI tool to perform integration tests from tests .json registry

**Other Changes**

- Changed integration tests structure, removed Arepyextras Tests dependency
- Pinned Arepyextras EO Products due to bug in version 1.2.11 [to be removed]

## v1.0.4

**Additional Features**

- Added ``Point Target Spectral Analysis`` feature
- Added ``Point Target Ambiguity Ratio (PTAR)`` feature
- IO: introduced support for ASAR/Envisat product format

**Other Changes**

- Removed pinning from several dependencies
- Minor fixes

## v1.0.3

**Incompatible Features**

- Plugins mechanism for different product formats and readers introduced
- Automatic plugins discovery introduced
- Introduced burst check in ``read_data`` to support latest arepyextras-quality features
- Removed radiometric ``input_quantity`` option from radiometric analysis configuration: it is now always retrieved from the product itself

**Other Changes**

- added acquisition mode to protocol implementation for each supported external product format
- IO: introduced specific plugin for Aresys internal Product Folder format


## v1.0.2

**Additional Features**

- IO: introduced support for COSMO SkyMed product format
- IO: introduced support for RADARSAT 2 product format

**Bug Fixing**

- Fixed computation of ground range step and slant range step in meters for GRD products
- Fixed Point Target Binary reader after Arepytools bugfix

**Other Changes**

- Introduced PDM

## v1.0.1

**Additional Features**

- IO: introduced support for EOS-04 product format
- `Interferometric Analysis`: coherence computation from two co-registered products added
- Added support for input RCS values for PointTargetBinary format
- Documentation updated and improved

**Incompatible Features**

- `Radiometric Analysis`: ``Gamma Profiles`` removed, substituted with ``Average Radiometric Profiles``

**Bug Fixing**

- Removed lines/samples ordering reference from NovaSAR-1 product format implementation

**Other Changes**

- Unittest coverage improved
- Theoretical RCS computation improved
- Improved point target analysis graphical output points selection to match the arepyextras-quality bugfix
- Rosamond corner data converter updated to express azimuth elevation and tilt with the same reference system as surat basin's


## v1.0.0

**Additional Features**

- Added an automatic analyses detection feature based on intersection of product footprint with a registry of supported locations
- Added an utility to download Ionospheric TEC Maps from NASA/CDDIS archive

**Other Changes**

- Improved and extended the .csv template for Point Targets input data
- Global re-organization of the corrections management inside the library
- Integration tests updated and extended


**Bug Fixing**

- Fixed perturbations signs to correct ALE values both in range and azimuth directions
- Incidence angles computation evaluated at target range time instead of mid-range
- Fixed Sentinel-1 mid-swath detection function

## v1.0.0.de## v2

**Additional Features**

- `Interferometric Analysis`: added a new module to perform interferometric coherence analysis
- IO: introduced support for SAOCOM product format

**Other Changes**

- Removed support for SQLite Point Target internal Database: .csv template-compliant file is the only viable input option
- Minor type hint bugfixing
- Removed unused ``get_acquisition_time`` function form `io.io_manager`


## v1.0.0.de## v1

**Additional Features**

- `Radiometric Analysis`: added a new module to perform radiometric analysis and profiles extraction (NESZ, Gamma, Scalloping)
- IO: introduced support for NovaSAR-1 product format
- IO: introduced support for ICEYE product format


## v1.0.0.dev0

**Additional Features**

- IO: introduced support for Sentinel-1 SAFE product format
- IO: introduced support for Aresys internal Product Folder format
- `Point Target Analysis` geodynamics corrections: introduced support for computing solid tides and plate tectonics displacements
- `Point Target Analysis` atmospheric corrections: introduced support for computing ionospheric and tropospheric delays
- `Point Target Analysis` Sentinel-1 specific corrections: introduced support for computing range and azimuth corrections

**Other Changes**

- User manual added to project documentation
