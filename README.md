# SAR Calibration Toolbox (SCT)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://python.org)
[![SCT CI](https://github.com/aresys-srl/sct/actions/workflows/sct.yml/badge.svg)](https://github.com/aresys-srl/sct/actions/workflows/sct.yml)

**SAR Calibration Toolbox (SCT)** is the official Aresys Python toolbox for SAR quality assessment and data processing.
This software provides several features to perform quality analysis of SAR L1 products (both SLC and GRD).

SCT is based on [**PERSEO**](https://github.com/aresys-srl/perseo)
([docs](https://aresys-srl.github.io/perseo)), the Aresys modular Python framework for SAR product handling, processing, and analysis. It also integrates plugins using the [**stevedore**](https://docs.openstack.org/stevedore/latest/) library.

SCT provides a comprehensive set of analyses for SAR product quality assessment:

- **Point Target Analysis** — IRF metrics, RCS estimation, localization errors
- **Radiometric Analysis** — NESZ, Rain Forest, Average Elevation Profiles, Scalloping
- **Interferometric Coherence Analysis** — interferometric coherence intensity and histograms
- **Spectral Analysis** — point & distributed target spectral content in frequency domain
- **Elevation Notch Analysis** — antenna pointing estimation
- **Target Ambiguity Ratio (PTAR/DTAR)** — point target and distributed ambiguity ratio computation

Supported input products include:

- Sentinel-1 (A/B/C/D) SAFE format
- ICEYE
- NovaSAR-1
- Radarsat-2
- Envisat/ERS
- SAOCOM
- COSMO SkyMed
- EOS-04
- STRIX

and more through a [plugin-based architecture](https://aresys-srl.github.io/sct_plugins/).

## Installation

This package is available on [PyPI](https://pypi.org/project/sct/) and can be installed with `pip`:

```bash
pip install sct[graphs]
```

The `[graphs]` extra enables graphical output (`matplotlib`).

> [!IMPORTANT]
> After installing SCT, install the plugin corresponding to the product format you want to process. The base SCT package does not include any plugins by default.

## Documentation

- **SCT documentation**: [https://aresys-srl.github.io/sct](https://aresys-srl.github.io/sct)
- **SCT Plugins documentation**: [https://aresys-srl.github.io/sct_plugins](https://aresys-srl.github.io/sct_plugins)
- **PERSEO documentation**: [https://aresys-srl.github.io/perseo](https://aresys-srl.github.io/perseo)

## Related Repositories

| Repository | Description | Documentation |
|---|---|---|
| [aresys-srl/sct_plugins](https://github.com/aresys-srl/sct_plugins) | SCT input product format plugins | [docs](https://aresys-srl.github.io/sct_plugins/) |
| [aresys-srl/perseo](https://github.com/aresys-srl/perseo) | Python Ecosystem for Remote Sensing & Earth Observation | [docs](https://aresys-srl.github.io/perseo/) |

## Contributing

Contributions are welcome! If you encounter a bug, have a feature request, or want to contribute code:

- **Report bugs & request features**: open an issue on [GitHub](https://github.com/aresys-srl/sct/issues). Include a clear description, steps to reproduce, and your environment details.
- **Submit changes**: fork the repository, create a feature branch, and open a pull request. Ensure your code passes the existing linting and test suite.
- **Questions**: use GitHub Discussions for general questions and discussions.

## License

This project is licensed under the MIT License.

Copyright &copy; 2026-present Aresys S.r.L. <info@aresys.it>
