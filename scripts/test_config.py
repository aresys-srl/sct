# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SAFE product reader testing script"""

from sct.configuration.sct_default_configuration import SCTConfiguration

if __name__ == "__main__":
    config = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\prova.toml"
    config_toml = SCTConfiguration.from_toml(config)

    out_file = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\dumped.toml"
    config_toml.dump_to_toml(
        out_file=out_file,
    )

    config_reloaded = SCTConfiguration.from_toml(out_file)
    assert config_toml == config_reloaded

    pass
