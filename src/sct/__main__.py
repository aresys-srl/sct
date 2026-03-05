# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Main CLI script"""

from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger


def main() -> None:
    """Main function to launch the Python SQT CLI program"""

    # setup custom logger
    sct_logger.setLevel("INFO")
    sct_logger.addHandler(ConsoleHandler())
    enable_quality_logger()

    from sct.cli.cli import app

    app()


if __name__ == "__main__":
    main()
