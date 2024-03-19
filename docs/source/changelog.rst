Changelog
=========

v1.0.0.dev2
----------

**Additional Features**

- `Interferometric Analysis`: added a new module to perform interferometric coherence analysis
- IO: introduced support for SAOCOM product format

**Other changes**

- Removed support for SQLite Point Target internal Database: .csv template-compliant file is the only viable input option
- Minor type hint bugfixing
- Removed unused ``get_acquisition_time`` function form `io.io_manager`


v1.0.0.dev1
----------

**Additional Features**

- `Radiometric Analysis`: added a new module to perform radiometric analysis and profiles extraction (NESZ, Gamma, Scalloping)
- IO: introduced support for NovaSAR-1 product format
- IO: introduced support for ICEYE product format


v1.0.0.dev0
----------

**Additional Features**

- IO: introduced support for Sentinel-1 SAFE product format
- IO: introduced support for Aresys internal Product Folder format
- `Point Target Analysis` geodynamics corrections: introduced support for computing solid tides and plate tectonics displacements
- `Point Target Analysis` atmospheric corrections: introduced support for computing ionospheric and tropospheric delays
- `Point Target Analysis` Sentinel-1 specific corrections: introduced support for computing range and azimuth corrections

**Other changes**

- User manual added to project documentation
