# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Main CLI script"""

from sct.configuration.logger import ConsoleHandler, sct_logger


def main():
    """Main function to launch the python SQT CLI program"""
    # setup custom logger
    sct_logger.addHandler(ConsoleHandler())
    sct_logger.setLevel("INFO")

    from sct.cli.cli import sct_analysis

    sct_analysis(max_content_width=120)


if __name__ == "__main__":
    main()
