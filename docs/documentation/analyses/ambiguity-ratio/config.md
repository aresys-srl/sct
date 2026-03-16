---
icon: lucide/file-sliders
title: "Configuration"
tags:
    - ambiguity ratio analysis
    - ptar
    - configuration
---

# Analysis Configuration

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

!!! note "TOML Configuration Section"

    These parameters must be specified in the configuration .toml file under the ``ambiguity_ratio_analysis`` section.

!!! tip "Defaults"

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

## Main Parameters

```toml title="Ambiguity Ratio Analysis section"
[ambiguity_ratio_analysis]
interpolation_factor = 8                   # ROI interpolation factor
cropping_size = [128, 128]                 # ROI size to be analyzed
```

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.
