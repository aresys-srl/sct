# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Radiometric Profiles Analysis
-----------------------------
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from arepyextras.quality.radiometric_analysis.analysis import gamma_profiles, nesz_profiles, scalloping_profiles
from arepyextras.quality.radiometric_analysis.config import RadiometricProfilesConfig
from arepyextras.quality.radiometric_analysis.custom_dataclasses import RadiometricProfilesOutput

from sct.configuration.sct_configuration import SCTRadiometricAnalysisConfig
from sct.io.io_manager import product_loader

# syncing with logger
log = logging.getLogger("quality_analysis")


class SupportedRadiometricProfiles(Enum):
    """Supported radiometric profiles analyses"""

    NESZ = "nesz"
    GAMMA = "gamma"
    SCALLOPING = "scalloping"


def sct_radiometric_profiles(
    product_path: str | Path, analysis_type: SupportedRadiometricProfiles, config: RadiometricProfilesConfig
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

    Returns
    -------
    list[RadiometricProfilesOutput]
        list of RadiometricProfilesOutput results dataclass, one for each channel
    """

    product_path = Path(product_path)

    # LOADING PRODUCT
    product, _, _ = product_loader(product_path=product_path)

    if analysis_type == SupportedRadiometricProfiles.NESZ:
        results = nesz_profiles(product=product, config=config)
    elif analysis_type == SupportedRadiometricProfiles.GAMMA:
        results = gamma_profiles(product=product, config=config)
    elif analysis_type == SupportedRadiometricProfiles.SCALLOPING:
        results = scalloping_profiles(product=product, config=config)

    return results


def nesz_analysis(
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


def gamma_analysis(
    product_path: str | Path, config: SCTRadiometricAnalysisConfig | None = None
) -> list[RadiometricProfilesOutput]:
    """SCT Gamma-Zero radiometric block-wise analysis.

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
        product_path=product_path, analysis_type=SupportedRadiometricProfiles.GAMMA, config=config.base_config
    )


def scalloping_analysis(
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
