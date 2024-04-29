# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Automatic analysis detection and run
------------------------------------
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum
from itertools import product
from pathlib import Path

import arepyextras.quality.core.custom_logger as clg
from arepyextras.quality.core.custom_logger import CustomFormatterFileHandler
from arepyextras.quality.radiometric_analysis.support import radiometric_profiles_to_netcdf
from jsonschema import validate
from shapely import Polygon

from sct import calibration_sites_registry_schema
from sct.analyses.point_target_analysis import point_target_analysis_with_corrections
from sct.analyses.radiometric_analysis import gamma_analysis, nesz_analysis, scalloping_analysis
from sct.configuration.sct_configuration import SCTConfiguration
from sct.io.io_manager import product_loader


class IntersectionNotFound(RuntimeError):
    """Intersection between product footprint and calibration sites region not found"""


class MultipleIntersectionsFound(RuntimeError):
    """Intersection between product footprint and calibration sites return more than one site"""


class SupportedAutomaticAnalyses(Enum):
    """Supported analyses in automatic mode"""

    POINT_TARGET_ANALYSIS = "point_target_analysis"
    NESZ = "nesz"
    SCALLOPING = "scalloping"
    GAMMA = "gamma"
    INTERFEROMETRY = "interferometry"


# instantiating logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())


@dataclass
class CalibrationSite:
    """Calibration Site representation"""

    name: str
    description: str
    region: Polygon
    supported_analyses: list[str]
    reference_file: Path | None = None

    @classmethod
    def from_dict(cls, val: dict) -> CalibrationSite:
        """Creating a CalibrationSite from a dict representing this dataclass.

        Parameters
        ----------
        arg : dict
            dict representing this dataclass

        Returns
        -------
        CalibrationSite
            CalibrationSite dataclass initialized from input dictionary
        """
        key = list(val.keys())[0]
        lat_bound = val[key]["latitude_boundaries_deg"]
        lon_bound = val[key]["longitude_boundaries_deg"]
        region_corners = list(product(lat_bound, lon_bound))
        ref_file = val[key]["reference_dataset"] if "reference_dataset" in val[key].keys() else None
        return cls(
            name=key,
            description=val[key]["description"],
            region=Polygon(region_corners),
            supported_analyses=val[key]["supported_analyses"],
            reference_file=ref_file,
        )


def _load_json_registry(path: str | Path) -> dict:
    """Loading input calibration sites registry json file and validating against its schema.

    Parameters
    ----------
    path : str | Path
        path to the input calibration sites .json file

    Returns
    -------
    dict
        dice representing the input registry
    """

    with open(calibration_sites_registry_schema, "r", encoding="utf-8") as f:
        json_schema = json.load(f)

    with open(path, "r", encoding="utf-8") as f:
        cal_sites = json.load(f)

    validate(cal_sites, json_schema)

    return cal_sites


def detect_calibration_site(calibration_areas: str | Path, product_footprint: Polygon) -> CalibrationSite:
    """Detecting the Calibration Site of interest based on product's footprint intersection with the site bounding box.

    Parameters
    ----------
    calibration_areas : str | Path
        calibration area registry, compliant with the internal schema
    product_footprint : Polygon
        footprint of the input product

    Returns
    -------
    CalibrationSite
        Calibration Site of interest
    """

    # loading the reference calibration sites config file
    cal_sites = _load_json_registry(path=calibration_areas)

    calibration_sites = [CalibrationSite.from_dict({k: v}) for k, v in cal_sites["regions"].items()]

    intersections = [c for c in calibration_sites if product_footprint.intersects(c.region)]

    if not intersections:
        raise IntersectionNotFound("Intersection of product footprint with calibration sites registry not found")

    if len(intersections) > 1:
        raise MultipleIntersectionsFound("More than one site intersecting the scene footprint")

    return intersections[0]


def sct_automatic_analysis(
    product_path: str | Path,
    output_dir: str | Path,
    calibration_sites_registry: str | Path,
    graphs: bool = False,
    external_orbit: str | Path | None = None,
    config: SCTConfiguration | None = None,
) -> None:
    """Automatic analysis mode for SCT tool.

    Parameters
    ----------
    product_path : str | Path
        path to the input product
    output_dir : str | Path
        path ton the output directory where to save results
    calibration_sites_registry : str | Path
        calibration sites registry .json file for automatic analysis dispatching
    graphs : bool, optional
        enabling flag to perform graphs and plots, by default False
    external_orbit : str | Path | None, optional
        external orbit file, if needed, by default None
    config : SCTConfiguration | None, optional
        SCT configuration, by default None
    """

    output_dir = Path(output_dir)
    product_path = Path(product_path)

    # checking config
    config = config or SCTConfiguration()

    log.info(f"Launching SCT automatic analysis on product {product_path}")

    # saving log file to output folder
    if config.general.save_log:
        logging_file_handler = logging.FileHandler(output_dir.joinpath("sct_automatic_analysis.log"))
        logging_file_handler.setFormatter(CustomFormatterFileHandler())
        log.addHandler(logging_file_handler)

    # saving configuration used to output folder as .toml file
    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_dir.joinpath("analysis_config.toml"), selected="radiometry")

    # load product
    sar_product, _, _ = product_loader(product_path=product_path, external_orbit=external_orbit)

    # recovering product footprint and find intersecting calibration site
    cal_site = detect_calibration_site(
        calibration_areas=calibration_sites_registry, product_footprint=sar_product.footprint
    )
    log.info(f"Calibration site intersected: {cal_site.name}")
    log.info(f"Available analyses {cal_site.supported_analyses}")

    for analysis in cal_site.supported_analyses:
        if SupportedAutomaticAnalyses(analysis.lower()) == SupportedAutomaticAnalyses.POINT_TARGET_ANALYSIS:
            results_df, graphs_data = point_target_analysis_with_corrections(
                product_path=product_path,
                external_target_source=cal_site.reference_file,
                external_orbit_path=external_orbit,
                config=config.point_target_analysis,
            )
            # saving results to csv file
            results_df.to_csv(output_dir.joinpath("point_target_analysis_results.csv"), index=False)
            if graphs:
                from sct.analyses.graphical_output import sct_pta_graphs

                sct_pta_graphs(graphs_data=graphs_data, results_df=results_df, output_dir=output_dir)
        else:
            if SupportedAutomaticAnalyses(analysis.lower()) == SupportedAutomaticAnalyses.NESZ:
                tag = "nesz"
                rad_results = nesz_analysis(product_path=product_path, config=config.radiometric_analysis)
            elif SupportedAutomaticAnalyses(analysis.lower()) == SupportedAutomaticAnalyses.GAMMA:
                tag = "nesz"
                rad_results = gamma_analysis(product_path=product_path, config=config.radiometric_analysis)
            elif SupportedAutomaticAnalyses(analysis.lower()) == SupportedAutomaticAnalyses.SCALLOPING:
                tag = "scalloping"
                rad_results = scalloping_analysis(product_path=product_path, config=config.radiometric_analysis)

            for res in rad_results:
                # saving results file to netCDF
                radiometric_profiles_to_netcdf(data=res, out_path=output_dir, tag=tag)
                if graphs:
                    from arepyextras.quality.radiometric_analysis.graphical_output import radiometric_2D_hist_plot

                    radiometric_2D_hist_plot(
                        data=res,
                        out_dir=output_dir,
                        title=f"{tag.upper()} Profiles {res.swath} {res.polarization.name}",
                    )
