Changelog
=========

v1.1.2
------

**Other changes**

- introduced graphs plotting option into testing module CLI/API

v1.1.1
------

**Other changes**

- Changed tolerances and validation variables grouping in testing module

v1.1.0
------

**Incompatible Features**

- Product Format python plugins supported with autodiscovery, removed all custom products implementations from IO module
- Removed automatic analysis, moved to SCAT

**Other changes**

- Added log of detected plugins into testing module CLI
- Disabled integration tests, moved to dedicated plugins' CI

v1.0.5
------

**Additional Features**

- IO: introduced support for ENVISAT/ERS ASAR product format
- Adding SCt testing module and secondary CLI tool to perform integration tests from tests .json registry

**Other changes**

- Changed integration tests structure, removed Arepyextras Tests dependency
- Pinned Arepyextras EO Products due to bug in version 1.2.11 [to be removed]

v1.0.4
------

**Additional Features**

- Added ``Point Target Spectral Analysis`` feature
- Added ``Point Target Ambiguity Ratio (PTAR)`` feature
- IO: introduced support for ASAR/Envisat product format

**Other changes**

- Removed pinning from several dependencies
- Minor fixes

v1.0.3
------

**Incompatible Features**

- Plugins mechanism for different product formats and readers introduced
- Automatic plugins discovery introduced
- Introduced burst check in ``read_data`` to support latest arepyextras-quality features
- Removed radiometric ``input_quantity`` option from radiometric analysis configuration: it is now always retrieved from the product itself

**Other changes**

- added acquisition mode to protocol implementation for each supported external product format
- IO: introduced specific plugin for Aresys internal Product Folder format


v1.0.2
------

**Additional Features**

- IO: introduced support for COSMO SkyMed product format
- IO: introduced support for RADARSAT 2 product format

**Bug Fixing**

- Fixed computation of ground range step and slant range step in meters for GRD products
- Fixed Point Target Binary reader after Arepytools bugfix

**Other changes**

- Introduced PDM

v1.0.1
------

**Additional Features**

- IO: introduced support for EOS-04 product format
- `Interferometric Analysis`: coherence computation from two co-registered products added
- Added support for input RCS values for PointTargetBinary format
- Documentation updated and improved

**Incompatible Features**

- `Radiometric Analysis`: ``Gamma Profiles`` removed, substituted with ``Average Radiometric Profiles``

**Bug Fixing**

- Removed lines/samples ordering reference from NovaSAR-1 product format implementation

**Other changes**

- Unittest coverage improved
- Theoretical RCS computation improved
- Improved point target analysis graphical output points selection to match the arepyextras-quality bugfix
- Rosamond corner data converter updated to express azimuth elevation and tilt with the same reference system as surat basin's


v1.0.0
------

**Additional Features**

- Added an automatic analyses detection feature based on intersection of product footprint with a registry of supported locations
- Added an utility to download Ionospheric TEC Maps from NASA/CDDIS archive

**Other changes**

- Improved and extended the .csv template for Point Targets input data
- Global re-organization of the corrections management inside the library
- Integration tests updated and extended


**Bug Fixing**

- Fixed perturbations signs to correct ALE values both in range and azimuth directions
- Incidence angles computation evaluated at target range time instead of mid-range
- Fixed Sentinel-1 mid-swath detection function

v1.0.0.dev2
-----------

**Additional Features**

- `Interferometric Analysis`: added a new module to perform interferometric coherence analysis
- IO: introduced support for SAOCOM product format

**Other changes**

- Removed support for SQLite Point Target internal Database: .csv template-compliant file is the only viable input option
- Minor type hint bugfixing
- Removed unused ``get_acquisition_time`` function form `io.io_manager`


v1.0.0.dev1
-----------

**Additional Features**

- `Radiometric Analysis`: added a new module to perform radiometric analysis and profiles extraction (NESZ, Gamma, Scalloping)
- IO: introduced support for NovaSAR-1 product format
- IO: introduced support for ICEYE product format


v1.0.0.dev0
-----------

**Additional Features**

- IO: introduced support for Sentinel-1 SAFE product format
- IO: introduced support for Aresys internal Product Folder format
- `Point Target Analysis` geodynamics corrections: introduced support for computing solid tides and plate tectonics displacements
- `Point Target Analysis` atmospheric corrections: introduced support for computing ionospheric and tropospheric delays
- `Point Target Analysis` Sentinel-1 specific corrections: introduced support for computing range and azimuth corrections

**Other changes**

- User manual added to project documentation
