# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Automating python testing, formatting and distribution of SCT"""

import glob
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import nox

nox.options.error_on_missing_interpreters = True

_LICENSE_HEADER = """# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
PY_VERSIONS = ["3.11", "3.12", "3.13", "3.14"]
WIN32 = sys.platform == "win32"
PLATFORM = "win" if WIN32 else "linux"


@nox.session()
def fix_format(session: nox.Session):
    """Reformat code base with ruff"""
    session.install("ruff")
    session.run("ruff", "check", "--select", "I", "--fix-only")
    session.run("ruff", "format")


@nox.session()
def check_format(session: nox.Session):
    """Check proper formatting with ruff. Check presence of license header"""
    session.install("ruff")
    session.run("ruff", "--version")
    session.run("ruff", "format", "--check")
    session.run("ruff", "check")

    def wrong_license_header(file: str) -> bool:
        with open(file, "r", encoding="utf-8") as ifile:
            first_line = ifile.readline()
            if "# noqa:" in first_line:
                first_line = ifile.readline()
            header = first_line + ifile.readline() + ifile.readline()
            return header != _LICENSE_HEADER

    source_files = glob.glob("src/sct/**/*.py", recursive=True)
    no_licensed_files = list(filter(wrong_license_header, source_files))

    if len(no_licensed_files) > 0:
        for file in no_licensed_files:
            session.warn(f"{file} has no license header")
        session.error()


@nox.session()
def pylint(session: nox.Session):
    """Analysis of code-base quality with pylint"""
    session.install("pylint")
    session.run("python", "-m", "pylint", "src/sct")


@nox.session(python=PY_VERSIONS)
def unittest(session: nox.Session):
    """Execute unittest"""
    Path("_build").mkdir(exist_ok=True)

    session.install("-e", ".[web,test,graph]")
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
def build_sdist(session: nox.Session):
    """Build source distribution package"""
    session.install("build")
    session.run("python", "-m", "build", "--sdist", silent=True)


@nox.session()
def build_wheel(session: nox.Session):
    """Build wheel distribution package"""
    session.install("build")
    session.run("python", "-m", "build", "--wheel", silent=True)


def _get_only_file_matching_in_dir(directory: Path, pattern: str):
    matching_dir_content = list(directory.glob(pattern))
    assert len(matching_dir_content) == 1
    return matching_dir_content[0]


@nox.session(venv_backend="conda", python="3.11")
def build_conda_recipe(session: nox.Session):
    """Build a conda recipe from sdist"""
    session.install("build")
    session.run("python", "-m", "build", "--sdist", silent=True)

    sdist_file = _get_only_file_matching_in_dir(Path("dist"), "*.tar.gz").absolute()

    session.conda_install(
        "conda-build",
        "conda-verify",
        "grayskull",
        channel="conda-forge",
    )

    recipe_maintainer = "Aresys srl"
    session.run("grayskull", "pypi", str(sdist_file), "-m", recipe_maintainer)
    yaml_file = Path("sct", "meta.yaml")
    assert yaml_file.exists()


@nox.session(venv_backend="conda", python="3.11")
def build_conda_pkg(session: nox.Session):
    """Build a conda package from conda recipe"""
    # build_conda_recipe(session)

    session.install("build")
    session.run("python", "-m", "build", "--sdist", silent=True)

    session.conda_install(
        "conda-build",
        "conda-verify",
        channel="conda-forge",
    )

    conda_build_dir = Path("conda_build_dir")
    session.run("conda-build", "conda_recipe", "--output-folder", str(conda_build_dir))

    package = _get_only_file_matching_in_dir(conda_build_dir.joinpath("noarch"), "*.conda").absolute()
    shutil.copy(str(package), "dist")


@nox.session()
def build_doc(session: nox.Session):
    """Building documentation"""

    if Path("site").exists():
        shutil.rmtree("site")

    tag = os.getenv("CI_COMMIT_TAG", "dev")
    sha = os.getenv("CI_COMMIT_SHORT_SHA")
    date = datetime.now().strftime("%Y-%m-%d")

    if sha is None:
        try:
            sha = session.run("git", "rev-parse", "--short", "HEAD", external=True, silent=True).strip()
        except Exception:
            sha = ""

    doc_name = f"{date}-{tag}-{sha}-html-doc"

    session.log("Adding build info to documentation section")
    build_info_file = Path("docs/about/build.template.md")
    build_info = build_info_file.read_text()
    build_info = build_info.replace("__SHA__", sha).replace("__TAG__", tag).replace("__DATE__", date)
    build_info_file.parent.joinpath("build.md").write_text(build_info)
    build_info_file.unlink()

    session.log(f"Current dir: {Path.cwd()}")
    session.log(f"Building documentation: {doc_name}")

    session.install(".[doc]")
    session.run("pip", "list")
    session.run("zensical", "build", "-f", str(Path.cwd() / "zensical.toml"))

    if os.getenv("CI") == "true":
        session.log("compressing documentation")
        shutil.make_archive(f"documentation-{doc_name}", "zip", root_dir=".", base_dir="site")
