# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Main CLI script"""
import logging
import sys

import arepyextras.quality.core.custom_logger as clg


def main():
    """Main function to launch the python SQT CLI program"""
    # setup custom logger
    log = logging.getLogger("quality_analysis")
    log.setLevel("INFO")
    log.addHandler(clg.MyHandler())

    try:
        from sct.cli.sct_cli import sct_analysis

        sct_analysis()

    except ImportError:
        print('Install cli requirements "pip install sct[cli]"')
        sys.exit(1)


if __name__ == "__main__":
    main()
