---
icon: lucide/file-sliders
title: "Configuration"
tags:
    - radiometric analysis
    - nesz
    - rain forest
    - radiometric profiles
    - scalloping
    - configuration
---

# Analysis Configuration

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

!!! note "TOML Configuration Section"

    These parameters must be specified in the configuration .toml file under the ``radiometric_analysis`` section.

!!! tip "Defaults"

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

## Main Parameters

```toml title="Radiometric Analysis section"
[radiometric_analysis]
input_type = "beta_nought"              # input radiometric quantity
azimuth_block_size = 2000               # scene partitioning block size in pixel along azimuth
range_pixel_margin = 150                # margin in pixel to exclude near and far range from profile
```

??? danger "Validation"

    ``input_type`` maps to an internal *enum class* and is validated by the schema to match the valid values.
    Here are the possible values:  
    ==input_type==: __``beta_nought``__, __``sigma_nought``__, __``gamma_nought``__  

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.

## Advanced Configuration

This sub-section cannot be expressed by itself but only through its sub-sections `profile_extraction_parameters` and `histogram_parameters`.
This choice has been done to explicitly separate these two configuration categories from the others because changing these
parameters heavily affects the results.

`radiometric_analysis` **is not required to be defined in the configuration file** for this sub-section to work.

!!! failure "Advanced Configuration"

    The ==__advanced_configuration__== subsection exposes low-level parameters. Changing these values **is not recommended** and
    may cause the software to fail, produce incorrect results, or behave unpredictably if parameters are invalid or
    scientifically unsound.

### Profile Extraction Parameters

This sub-subsection is used when the the user wants to access low level parameters affecting the radiometric profiles
extraction algorithm.

```toml title="Profile Extraction Parameters subsection"
[radiometric_analysis.advanced_configuration.profile_extraction_parameters]
outlier_removal = false                     # enabling/disabling outlier removal filter
smoothening_filter = false                  # enabling/disabling smoothening filter
filtering_kernel_size = [11, 11]            # size of the smoothening filter kernel
outliers_kernel_size = [5, 5]               # size of the outliers removal kernel
outliers_percentile_boundaries = [20, 90]   # outliers percentile boundaries to be preserved
```

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.

#### River Masking Parameters

This is a sub-subsection of the previous one. It can be specified when the the user wants to configure the river masking algorithm
that can be used to mask out the river pixels and improve the quality of the analysis for example in Rain Forest products.

```toml title="River Masking Parameters subsection"
[radiometric_analysis.advanced_configuration.profile_extraction_parameters.river_masking]
river_masking_mode = "FULL"                     # masking mode, it can be FULL or FAST
local_stats_window = 10                         # side length of the local stats window
backscatter_threshold_percentile = 25           # signal percentile threshold to remove low level areas
cv_lower_threshold_percentile = 20              # coefficient of variation lower threshold percentile
cv_upper_threshold_percentile = 90              # coefficient of variation upper threshold percentile
morph_opening_radius = 3                        # morphological cleaning radius to remove small objects
min_river_area_px_percentile = 99               # threshold on blobs area to be removed
region_grow_iterations = 13                     # mask region growth iterations
relaxed_backscatter_threshold_percentile = 35   # threshold for mask blobs growth
```

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.

### 2D Histograms Parameters

This sub-subsection is used when the the user wants to access low level parameters affecting the computation algorithm
of the 2D histograms.

```toml title="2D Histograms Parameters subsection"
[radiometric_analysis.advanced_configuration.histogram_parameters]
x_bins_step = 10            # number of bins along the x axis [look angles/azimuth times]
y_bins_num = 101            # number of bins along the y axis [intensity (dB)]
y_bins_center_margin = 3    # extent of the intensity graph (in dB) from the central bin
```

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.
