"""Documentation that is generated must be current."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_test_catalogue_is_current():
    """This catalogue is regenerated whenever the tests change."""
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "test_catalog.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_the_repository_holds_no_copy_of_a_paper():
    """No PDF, page image, page text, figure crop, image, released code (.m, .mat) or data spreadsheet is committed: papers, their code and their data are copyrighted."""
    import re
    import subprocess

    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=root)
    if r.returncode != 0:
        pytest.skip("not a git checkout")
    allowed_text = ("tests/fixtures/", "pipeline/evals/")  # hand-written and synthetic papers only
    own_images = {"docs/figures/overview.png", "docs/figures/overview-cardio.png",  # screenshots of our own pages
                  # our own rendering of released (openly licensed) network data, and its copy next to the page
                  *(f"{d}/schwarz_tree_{v}.png" for d in ("corpora/cardio/overview_figures", "site/cardio/img")
                    for v in ("pressure", "wss", "diameter"))}  # named one by one
    bad = [f for f in r.stdout.splitlines() if f not in own_images
           if re.search(r"\.(pdf|png|jpe?g|tiff?|gif|bmp|webp|djvu|epub|mat|xlsx?)$", f, re.I)
           or (f.startswith(("records/", "corpora/")) and f.endswith(".m"))
           or re.match(r"(corpus/|(corpora/[^/]+/)?records/[^/]+/(text|pages|figwork)/)", f)
           or (f.endswith(".txt") and not f.startswith(allowed_text))]
    assert not bad, bad
