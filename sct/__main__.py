# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Main CLI script"""

import sys

from sct.configuration.logger import ConsoleHandler, sct_logger


def main():
    """Main function to launch the python SQT CLI program"""
    # setup custom logger
    sct_logger.addHandler(ConsoleHandler())
    sct_logger.setLevel("INFO")

    try:
        from sct.cli.sct_cli import sct_analysis

        sct_analysis(max_content_width=120)

    except ImportError:
        print('Install cli requirements "pip install sct[cli]"')
        sys.exit(1)


if __name__ == "__main__":
    main()
