# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test point target analysis script"""

import logging
from pathlib import Path

import arepyextras.quality.core.custom_logger as clg
import arepyextras.quality.point_targets_analysis.graphical_output as ptgpo

from sct.analyses import point_target_analysis as pta
from sct.configuration.sct_configuration import SCTConfiguration

# setup custom logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())

# insert proper working dir path here
working_dir = Path("...")
# path to the product to be analyzed inside of the working dir
product_path = working_dir.joinpath("...")
# external point target .csv file path
ext_target = working_dir.joinpath("...")
# path to the configuration, if any
configuration_path = working_dir.joinpath("config.toml")

# output folder generation
output_fldr = working_dir.joinpath("output")
output_fldr.mkdir(exist_ok=True)


if __name__ == "__main__":
    # defining output file for logger dump
    logging_file_handler = logging.FileHandler(
        output_fldr.joinpath("sct_pta_analysis.log")
    )
    logging_file_handler.setFormatter(clg.CustomFormatterFileHandler())
    log.addHandler(logging_file_handler)

    # test config
    if configuration_path.is_file():
        test_config = SCTConfiguration.from_toml(configuration_path)
    else:
        test_config = SCTConfiguration()  # default config

    # executing point target analysis
    out, out_graph = pta.point_target_analysis_with_corrections(
        product_path=product_path,
        external_target_source=ext_target,
        config=test_config.point_target_analysis,
    )

    # saving results
    out.to_csv(
        Path(output_fldr).joinpath("point_target_analysis_results.csv"), index=False
    )

    out_graph_fldr = output_fldr.joinpath("pta_graphs")
    out_graph_fldr.mkdir(exist_ok=True)
    for item in out_graph:
        try:
            data_val = out.query(
                "target_name == @item.target & channel == @item.channel & "
                + "burst == @item.burst & swath == @item.swath & "
                + "polarization == @item.polarization.value"
            ).to_dict("records")[0]
            label = (
                f"target_{data_val['target_name']}_{data_val['swath']}_"
                + f"polarization_{data_val['polarization'].replace('/', '')}_"
                + f"{data_val['product_type']}_b{data_val['burst']}"
            )
            ptgpo.irf_graphs(
                data_graph=item.irf,
                data_values=data_val,
                label=label,
                out_dir=out_graph_fldr,
            )
            ptgpo.rcs_graphs(
                data_graph=item.rcs,
                label=label,
                out_dir=out_graph_fldr,
            )
        except Exception:
            continue
    log.info("Graphs done.")
