# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Web Scraping Base Utilities
---------------------------
"""

import time
from pathlib import Path
from typing import Union


def download_watchdog(directory: Union[str, Path], n_files: int, timeout: int = 10) -> bool:
    """Wait for downloads to finish with a specified timeout.

    Parameters
    ----------
    directory : Union[str, Path]
        path to the folder where the files will be downloaded
    n_files : int
        wait for the expected number of files
    timeout : int, optional
        seconds to wait until timing out, by default 10

    Returns
    -------
    bool
        True if download is successful, False if not
    """
    directory = Path(directory)
    files = set([f.name for f in directory.iterdir()])
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        new_files = set([f.name for f in directory.iterdir()]) - files
        # check if the number of files is different from the expected one
        if n_files and len(new_files) != n_files:
            dl_wait = True

        # check if there is a partially downloaded file, meaning download is not yet completed
        for fname in new_files:
            if fname.endswith(".crdownload") or fname.endswith(".tmp"):
                dl_wait = True

        seconds += 1

    if seconds == timeout:
        return False
    return True
