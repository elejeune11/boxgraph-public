"""The command-line tool."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

FX = Path(__file__).parent / "fixtures"


def cli(*args, cwd=None):
    return subprocess.run([sys.executable, "-m", "boxgraph", *args], capture_output=True, text=True, cwd=cwd)


def test_validate_sound_record():
    """`boxgraph validate` reports a sound record and exits 0."""
    r = cli("validate", str(FX / "toy"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "SOUND" in r.stdout


def test_validate_unsound_record(tmp_path):
    """`boxgraph validate` reports an unsound record and exits 1."""
    d = tmp_path / "toy"
    shutil.copytree(FX / "toy", d)
    (d / "models" / "decay" / "model.py").write_text("def run(i, s):\n    raise RuntimeError('no')\n")
    r = cli("validate", str(d))
    assert r.returncode == 1
    assert "NOT SOUND" in r.stdout


def test_build_writes_synthesis_and_report(tmp_path):
    """`boxgraph build` writes the Synthesis, per-record builds, the report and the explorer."""
    root = tmp_path / "records"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    out = tmp_path / "build"
    r = cli("build", str(root), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    syn = json.loads((out / "synthesis.json").read_text())
    assert set(syn["papers"]) == {"toy", "toy2"}
    assert (out / "report.md").exists() and (out / "report.html").exists()
    assert (out / "records" / "toy.json").exists()
    assert "toy2" in (out / "explorer.html").read_text()
    assert "toy2" in (out / "overview" / "index.html").read_text()


def test_build_takes_the_overviews_text_and_case_studies_from_a_content_file(tmp_path):
    """`boxgraph build --overview content.yaml` puts that file's introduction and case studies in the overview."""
    root = tmp_path / "records"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    content = tmp_path / "overview.yaml"
    content.write_text("intro: [An introduction for the reader.]\n"
                       "case_studies:\n  - {id: c1, title: First case, summary: s, steps: [{text: t, show: 'comparison: toy/cmp_good'}]}\n")
    out = tmp_path / "build"
    r = cli("build", str(root), "--out", str(out), "--overview", str(content))
    assert r.returncode == 0, r.stdout + r.stderr
    page = (out / "overview" / "index.html").read_text()
    assert "An introduction for the reader." in page and "First case" in page


def test_installed_command_works_from_anywhere(tmp_path):
    """The installed `boxgraph` command imports the real package from any directory."""
    exe = Path(sys.executable).with_name("boxgraph")
    r = subprocess.run([str(exe), "--version"], capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    r = subprocess.run([str(exe), "validate", str(FX / "toy"), "--no-run"], capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_relations_command_tests_the_chosen_records_relations(tmp_path):
    """`boxgraph relations` tests the relations entered in the chosen records and names each status."""
    root = tmp_path / "records"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    r = cli("relations", str(root), "--only", "toy2")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "toy2/rel_same" in r.stdout and "verified" in r.stdout and "toy2/rel_wrong" in r.stdout


def test_relations_command_fails_on_a_relation_to_no_model(tmp_path):
    """A relation naming a model that does not exist makes `boxgraph relations` exit 1, naming it."""
    root = tmp_path / "records"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    rel = root / "toy2" / "relations.yaml"
    rel.write_text(rel.read_text() + "- {id: rel_ghost, kind: same_as, a: toy/ghost, b: toy2/lifetime, mapping: {}, "
                   "provenance: proposed, reason: x}\n")
    r = cli("relations", str(root), "--only", "toy2")
    assert r.returncode == 1 and "rel_ghost" in r.stdout and "toy/ghost" in r.stdout


def test_validate_uses_the_shared_cache_named_in_the_environment(tmp_path):
    """`boxgraph validate` without --cache uses the cache named by BOXGRAPH_CACHE, so agents and gates share model runs."""
    import os

    env = {**os.environ, "BOXGRAPH_CACHE": str(tmp_path / "shared")}
    r = subprocess.run([sys.executable, "-m", "boxgraph", "validate", str(FX / "toy")], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert any((tmp_path / "shared").glob("*.json"))


def test_digest_prints_the_version_that_pins_code_or_data(tmp_path):
    """`boxgraph digest PATH` prints the sha256 digest a code or data record pins its files with."""
    from boxgraph.sources import tree_digest

    (tmp_path / "code").mkdir()
    (tmp_path / "code" / "run.m").write_text("x = 1;\n")
    r = cli("digest", str(tmp_path / "code"))
    assert r.returncode == 0 and r.stdout.strip() == tree_digest(tmp_path / "code")


def test_relation_tests_use_the_shared_cache(tmp_path):
    """`boxgraph relations` caches its model runs in the cache named by BOXGRAPH_CACHE, so a gate repeats no test an agent ran."""
    import os

    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    env = {**os.environ, "BOXGRAPH_CACHE": str(tmp_path / "shared")}
    r = subprocess.run([sys.executable, "-m", "boxgraph", "relations", str(root), "--only", "toy2"],
                       capture_output=True, text=True, env=env)
    assert any((tmp_path / "shared").glob("*.json")), r.stdout + r.stderr
