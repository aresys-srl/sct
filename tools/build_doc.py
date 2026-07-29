#!/usr/bin/env python
# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Build the SCT documentation with zensical."""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent

    if (root / "site").exists():
        shutil.rmtree(root / "site")

    tag = os.getenv("CI_COMMIT_TAG") or os.getenv("GITHUB_REF_NAME", "dev")
    sha = os.getenv("CI_COMMIT_SHORT_SHA")
    if sha is None:
        try:
            sha = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except subprocess.CalledProcessError:
            sha = ""
    date = datetime.now().strftime("%Y-%m-%d")

    build_info_template = root / "docs" / "about" / "build.template.md"
    build_info = build_info_template.read_text(encoding="utf-8")
    build_info = build_info.replace("__SHA__", sha).replace("__TAG__", tag).replace("__DATE__", date)
    build_info_template.with_name("build.md").write_text(build_info, encoding="utf-8")
    build_info_template.unlink()

    subprocess.run(["zensical", "build", "-f", str(root / "zensical.toml")], check=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
