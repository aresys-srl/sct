# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Automating python testing, formatting and distribution of SCT module"""

import glob
import os
import shutil
import sys
from pathlib import Path

import nox

nox.options.error_on_missing_interpreters = True

_LICENSE_HEADER = """# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
PYVERSIONS = ["3.9", "3.10", "3.11", "3.12"]
WIN32 = sys.platform == "win32"
PLATFORM = "win" if WIN32 else "linux"


@nox.session()
def fixformat(session: nox.Session):
    """Force formatting on python files"""
    session.install("isort", "black")
    session.run("python", "-m", "isort", ".")
    session.run("python", "-m", "black", ".")


@nox.session()
def format(session: nox.Session):
    """Check formatting of python files"""
    session.install("isort", "black")
    session.run("python", "-m", "isort", "--check", ".")
    session.run("python", "-m", "black", "--check", ".")

    def wrong_license_header(file: str) -> bool:
        with open(file, "r", encoding="UTF-8") as ifile:
            header = ifile.readline() + ifile.readline() + ifile.readline()
            return header != _LICENSE_HEADER

    source_files = glob.glob("sct/**/*.py", recursive=True)
    no_licensed_files = list(filter(wrong_license_header, source_files))

    if len(no_licensed_files) > 0:
        for file in no_licensed_files:
            session.warn(f"{file} has no license header")
        session.error()


@nox.session()
def pylint(session: nox.Session):
    """Linting with pylint"""
    session.install("pylint")
    session.run("python", "-m", "pylint", "sct")


@nox.session()
def build_sdist(session: nox.Session):
    """Building source distribution"""
    session.install("build")
    session.run("python", "-m", "build", "--sdist", silent=True)


@nox.session()
def build_wheel(session: nox.Session):
    """Building wheel for distribution"""
    session.install("build")
    session.run("python", "-m", "build", "--wheel", silent=True)


def _get_only_file_matching_in_dir(directory: Path, pattern: str):
    matching_dir_content = list(directory.glob(pattern))
    assert len(matching_dir_content) == 1
    return matching_dir_content[0]


@nox.session(python=PYVERSIONS)
def unittest(session: nox.Session):
    """Module testing with unittest"""
    Path("_build").mkdir(exist_ok=True)

    session.install("-e", ".[cli, test]")

    session.run(
        "python",
        "-m",
        "coverage",
        "run",
        "--source=sct",
        "-m",
        "xmlrunner",
        "--output-file",
        f"_build/unittest-report-{PLATFORM}-py{session.python}.xml",
        "discover",
    )
    session.run("python", "-m", "coverage", "report", "-m")
    session.run(
        "python",
        "-m",
        "coverage",
        "xml",
        "-o",
        f"_build/unittest-coverage-{PLATFORM}-py{session.python}.xml",
    )


@nox.session()
def build_doc(session: nox.Session):
    """Building documentation"""
    if tag := os.getenv("CI_COMMIT_TAG"):
        build_dir = f"docs/build/sct-{tag}-html-doc"
    elif sha := os.getenv("CI_COMMIT_SHORT_SHA"):
        build_dir = f"docs/build/sct-{sha}-html-doc"
    else:
        build_dir = "docs/build/"

    session.install("-e", ".[doc]")

    source_static_dir = Path("docs/source/_static")
    source_static_dir.mkdir(exist_ok=False)

    autodoc_scss = Path("docs/source/resource/autodoc.scss")
    session.run("scss-compile", "--no-git", str(autodoc_scss), success_codes=[0, 2])
    Path("docs/source/resource/autodoc.css").rename("docs/source/_static/custom.css")

    session.run("python", "-m", "sphinx", "-M", "clean", "docs/source", build_dir)
    session.run("python", "-m", "sphinx", "-b", "html", "docs/source", build_dir)

    shutil.rmtree(str(source_static_dir))

    if os.getenv("CI") == "true":
        session.log(f"compressing '{build_dir}'")
        root_dir, base_dir = Path(build_dir).parent, Path(build_dir).name
        shutil.make_archive(build_dir, "zip", root_dir=root_dir, base_dir=base_dir)
