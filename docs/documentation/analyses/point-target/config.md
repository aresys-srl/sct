---
icon: lucide/file-sliders
title: "Configuration"
tags:
    - point target analysis
    - configuration
    - IRF
    - RCS
    - ionosphere
    - troposphere
---

# Analysis Configuration

Point Target Analysis can be heavily configured through the configuration file and deeply customized. Here is a brief
description of the available parameters that can be set.

!!! note "TOML Configuration Section"

    These parameters must be specified in the configuration .toml file under the ``point_target_analysis`` section.

!!! tip "Defaults"

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

## Main Parameters

```toml title="Point Target Analysis section"
[point_target_analysis]
perform_irf = true                 # on/off IRF computation
perform_rcs = true                 # on/off RCS computation
evaluate_pslr = true               # on/off PSLR computation
evaluate_islr = true               # on/off ISLR computation
evaluate_sslr = true               # on/off SSLR computation
evaluate_localization = true       # on/off Localization Errors computation
ale_validity_limits = [100, 50]    # set Absolute Localization Error validity limits in meters [rng, az]
```

??? danger "Validation"

    `ale_validity_limits` actual default value is ``None`` inside the SCT code. It can be specified as an array of two
    ``float`` values representing the ALE limits in meters along range and azimuth directions.

## Corrections

The following parameters can be configured directly under the `point_target_analysis.corrections` section.

```toml title="Corrections subsection"
[point_target_analysis.corrections]
enable_solid_tides_correction = false                # on/off Solid Earth Tides corr.
enable_plate_tectonics_correction = true             # on/off Plate Tectonics corr.
enable_sensor_specific_processing_corrections = true # on/off Sensor specific corr.
enable_ionospheric_correction = false                # on/off Ionospheric corr.
enable_tropospheric_correction = false               # on/off Tropospheric corr.
```

!!! tip "Sections and sub-sections"

    The ``[point_target_analysis]`` section does not need to be explicitly defined in the configuration file for this subsection to work.  
    ``[point_target_analysis.corrections]`` can be defined directly, even if the parent section is omitted.

### Ionosphere

This sub-subsection is used when the ``point_target_analysis.corrections`` ``enable_ionospheric_correction`` flag
is enabled. Just the highlighted rows in the code below **are required** for the code to work.

```toml hl_lines="2 5 6" title="Ionosphere subsection"
[point_target_analysis.corrections]
enable_ionospheric_correction = true           # on/off Ionospheric corr.

[point_target_analysis.corrections.ionosphere]
ionospheric_maps_directory = ""                # path to the tec map directory
ionospheric_analysis_center = "cor"            # analysis center (maps provider)
```

??? danger "Validation"

    ``ionospheric_analysis_center`` and ``ionospheric_tec_inc_angle_method`` map to internal *enum classes* and are validated
    by the schema to match these valid values.
    Here are the possible values:  
    ==ionospheric_analysis_center==: __``cor``__, __``cod``__, __``esa``__, __``esr``__  
    `Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.


### Troposphere

This sub-subsection is used when the ``point_target_analysis.corrections`` ``enable_tropospheric_correction`` flag
is enabled. Just the highlighted rows in the code below **are required** for the code to work.

```toml hl_lines="2 5 6" title="Troposphere subsection"
[point_target_analysis.corrections]
enable_tropospheric_correction = true           # on/off Tropospheric corr.

[point_target_analysis.corrections.troposphere]
tropospheric_maps_directory = ""                # path to the maps directory
tropospheric_map_grid_resolution = "fine"       # maps grid resolution
```

??? danger "Validation"

    ``tropospheric_map_grid_resolution`` maps to an internal *enum class* and is validated by the schema to match the valid values.  
    Here are the possible values:
    ==tropospheric_map_grid_resolution==: __``fine``__, __``coarse``__  

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.

## Advanced Configuration

This subsection cannot be expressed by itself but only through its sub-sections ``irf_parameters`` and ``rcs_parameters``.
This choice has been done to explicitly separate these two configuration categories from the others because changing these
parameters heavily affects the results and can also lead to code errors.

!!! failure "Advanced Configuration"

    The ==__advanced_configuration__== subsection exposes low-level parameters. Changing these values **is not recommended** and
    may cause the software to fail, produce incorrect results, or behave unpredictably if parameters are invalid or
    scientifically unsound.

### IRF Parameters

This sub-subsection is used when the the user wants to access low level parameters affecting the IRF computation algorithm.

```toml title="IRF subsection"
[point_target_analysis.advanced_configuration.irf_parameters]
peak_finding_roi_size = [33, 33]            # roi in pixel where to find the signal peak
analysis_roi_size = [128, 128]              # roi in pixel for processing oversampled image
oversampling_factor = 16                    # processing oversampling factor
zero_doppler_abs_squint_threshold_deg = 1.0 # squint angle threshold below which not considering this effect
masking_method = "peak"                     # masking method for computing IRF quantities
```

??? danger "Validation"

    ``masking_method`` maps to an internal *enum class* and is validated by the schema to match the valid values.  
    Here are the possible values:
    ==masking_method==: __``peak``__, __``resolution``__  

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.

### RCS Parameters

This sub-subsection is used when the the user wants to access low level parameters affecting the RCS computation algorithm.

```toml title="RCS subsection"
[point_target_analysis.advanced_configuration.rcs_parameters]
interpolation_factor = 8           # processing interpolation factor 
roi_dimension = 128                # roi (squared) in pixel for processing image
calibration_factor = 1.0           # rcs calibration factor
resampling_factor = 1.0            # rcs resampling factor
```

> :lucide-circle-chevron-right: Refer to the [API documentation](api.md) to learn more about these values and their meaning.
