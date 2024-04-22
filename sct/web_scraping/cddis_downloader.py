# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CDDIS Archive Data Downloader Utility
-------------------------------------
"""
from ftplib import FTP_TLS, error_perm
from pathlib import Path

FTP_HOST = "gdc.cddis.eosdis.nasa.gov"


class InvalidCDDISRequest(error_perm):
    """Invalid e-mail authentication on CDDIS platform or file requested not found"""


def cddis_ftps_archive_downloader(directory: str, filename: str, email: str, out_dir: str | Path) -> Path:
    """Utility to download data from the CDDIS products archive.

    Parameters
    ----------
    directory : str
        directory on the server where to find the product to be downloaded
    filename : str
        name of the product to be downloaded
    email : str
        user e-mail for authentication purposes
    out_dir : str | Path
        output directory where to save the downloaded file

    Returns
    -------
    Path
        Path to the downloaded file on disk
    """

    out_dir = Path(out_dir)
    output_file = out_dir.joinpath(filename)

    ftps = FTP_TLS(host=FTP_HOST, timeout=15)
    ftps.login(user="anonymous", passwd=email)
    ftps.prot_p()
    ftps.cwd(directory)
    try:
        with open(output_file, "wb") as f_out:
            ftps.retrbinary("RETR " + filename, f_out.write)
        return output_file
    except error_perm as err:
        if output_file.exists():
            output_file.unlink()
        raise InvalidCDDISRequest("Check e-mail provided for authentication or if requested file is available") from err
    finally:
        ftps.close()
