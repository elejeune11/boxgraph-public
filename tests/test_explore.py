"""The explorer: one self-contained page that shows the Synthesis as a
knowledge graph and a dashboard of results (04-synthesis.md)."""

import copy
import json
import re
import shutil
from pathlib import Path

import pytest
from PIL import Image

from boxgraph.explore import render_explorer
from boxgraph.synthesis import build_synthesis, to_json

FX = Path(__file__).parent / "fixtures"
CDN = ("https://cdnjs.cloudflare.com/ajax/libs/", "https://cdn.jsdelivr.net/npm/")


@pytest.fixture(scope="module")
def full(tmp_path_factory):
    root = tmp_path_factory.mktemp("records")
    for name in ("toy", "toy2"):
        shutil.copytree(FX / name, root / name)
    return build_synthesis(root, cache_dir=tmp_path_factory.mktemp("cache"))


@pytest.fixture(scope="module")
def syn(full):
    return json.loads(json.dumps(to_json(full), default=str))


def embedded(page: str) -> dict:
    m = re.search(r'<script type="application/json" id="bg-data">(.*?)</script>', page, re.S)
    assert m, "no embedded data"
    return json.loads(m.group(1))


def test_explorer_embeds_every_paper_relation_and_finding(syn):
    """The explorer embeds every paper, relation and finding of the Synthesis."""
    data = embedded(render_explorer(syn, title="t"))
    ids = {n["id"] for n in data["graph"]["nodes"]}
    assert set(syn["papers"]) <= ids
    assert {r["key"] for r in data["relations"]} == {r["key"] for r in syn["relations"]}
    assert {e["id"] for e in data["graph"]["edges"] if e["type"] == "relation"} == {r["key"] for r in syn["relations"]}
    assert sorted(f["subject"] for f in data["findings"]) == sorted(f["subject"] for f in syn["findings"])
    assert {n["finding"]["subject"] for n in data["graph"]["nodes"] if n["type"] == "finding"} == \
        {f["subject"] for f in syn["findings"]}


def test_explorer_graph_edges_join_nodes(syn):
    """Every graph edge joins two nodes of the graph, and ids are unique."""
    g = embedded(render_explorer(syn, title="t"))["graph"]
    ids = [n["id"] for n in g["nodes"]]
    assert len(ids) == len(set(ids))
    eids = [e["id"] for e in g["edges"]]
    assert len(eids) == len(set(eids))
    for e in g["edges"]:
        assert e["source"] in ids and e["target"] in ids, e


def test_explorer_colours_checks_by_verdict(syn):
    """Cross-paper checks and checked cited values are edges that carry their verdict."""
    g = embedded(render_explorer(syn, title="t"))["graph"]
    cross = [e for e in g["edges"] if e["type"] == "cross_check"]
    assert {e["verdict"] for e in cross} == {x["verdict"] for x in syn["cross_checks"] if x.get("status") == "checked"}
    cited = [e for e in g["edges"] if e["type"] == "cited"]
    assert len(cited) == sum(1 for c in syn["cited_values"] if c.get("status") == "checked")
    assert any(e["type"] == "comparison" and e["verdict"] == "not reproduced" for e in g["edges"])


def test_explorer_is_deterministic_and_order_independent(syn):
    """The same Synthesis gives the same page, whatever order its parts come in."""
    a = render_explorer(syn, title="t")
    shuffled = copy.deepcopy(syn)
    shuffled["papers"] = dict(reversed(list(shuffled["papers"].items())))
    for k in ("relations", "findings", "cross_checks", "cited_values", "references", "families"):
        shuffled[k] = list(reversed(shuffled[k]))
    assert render_explorer(shuffled, title="t") == a
    assert render_explorer(syn, title="t") == a


def test_explorer_takes_the_built_synthesis_too(full, syn):
    """The explorer gives the same page from the built Synthesis and from its JSON form."""
    assert render_explorer(full, title="t") == render_explorer(syn, title="t")


def test_explorer_loads_scripts_only_from_pinned_cdn(syn):
    """The page is one file: its only external scripts come from an allowed CDN at an exact version."""
    page = render_explorer(syn, title="t")
    srcs = re.findall(r"<script[^>]*\ssrc=\"([^\"]+)\"", page)
    for s in srcs:
        assert s.startswith(CDN), s
        assert re.search(r"[/@]\d+\.\d+\.\d+/", s), s
    assert not re.search(r"<link[^>]+stylesheet[^>]+href=\"(?!https://fonts.googleapis.com)", page)


def test_explorer_embeds_figure_images(syn, tmp_path):
    """Figure readings show their overlay as an embedded image when a figure folder is given."""
    s = copy.deepcopy(syn)
    s["papers"]["toy"]["figures"] = [{
        "id": "fig_a", "where": "Fig. 1", "what": "a curve", "page": 2, "readings": [], "errors": [], "notes": [],
        "used_by": [{"comparison": "cmp_good", "purpose": "reproduction", "verdict": "reproduced", "per_value": None}],
    }]
    (tmp_path / "toy").mkdir()
    Image.new("RGB", (40, 30), (200, 10, 10)).save(tmp_path / "toy" / "fig_a.png")
    with_img = render_explorer(s, title="t", figdir=tmp_path)
    assert "data:image/png;base64," in with_img
    assert "fig_a" in json.dumps(embedded(with_img)["figures"])
    assert "data:image/png;base64," not in render_explorer(s, title="t")


def test_explorer_keeps_embedded_overlays_small(syn, tmp_path):
    """A large overlay is embedded at most 720 px wide with a 256-colour palette, so the page stays publishable."""
    import base64
    import io

    s = copy.deepcopy(syn)
    s["papers"]["toy"]["figures"] = [{
        "id": "fig_big", "where": "Fig. 2", "what": "a curve", "page": 2, "readings": [], "errors": [], "notes": [],
        "used_by": [],
    }]
    (tmp_path / "toy").mkdir()
    im = Image.new("RGB", (3000, 2000), (255, 255, 255))
    for x in range(0, 3000, 7):
        for y in range(0, 2000, 50):
            im.putpixel((x, y), (x % 256, y % 256, (x + y) % 256))
    im.save(tmp_path / "toy" / "fig_big.png")
    page = render_explorer(s, title="t", figdir=tmp_path)
    uri = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", page).group(1)
    got = Image.open(io.BytesIO(base64.b64decode(uri)))
    assert got.width <= 720 and got.mode == "P", (got.size, got.mode)


def test_explorer_can_keep_its_images_beside_the_page(syn, tmp_path):
    """With an image folder, overlays are written there (reduced as when embedded) and referenced by relative path,
    so the page stays small however many figures the corpus has."""
    s = copy.deepcopy(syn)
    s["papers"]["toy"]["figures"] = [{
        "id": "fig_a", "where": "Fig. 1", "what": "a curve", "page": 2, "readings": [], "errors": [], "notes": [],
        "used_by": [],
    }]
    (tmp_path / "figs" / "toy").mkdir(parents=True)
    Image.new("RGB", (1500, 900), (200, 10, 10)).save(tmp_path / "figs" / "toy" / "fig_a.png")
    page = render_explorer(s, title="t", figdir=tmp_path / "figs", image_dir=tmp_path / "out" / "explorer_files",
                           image_prefix="explorer_files/")
    assert "data:image/png;base64," not in page
    src = next(f["src"] for f in embedded(page)["figures"] if f["id"] == "fig_a")
    assert src == "explorer_files/toy/fig_a.png"
    with Image.open(tmp_path / "out" / "explorer_files" / "toy" / "fig_a.png") as im:
        assert im.width == 720
