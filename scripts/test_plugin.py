# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test SCT plugins import"""

import logging

from sct.configuration.logger import ConsoleHandler, sct_logger

if __name__ == "__main__":

    sct_logger.addHandler(ConsoleHandler())
    sct_logger.setLevel(logging.INFO)

    from sct.plugins import available_plugins
    print(available_plugins)
