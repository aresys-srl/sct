# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test SCT testing module  script"""

from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.testing.run import run_tests

if __name__ == "__main__":
    enable_quality_logger()
    sct_logger.addHandler(ConsoleHandler())
    run_tests(
        registry_path=r"C:\ARESYS_PROJ\sct\test_registry_windows.json",
        output_dir=r"C:\ARESYS_PROJ\sct\scripts\out",
        graphs=False,
    )
