.. _sct_analyses:

Analyses and Features
=====================

.. toctree::
    :hidden:
    :maxdepth: 2

    pt/index
    ra/index
    interf/index
    spectra/index
    notch/index
    ptar/index

Here is reported a list of implemented features and available analyses for SCT:

- :ref:`Point Target Analysis<sct_pta>`
- :ref:`Radiometric Analysis<sct_ra>` (NESZ, Average Elevation Profiles, Scalloping)
- :ref:`Interferometric Analysis<sct_interf>`
- :ref:`Spectral Analysis<sct_spectra>`
- :ref:`Point Target Ambiguity Ratio (PTAR)<sct_ptar>`

The SCT framework uses a **plugin-based architecture** for analyses and all analyses are automatically discovered and
registered at runtime.

Architecture Summary
--------------------

Each analysis:

1. Lives under:

    .. code-block:: text

        sct/analyses/<analysis_name>/

2. Registers itself in its ``__init__.py``

3. Is auto-loaded by :py:func:`sct.analyses.load_analyses`

4. Its CLI command is attached to the root :py:mod:`sct.cli.cli` CLI group


Directory Structure
-------------------

Example:

.. code-block:: text

    sct/
        analyses/
            __init__.py
            <analysis_name>/
                __init__.py
                cli.py
                main.py
                config.py
