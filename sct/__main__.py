# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Main CLI script"""
import logging

import arepyextras.quality.configuration.custom_logger as clg


def main():
    """Main function to launch the python SQT CLI program"""
    # setup custom logger
    log = logging.getLogger("arepyextras.quality")
    log.setLevel("DEBUG")
    log.addHandler(clg.MyHandler())


if __name__ == "__main__":
    main()
