"""Code and data as sources of their own (docs/archive/CODE_PLAN.md): a software record cites the
values written in its code by file and line, pins the code by its content, and runs it; a
dataset record cites spreadsheet cells. Neither the code nor the data is ever committed."""

import shutil
import zipfile
from pathlib import Path

import pytest
import yaml

from boxgraph.engine import Builder
from boxgraph.sources import read_cells, tree_digest
from boxgraph.store import load_record
from boxgraph.synthesis import build_synthesis
from boxgraph.validate import validate

FX = Path(__file__).parent / "fixtures"


def _project(tmp_path: Path) -> Path:
    """records/toy, records/toycode and the code under corpus/code/toycode, as a project lays them out."""
    root = tmp_path / "project"
    for rid in ("toy", "toycode"):
        shutil.copytree(FX / rid, root / "records" / rid)
    shutil.copytree(FX / "toycode_src", root / "corpus" / "code" / "toycode")
    return root


def _errors(d: Path, run=True, tmp=None):
    return validate(load_record(d), run=run, cache_dir=tmp).errors


def test_a_software_record_is_sound_with_its_code_pinned_and_quoted(tmp_path):
    """A software record whose quotes are on the cited lines of its code, and whose code matches its version, is sound."""
    root = _project(tmp_path)
    r = validate(load_record(root / "records" / "toycode"), cache_dir=tmp_path / "c")
    assert r.sound, r.errors


def test_a_quote_not_on_its_lines_of_code_is_an_error(tmp_path):
    """A value cited from code must quote the cited lines; a wrong line or a wrong quote is an error."""
    root = _project(tmp_path)
    d = root / "records" / "toycode"
    data = yaml.safe_load((d / "data.yaml").read_text())
    data[0]["citation"]["lines"] = "5"
    data[1]["citation"]["quote"] = "XB = 0.7"
    (d / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    errs = _errors(d, tmp=tmp_path / "c")
    assert any("k0_code" in e and "line" in e for e in errs) and any("xb_code" in e for e in errs)


def test_code_that_changed_since_it_was_read_is_an_error(tmp_path):
    """The record pins its code by a digest of its files; code that no longer matches is an error until it is read again."""
    root = _project(tmp_path)
    (root / "corpus" / "code" / "toycode" / "clutch.py").write_text("K0 = 0.3\n")
    assert any("changed" in e for e in _errors(root / "records" / "toycode", tmp=tmp_path / "c"))


def test_without_the_code_the_record_is_checked_for_structure_only(tmp_path):
    """The code is never committed: without it, a structure-only check passes with a warning, and a full one is an error."""
    root = _project(tmp_path)
    shutil.rmtree(root / "corpus")
    d = root / "records" / "toycode"
    assert validate(load_record(d), run=False).sound
    assert any("code" in e for e in _errors(d, tmp=tmp_path / "c"))


def test_a_model_that_runs_the_sources_own_code_outputs_values_of_origin_run(tmp_path):
    """A software model runs the released code itself (found through BOXGRAPH_SOURCE), and what it outputs has origin run."""
    root = _project(tmp_path)
    b = Builder(load_record(root / "records" / "toycode"), cache_dir=tmp_path / "c").build()
    v = b.values["t_code"]
    assert v.origin == "run" and abs(v.value - 2 * 2.718281828 ** (-5 * 0.5 / 4.1)) < 1e-6


def test_a_value_in_the_code_that_differs_from_the_paper_is_a_finding(tmp_path):
    """A parameter written in the code is checked against the value the paper prints, and a difference is a finding."""
    root = _project(tmp_path)
    syn = build_synthesis(root / "records", cache_dir=tmp_path / "c")
    c = next(x for x in syn["cited_values"] if x["datum"] == "toycode/k0_code")
    assert c["verdict"] == "not reproduced"
    assert any(f["kind"] == "cited_value" and f["subject"] == "toycode/k0_code" for f in syn["findings"])


def _xlsx(path: Path, sheets: dict[str, list[list]]) -> None:
    """A minimal .xlsx with inline strings and numbers, as a spreadsheet program writes them."""
    def col(i):
        s = ""
        i += 1
        while i:
            i, r = divmod(i - 1, 26)
            s = chr(65 + r) + s
        return s

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        rels = "".join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="x"/>' for i in range(1, len(sheets) + 1))
        z.writestr("xl/_rels/workbook.xml.rels", f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        names = "".join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(sheets, 1))
        z.writestr("xl/workbook.xml", '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{names}</sheets></workbook>')
        for i, rows in enumerate(sheets.values(), 1):
            xml = []
            for r, row in enumerate(rows, 1):
                cells = []
                for c, v in enumerate(row):
                    ref = f"{col(c)}{r}"
                    if isinstance(v, str):
                        cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{v}</t></is></c>')
                    elif v is not None:
                        cells.append(f'<c r="{ref}"><v>{v}</v></c>')
                xml.append(f'<row r="{r}">{"".join(cells)}</row>')
            z.writestr(f"xl/worksheets/sheet{i}.xml", '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                       f'<sheetData>{"".join(xml)}</sheetData></worksheet>')


def test_cells_are_read_from_a_spreadsheet_by_sheet_and_range(tmp_path):
    """read_cells returns a cell, a column range or a row range from a named sheet, numbers as numbers."""
    f = tmp_path / "d.xlsx"
    _xlsx(f, {"Figure 1": [["F (pN)", "t (s)"], [0, 5.0], [5, 2.7], [10, 1.5]], "Other": [["x"]]})
    assert read_cells(f, "Figure 1", "B2") == [5.0]
    assert read_cells(f, "Figure 1", "A2:A4") == [0, 5, 10]
    assert read_cells(f, "Figure 1", "A1:B1") == ["F (pN)", "t (s)"]
    with pytest.raises(KeyError):
        read_cells(f, "Nope", "A1")


def test_a_dataset_record_cites_cells_and_they_are_checked(tmp_path):
    """A dataset record's values cite their sheet and cells; values that do not match the cells are errors."""
    root = tmp_path / "project"
    d = root / "records" / "toydata"
    shutil.copytree(FX / "toydata", d)
    f = root / "corpus" / "data" / "toydata.xlsx"
    _xlsx(f, {"Figure 1": [["F (pN)", "t (s)"], [0, 5.0], [5, 2.7], [10, 1.5]]})
    src = yaml.safe_load((d / "source.yaml").read_text())
    src["version"] = tree_digest(f)
    (d / "source.yaml").write_text(yaml.safe_dump(src, sort_keys=False))
    r = validate(load_record(d), cache_dir=tmp_path / "c")
    assert r.sound, r.errors
    data = yaml.safe_load((d / "data.yaml").read_text())
    data[0]["table"]["values"][1] = "2.9"
    (d / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    assert any("cell" in e for e in _errors(d, tmp=tmp_path / "c"))


def test_a_model_cannot_reach_the_network_when_the_system_allows_a_sandbox(tmp_path):
    """Record code runs without network access wherever the system can provide that (Linux namespaces)."""
    from boxgraph import engine

    if not engine.sandbox_available():
        pytest.skip("no network namespace on this system")
    m = tmp_path / "net"
    m.mkdir()
    (m / "model.py").write_text(
        "import socket\n"
        "def run(i, s):\n"
        "    try:\n"
        "        socket.create_connection(('1.1.1.1', 53), timeout=2)\n"
        "        return {'reached': 1.0}\n"
        "    except OSError:\n"
        "        return {'reached': 0.0}\n")
    assert engine.execute(m / "model.py", [{"inputs": {}, "settings": {}}])[0]["reached"] == 0.0


def test_a_curve_said_to_come_from_a_dataset_is_checked_point_by_point(tmp_path):
    """A table (e.g. a curve read from a figure) said to come from a dataset is compared with it at each shared x value."""
    root = tmp_path / "project"
    for rid in ("toy", "toydata"):
        shutil.copytree(FX / rid, root / "records" / rid)
    f = root / "corpus" / "data" / "toydata.xlsx"
    _xlsx(f, {"Figure 1": [["F (pN)", "t (s)"], [0, 5.0], [5, 2.7], [10, 1.5]]})
    src = yaml.safe_load((root / "records" / "toydata" / "source.yaml").read_text())
    src["version"] = tree_digest(f)
    (root / "records" / "toydata" / "source.yaml").write_text(yaml.safe_dump(src, sort_keys=False))
    data = yaml.safe_load((root / "records" / "toy" / "data.yaml").read_text())
    curve = next(d for d in data if d["id"] == "t_curve")
    curve.update(from_source="toydata", from_datum="t_measured")
    curve["table"]["values"][2] = "1.9"  # the paper's figure, read: one point off the source data
    (root / "records" / "toy" / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    syn = build_synthesis(root / "records", cache_dir=tmp_path / "c")
    c = next(x for x in syn["cited_values"] if x["datum"] == "toy/t_curve")
    assert c["status"] == "checked" and c["verdict"] == "not reproduced"
    assert c["per_value"] == ["reproduced", "reproduced", "not reproduced"]


def test_a_link_can_say_where_a_value_comes_from_when_the_datum_does_not(tmp_path):
    """A paper read before its source data never named it: a link in cited.yaml may give from_source as well as from_datum."""
    root = tmp_path / "project"
    for rid in ("toy", "toydata"):
        shutil.copytree(FX / rid, root / "records" / rid)
    f = root / "corpus" / "data" / "toydata.xlsx"
    _xlsx(f, {"Figure 1": [["F (pN)", "t (s)"], [0, 5.0], [5, 2.7], [10, 1.5]]})
    src = yaml.safe_load((root / "records" / "toydata" / "source.yaml").read_text())
    src["version"] = tree_digest(f)
    (root / "records" / "toydata" / "source.yaml").write_text(yaml.safe_dump(src, sort_keys=False))
    (root / "records" / "toy" / "cited.yaml").write_text(
        "- {datum: t_curve, from_source: toydata, from_datum: t_measured, evidence: the source data of Fig. 1}\n")
    assert validate(load_record(root / "records" / "toy"), run=False).sound
    syn = build_synthesis(root / "records", cache_dir=tmp_path / "c")
    c = next(x for x in syn["cited_values"] if x["datum"] == "toy/t_curve")
    assert c["verdict"] == "reproduced" and c["from_source"] == "toydata"
