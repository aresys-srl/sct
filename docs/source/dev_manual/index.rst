Development Guide
=================

.. toctree::
   :hidden:
   :maxdepth: 2

   create_analysis
   create_plugin


This section of the documentation provides general guidance for developers who want to extend this package.
It focuses on two common development tasks:

- Implementing new analysis modules
- Adding support for new input formats through reader plugins

The goal of this section is to explain the overall architecture of the package and provide practical instructions for
integrating new functionality while maintaining consistency with the existing codebase.

The package is designed to be modular and extensible. Analyses are implemented as independent components that operate on
standardized internal data structures, while input formats are handled through a plugin-based reader system, exploiting **stevedore**.
This separation allows developers to introduce new analyses without worrying about input file structure, and to support
new file formats without modifying the core analysis logic.

.. note::

   These guides are intended for contributors who are already familiar with Python and basic software development practices.
