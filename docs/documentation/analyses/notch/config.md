---
icon: lucide/file-sliders
title: "Configuration"
tags:
    - elevation notch analysis
    - configuration
---

# Analysis Configuration

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

!!! note "TOML Configuration Section"

    These parameters must be specified in the configuration .toml file under the ``elevation_notch_analysis`` section.

!!! tip "Defaults"

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

## Main Parameters

```toml title="Elevation Notch Analysis section"
[elevation_notch_analysis]
azimuth_block_size = 2500               # scene partitioning block size in pixel along azimuth
range_pixel_margin = 100                # margin in pixel to exclude near and far range from profile
```

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.
