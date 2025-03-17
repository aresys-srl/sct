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

out_fldr = Path(r"C:\Users\giorgio.parma\Desktop\temporary_outputs")
logging_file_handler = logging.FileHandler(out_fldr.joinpath("sct_pta_analysis.log"))
logging_file_handler.setFormatter(clg.CustomFormatterFileHandler())
log.addHandler(logging_file_handler)

if __name__ == "__main__":
    # products
    # prod = r"C:\Users\giorgio.parma\Aresys_DATA\quality_data\demo_topsar\SLC"
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\SLC_23.SAFE"

    # external orbits
    ext_orbit = None
    # ext_orbit = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\S1A_OPER_AUX_RESORB_OPOD_20190108T123406_V20190108T070200_20190108T101930.EOF"

    # external target source
    ext_target = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\surat_basin_data.csv"
    # ext_target = r"C:\Users\giorgio.parma\Aresys_DATA\quality_data\demo_topsar\PointTargetsBinary"

    # # test config
    test_config = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\config_etad.toml"
    test_config = SCTConfiguration.from_toml(test_config)
    # test_config = SCTConfiguration()

    # executing point target analysis
    out, out_graph = pta.point_target_analysis_with_corrections(
        product_path=prod,
        external_orbit_path=ext_orbit,
        external_target_source=ext_target,
        config=test_config.point_target_analysis,
    )

    # saving results
    out.to_csv(Path(out_fldr).joinpath("point_target_analysis_results.csv"), index=False)

    out_graph_fldr = out_fldr.joinpath("pta_graphs")
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
                + f"polarization_{data_val['polarization'].replace('/','')}_"
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
