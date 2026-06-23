---
icon: lucide/history
title: "Changelog"
tags:
    - changelog
    - release notes
---

# Changelog

## v3.0.0

First official public release on PyPI.

**Additional Features**

- Adding Elevation Notch Analysis feature and corresponding CLI command
- Adding Distributed and Point Target Spectral Analyses and corresponding CLI command
- Adding Distributed and Point Target Ambiguity Ratio Analyses and corresponding CLI command
- Radiometric Analysis: adding configuration for `River Masking` in Rain Forest analysis
- Radiometric Analysis: adding Rain Forest full implementation function
- Added support for SARCalNet calibration sites survey json files

**Bug Fixing**

- Fixing minor bugs
- Fixing RCS Error computation from PERSEO Quality by subtracting the Theoretical RCS
- Fixed bug in Rosamond Corner Reflector conversion to SCT compliant Point Target .csv dataset format

**Other Changes**

- Plugins mechanism for different product formats and readers introduced using `stevedore`
- Automatic plugins discovery introduced
- Unit testing framework changed to pytest
- Increasing unit test code coverage
- Command Line Interface: switched from Click to Typer
- Command Line Interface: moved secondary CLI utilities commands to ``auxiliary`` CLI group
- Code refactoring to support multiple analyses as self-registering plugins
- Documentation updated, switched from `sphinx` to `zensical` and `mkdocstrings`
- Dropping support for Python 3.10
- Changing package layout to ``src``
- Changed Arepyextras-* and Arepytools dependencies to PERSEO python framework
- Removed automatic analysis module

## v2.1.1

...

## v2.1.0

...

## v2.0.0

First official release. Not public on PyPI.
