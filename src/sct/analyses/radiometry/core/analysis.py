# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Radiometric Analysis"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity
from perseo_quality.radiometric_analysis.block_wise.analysis import (
    average_elevation_profiles,
    nesz_profiles,
    scalloping_profiles,
)
from perseo_quality.radiometric_analysis.block_wise.config import RadiometricProfilesConfig
from perseo_quality.radiometric_analysis.custom_dataclasses import RadiometricProfilesOutput

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.configuration.logger import sct_logger
from sct.io.io_manager import InvalidProductType, product_loader


class SupportedRadiometricProfiles(Enum):
    """Supported radiometric profiles analyses"""

    NESZ = "nesz"
    PROFILES = "average_profiles"
    SCALLOPING = "scalloping"


def sct_radiometric_profiles(
    product_path: str | Path,
    analysis_type: SupportedRadiometricProfiles,
    config: RadiometricProfilesConfig,
    output_quantity: SARRadiometricQuantity | None = None,
) -> list[RadiometricProfilesOutput]:
    """Radiometric profiles SCT wrapper.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    analysis_type : SupportedRadiometricProfiles
        type of analysis to perform
    config : RadiometricProfilesConfig
        radiometric profiles configuration
    output_quantity : SARRadiometricQuantity | None, optional
        output SAR radiometric quantity, by default None

    Returns
    -------
    list[RadiometricProfilesOutput]
        list of RadiometricProfilesOutput results dataclass, one for each channel
    """

    product_path = Path(product_path)

    # LOADING PRODUCT
    try:
        product, _ = product_loader(product_path=product_path)
    except InvalidProductType as err:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        raise InvalidProductType from err

    if analysis_type == SupportedRadiometricProfiles.NESZ:
        results = nesz_profiles(product=product, config=config)
    elif analysis_type == SupportedRadiometricProfiles.PROFILES:
        results = average_elevation_profiles(product=product, output_quantity=output_quantity, config=config)
    elif analysis_type == SupportedRadiometricProfiles.SCALLOPING:
        results = scalloping_profiles(product=product, config=config)

    return results


def sct_nesz_analysis(
    product_path: str | Path, config: SCTRadiometricAnalysisConfig | None = None
) -> list[RadiometricProfilesOutput]:
    """SCT Noise Equivalent Sigma-Zero (NESZ) radiometric block-wise analysis.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    config : SCTRadiometricAnalysisConfig | None, optional
        SCT radiometric analysis configuration, by default None

    Returns
    -------
    list[RadiometricProfilesOutput]
        list of RadiometricProfilesOutput results dataclass, one for each channel
    """

    # configuration management
    if config is None:
        # initializing a default configuration
        config = SCTRadiometricAnalysisConfig()

    return sct_radiometric_profiles(
        product_path=product_path, analysis_type=SupportedRadiometricProfiles.NESZ, config=config.base_config
    )


def sct_average_elevation_profile_analysis(
    product_path: str | Path,
    output_quantity: SARRadiometricQuantity,
    config: SCTRadiometricAnalysisConfig | None = None,
) -> list[RadiometricProfilesOutput]:
    """SCT Average Radiometric Elevation Profile block-wise analysis.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    output_quantity : SARRadiometricQuantity
        output SAR radiometric quantity
    config : SCTRadiometricAnalysisConfig | None, optional
        SCT radiometric analysis configuration, by default None

    Returns
    -------
    list[RadiometricProfilesOutput]
        list of RadiometricProfilesOutput results dataclass, one for each channel
    """

    # configuration management
    if config is None:
        # initializing a default configuration
        config = SCTRadiometricAnalysisConfig()

    return sct_radiometric_profiles(
        product_path=product_path,
        output_quantity=output_quantity,
        analysis_type=SupportedRadiometricProfiles.PROFILES,
        config=config.base_config,
    )


def sct_scalloping_analysis(
    product_path: str | Path, config: SCTRadiometricAnalysisConfig | None = None
) -> list[RadiometricProfilesOutput]:
    """SCT Scalloping radiometric block-wise analysis.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    config : SCTRadiometricAnalysisConfig | None, optional
        SCT radiometric analysis configuration, by default None

    Returns
    -------
    list[RadiometricProfilesOutput]
        list of RadiometricProfilesOutput results dataclass, one for each channel
    """

    # configuration management
    if config is None:
        # initializing a default configuration
        config = SCTRadiometricAnalysisConfig()

    return sct_radiometric_profiles(
        product_path=product_path, analysis_type=SupportedRadiometricProfiles.SCALLOPING, config=config.base_config
    )
