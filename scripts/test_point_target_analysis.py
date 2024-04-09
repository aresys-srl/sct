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

out_fldr = Path(r"C:\Users\giorgio.parma\Desktop\temporary_outputs\wv_pta\sct_reports\report_WV_DT059DA1")
logging_file_handler = logging.FileHandler(out_fldr.joinpath("sct_pta_analysis.log"))
logging_file_handler.setFormatter(clg.CustomFormatterFileHandler())
log.addHandler(logging_file_handler)

if __name__ == "__main__":
    # products
    prod = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\wv_pta\WV_DT059DA1\iSLC_RgCorr"

    # external orbits
    ext_orbit = None
    # ext_orbit = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\S1A_OPER_AUX_RESORB_OPOD_20190108T123406_V20190108T070200_20190108T101930.EOF"

    # external target source
    ext_target = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\reference_datasets\surat_basin_data.csv"

    # test config
    test_config = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\wv_pta\config.toml"
    test_config = SCTConfiguration.from_toml(test_config)

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
            data_val = out.query("target_name == @item.target & channel == @item.channel").to_dict("records")[0]
            label = (
                f"target_{data_val['target_name']}_{data_val['swath']}_"
                + f"polarization_{data_val['polarization'].replace('/','')}_{data_val['product_type']}"
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
