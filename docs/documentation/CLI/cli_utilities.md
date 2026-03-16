---
icon: material/powershell
title: "CLI Utilities"
tags:
    - CLI
    - ionosphere
    - troposphere
    - rosamond
    - download
---

# CLI Auxiliary Utilities

Auxiliary CLI utilities have been added to perform secondary tasks that can be useful to the user. The list of available
commands can be accessed by calling:

```bash title="Auxiliary CLI Utilities"
sct auxiliary --help/-h
```

## Convert Rosamond Point Target Dataset

This utility let the user convert a Rosamond Point Target dataset as downloaded from their site into a SCT compliant
Point Target .csv file.

```bash title="Rosamond Point Target Dataset Converter"
sct auxiliary rosamond-pt-converter -s <rosamond_dataset> -d <date> -out <output_dir>
```

## Download of Ionospheric TEC Maps

This utility let the user download the Ionospheric TEC maps from the CDDIS repository using credentials.

```bash title="Ionospheric TEC Maps Downloader"
sct auxiliary iono-downloader -d "date" -c "analysis_center" -e "authentication_cddis_email" -out "output_dir"
```

## Download of Tropospheric VMF3 Products

This utility let the user download the Tropospheric VMF3 products from the VMF3 repository.

```bash title="Tropospheric VMF3 Products Downloader"
sct auxiliary tropo-downloader -d "date" -r "resolution" -out "output_dir"
```
