# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Point Target Analysis commands.
-----------------------------------
"""

import sys
from pathlib import Path

import click

import sct.analyses.point_target_analysis as pta
from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


@click.command(name="target-analysis")
@common.input_product_option
@common.output_directory_option
@click.option(
    "--external-orbit",
    "-eo",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the external orbit file",
)
@common.input_point_target_option
@common.generate_graph_option
@common.share_config
def target_analysis(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    external_orbit: Path,
    point_target_source: Path,
    graphs: bool,
) -> None:
    """Point Target Analysis (IRF, Localization and RCS)."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_pta_analysis.log")) if config.general.save_log else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    if external_orbit:
        sct_logger.info(f"External orbit: {external_orbit}")
    else:
        sct_logger.info("No external orbit provided, using orbit from product.")
    sct_logger.info(f"Point targets: {point_target_source}")
    sct_logger.info(f"Output folder: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Point Target Analysis")

    target_analysis_implementation(
        product=product,
        external_orbit=external_orbit,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@common.log_elapsed_time("Point Target Analysis")
def target_analysis_implementation(
    product: Path,
    external_orbit: Path | None,
    point_target_source: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the point target analysis command."""
    if graphs:
        try:
            from sct.analyses.graphical_output import sct_pta_graphs

        except ImportError:
            sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
            sys.exit(1)

    results, graphs_data = pta.point_target_analysis_with_corrections(
        product_path=product,
        external_orbit_path=external_orbit,
        external_target_source=point_target_source,
        config=config.point_target_analysis,
    )

    results.to_csv(output_directory.joinpath("point_target_analysis_results.csv"), index=False)

    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_directory.joinpath("analysis_config.toml"), selected="point_target")

    if graphs:
        sct_logger.info("Plotting graphs...")
        graphs_out_dir = output_directory.joinpath("graphs")
        graphs_out_dir.mkdir(exist_ok=True)
        sct_pta_graphs(graphs_data=graphs_data, results_df=results, output_dir=graphs_out_dir)
