# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CDDIS Archive Data Downloader Utility
-------------------------------------
"""
from ftplib import FTP_TLS
from pathlib import Path

FTP_HOST = "gdc.cddis.eosdis.nasa.gov"


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
    ftps.retrbinary("RETR " + filename, open(output_file, "wb").write)
    return output_file


if __name__ == "__main__":
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    # out_file = cddis_downloader(download_link, out_dir)
    # print(out_file)
    prova = cddis_ftps_archive_downloader(
        directory="gnss/products/ionex/2024/009",
        filename="JPL0OPSFIN_20240090000_01D_02H_GIM.INX.gz",
        email="giorgio.parma@aresys.it",
        out_dir=out_dir,
    )
    print(prova)
