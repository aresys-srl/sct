# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test point target analysis script"""

from pathlib import Path

import perseo_quality.point_targets_analysis.graphical_output as ptgpo

from sct.analyses import point_target as pta
from sct.configuration.logger import SCTFileHandler, enable_quality_logger, sct_logger
from sct.configuration.config import SCTConfiguration

out_fldr = Path(r"C:\Users\giorgio.parma\Desktop\temporary_outputs")

# setup custom logger
file_handler = SCTFileHandler(out_fldr.joinpath("sct_pta_analysis.log"))
sct_logger.addHandler(file_handler)
enable_quality_logger(file_handler=file_handler)
sct_logger.setLevel("INFO")

if __name__ == "__main__":
    # products
    # prod = r"C:\Users\giorgio.parma\Aresys_DATA\quality_data\demo_topsar\SLC"
    prod = r"C:/Users/giorgio.parma/Aresys_DATA/sct_data/sentinel1/SLC_23.SAFE"

    # external orbits
    ext_orbit = None

    # external target source
    ext_target = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\surat_basin_data.csv"
    # ext_target = r"C:\Users\giorgio.parma\Aresys_DATA\quality_data\demo_topsar\PointTargetsBinary"

    # # test config
    # test_config = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\config_etad.toml"
    # test_config = SCTConfiguration.from_toml(test_config)
    test_config = SCTConfiguration()
    # test_config.point_target_analysis.enable_plate_tectonics_correction = False
    # test_config.point_target_analysis.enable_solid_tides_correction = False

    # executing point target analysis
    out, out_graph = pta.point_target_analysis_with_corrections(
        product_path=prod,
        external_orbit_path=ext_orbit,
        external_target_source=ext_target,
        external_corrections_product=r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\ETAD_23.SAFE",  # ETAD
        config=test_config.point_target_analysis,
    )

    # saving results
    out.to_csv(Path(out_fldr).joinpath("point_target_analysis_results.csv"), index=False)

    sct_logger.info("Plotting Graphs...")
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
    sct_logger.info("Graphs done.")
