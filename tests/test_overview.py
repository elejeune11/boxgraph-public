"""The overview: a page for showing the Synthesis to others (04-synthesis.md). It
leads with a graph of the sources joined by what was tested between them, has a
view per source, and carries a few case studies whose numbers come from the build."""

import copy
import json
import re
import shutil
from pathlib import Path

import pytest

from boxgraph.overview import CaseStudyError, layout, overview_data, render_overview
from boxgraph.synthesis import build_synthesis, to_json

FX = Path(__file__).parent / "fixtures"
ALLOWED = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")


@pytest.fixture(scope="module")
def syn(tmp_path_factory):
    """toy, toy2 and toycode (with its code), as a project lays them out."""
    root = tmp_path_factory.mktemp("project")
    for rid in ("toy", "toy2", "toycode"):
        shutil.copytree(FX / rid, root / "records" / rid)
    shutil.copytree(FX / "toycode_src", root / "corpus" / "code" / "toycode")
    s = build_synthesis(root / "records", cache_dir=tmp_path_factory.mktemp("cache"))
    return json.loads(json.dumps(to_json(s), default=str))


@pytest.fixture
def dated(syn):
    """The same Synthesis with the three sources in different years."""
    s = copy.deepcopy(syn)
    for sid, year in (("toy", 2001), ("toy2", 2010), ("toycode", 2012)):
        s["papers"][sid]["year"] = year
    return s


def embedded(page: str) -> dict:
    m = re.search(r'<script type="application/json" id="ov-data">(.*?)</script>', page, re.S)
    assert m, "no embedded data"
    return json.loads(m.group(1))


def test_every_source_is_a_node_with_its_kind_year_and_tally(syn):
    """Every source in the Synthesis is a node, with its kind, year, verdict tally and models."""
    d = overview_data(syn)
    by = {s["id"]: s for s in d["sources"]}
    assert set(by) == set(syn["papers"])
    assert by["toycode"]["kind"] == "software" and by["toy"]["kind"] == syn["papers"]["toy"]["kind"]
    assert by["toy"]["tally"] == syn["papers"]["toy"]["tally"]
    for sid, s in by.items():  # the bar counts every comparison, whatever its purpose
        bp = syn["papers"][sid]["tally_by_purpose"]
        assert s["checked"] == {v: sum(t.get(v, 0) for t in bp.values()) for v in ("reproduced", "close", "not reproduced", "no verdict")}
    assert {m["id"] for m in by["toy2"]["models"]} == set(syn["papers"]["toy2"]["models"])


def test_links_join_sources_by_tested_relations_counted_by_status(syn):
    """Two sources are linked by the relations tested between their models, counted by status; a relation inside one source is not a link."""
    d = overview_data(syn)
    rel = [x for x in d["links"] if x["kind"] == "relation"]
    assert [(x["a"], x["b"]) for x in rel] == [("toy", "toy2")]
    between = [r for r in syn["relations"] if r["a"].split("/")[0] != r["b"].split("/")[0]]
    assert sum(rel[0]["status"].values()) == len(between)
    assert rel[0]["status"]["verified"] == sum(r["status"] == "verified" for r in between)


def test_a_checked_cited_value_links_the_two_sources_and_says_if_it_agrees(syn):
    """A cited value checked against its source links the two sources, counting the values that agree and those that do not."""
    d = overview_data(syn)
    cited = {(x["a"], x["b"]): x for x in d["links"] if x["kind"] == "cited"}
    assert set(cited) == {("toy", "toy2"), ("toy", "toycode")}
    code = cited[("toy", "toycode")]
    assert code["agree"] == 0 and code["differ"] == 1


def test_code_or_data_is_placed_with_the_papers_it_takes_values_from(syn):
    """Released code or data names the papers it belongs to: those it takes values from."""
    by = {s["id"]: s for s in overview_data(syn)["sources"]}
    assert by["toycode"]["of"] == ["toy"]
    assert by["toy"]["of"] == []


def test_families_name_the_sources_they_span(syn):
    """Each family lists its models and the sources they come from."""
    fam = overview_data(syn)["families"]
    assert fam == [{"models": ["toy/decay", "toy2/lifetime"], "sources": ["toy", "toy2"]}]


def test_layout_orders_sources_by_year_and_keeps_them_apart(dated):
    """The layout puts sources in order of year from left to right, and no two nodes overlap."""
    pos = layout(overview_data(dated))
    assert pos["toy"]["x"] < pos["toy2"]["x"] < pos["toycode"]["x"]
    pts = list(pos.values())
    for i, p in enumerate(pts):
        for q in pts[i + 1:]:
            assert (p["x"] - q["x"]) ** 2 + (p["y"] - q["y"]) ** 2 >= (p["r"] + q["r"]) ** 2


def test_layout_does_not_depend_on_the_order_of_the_synthesis(dated):
    """The same Synthesis in another order gives the same layout."""
    shuffled = copy.deepcopy(dated)
    shuffled["papers"] = dict(reversed(list(shuffled["papers"].items())))
    shuffled["relations"] = list(reversed(shuffled["relations"]))
    shuffled["cited_values"] = list(reversed(shuffled["cited_values"]))
    assert layout(overview_data(shuffled)) == layout(overview_data(dated))


def test_the_page_embeds_its_data_and_loads_nothing_from_elsewhere(syn, tmp_path):
    """The page embeds the graph and every source view, is the same on every build, and loads nothing but fonts from outside."""
    a = render_overview(syn, tmp_path / "a", title="T")
    b = render_overview(syn, tmp_path / "b", title="T")
    page = a.read_text()
    assert page == b.read_text()
    d = embedded(page)
    assert {s["id"] for s in d["sources"]} == set(syn["papers"])
    assert set(d["positions"]) == set(syn["papers"])
    for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', page):
        assert url.startswith(ALLOWED), url
    assert "<title>T</title>" in page


def test_a_source_view_holds_its_verdicts_models_and_open_questions(syn, tmp_path):
    """The view of a source holds its verdicts, its models with their relations to other sources, and its open questions."""
    d = embedded(render_overview(syn, tmp_path, title="T").read_text())
    toy2 = next(s for s in d["sources"] if s["id"] == "toy2")
    assert {v["comparison"] for v in toy2["verdicts"]} == {v["comparison"] for v in syn["papers"]["toy2"]["verdicts"]}
    assert [q["id"] for q in toy2["questions"]] == [q["id"] for q in syn["papers"]["toy2"]["questions"]]
    lifetime = next(m for m in toy2["models"] if m["id"] == "lifetime")
    assert any(r["other"] == "toy/decay" and r["kind"] == "same_as" for r in lifetime["relations"])


def test_a_case_study_shows_values_from_the_build(syn, tmp_path):
    """A case study cites a comparison, a relation or a cited value, and the page shows its numbers as the build computed them."""
    v = next(x for x in syn["papers"]["toy"]["verdicts"] if x["comparison"] == "cmp_good")
    content = {"case_studies": [{"id": "one", "title": "A first case", "summary": "What it shows.",
                                 "steps": [{"text": "The printed value against the model.", "show": "comparison: toy/cmp_good"},
                                           {"text": "The two models.", "show": "relation: toy2/rel_same"},
                                           {"text": "A value taken from toy.", "show": "cited: toy2/k0_cited_ok"}]}]}
    d = embedded(render_overview(syn, tmp_path, title="T", content=content).read_text())
    steps = d["case_studies"][0]["steps"]
    assert steps[0]["evidence"]["verdict"] == v["verdict"]
    assert steps[0]["evidence"]["printed"] == v["printed_text"]
    assert steps[1]["evidence"]["kind"] == "relation" and steps[1]["evidence"]["status"]
    assert steps[2]["evidence"]["verdict"] == "reproduced"
    assert steps[2]["evidence"]["unit"] == syn["papers"]["toy2"]["data"]["k0_cited_ok"]["unit"]
    assert steps[2]["evidence"]["cited_unit"] == syn["papers"]["toy"]["data"]["k0"]["unit"]


def test_a_case_study_that_names_something_not_in_the_build_is_an_error(syn, tmp_path):
    """A case study naming a comparison the build does not have stops the overview with a message that names it."""
    content = {"case_studies": [{"id": "x", "title": "X", "summary": "",
                                 "steps": [{"text": "t", "show": "comparison: toy/no_such"}]}]}
    with pytest.raises(CaseStudyError, match="toy/no_such"):
        render_overview(syn, tmp_path, title="T", content=content)


def test_a_case_study_can_show_a_refinement_a_family_and_an_open_question(syn, tmp_path):
    """A case study can also show a refinement series, the family a model belongs to, and an open question, from the build."""
    ref = syn["papers"]["toy"]["refinements"][0]
    q = syn["papers"]["toy2"]["questions"][0]
    content = {"case_studies": [{"id": "two", "title": "T", "summary": "",
                                 "steps": [{"text": "a", "show": f"refinement: toy/{ref['id']}"},
                                           {"text": "b", "show": "family: toy2/lifetime"},
                                           {"text": "c", "show": f"question: toy2/{q['id']}"}]}]}
    d = embedded(render_overview(syn, tmp_path, title="T", content=content).read_text())
    r, f, qq = (s["evidence"] for s in d["case_studies"][0]["steps"])
    assert r["kind"] == "refinement" and r["belongs_to"] == ref["belongs_to"]
    assert [p["setting"] for p in r["series"]] == [p["setting"] for p in ref["series"]]
    assert f["kind"] == "family" and [m["key"] for m in f["models"]] == ["toy/decay", "toy2/lifetime"]
    assert all(m["name"] and m["source"] for m in f["models"])
    assert qq["kind"] == "question" and qq["text"] == q["text"]


def test_the_full_graph_has_every_source_and_model_joined_by_what_was_tested(syn):
    """The full view has every source and every model; each model hangs from its source, and every tested relation joins its two models."""
    from boxgraph.overview import full_graph

    g = full_graph(overview_data(syn), syn)
    ids = {n["id"] for n in g["nodes"]}
    models = {f"{sid}/{m}" for sid, p in syn["papers"].items() for m in p["models"]}
    assert ids == set(syn["papers"]) | models
    member = {(e["a"], e["b"]) for e in g["edges"] if e["kind"] == "member"}
    assert member == {(m.split("/")[0], m) for m in models}
    rel = [e for e in g["edges"] if e["kind"] == "relation"]
    assert len(rel) == len({(r["a"], r["b"], r["kind"], r["status"]) for r in syn["relations"]})
    assert all(e["a"] in ids and e["b"] in ids for e in g["edges"])


def test_the_full_layout_keeps_every_node_on_the_canvas_whatever_the_order(syn):
    """The full view's layout places every node on the canvas, and the same Synthesis in another order gives the same layout."""
    from boxgraph.overview import full_graph, full_layout

    pos = full_layout(full_graph(overview_data(syn), syn), width=900, height=600)
    assert all(0 <= p["x"] <= 900 and 0 <= p["y"] <= 600 for p in pos.values())
    shuffled = copy.deepcopy(syn)
    shuffled["papers"] = dict(reversed(list(shuffled["papers"].items())))
    shuffled["relations"] = list(reversed(shuffled["relations"]))
    assert full_layout(full_graph(overview_data(shuffled), shuffled), width=900, height=600) == pos


def test_the_page_offers_both_views_and_no_family_highlight(syn, tmp_path):
    """The page embeds the full view and the sources view, with a position for every node of each, and no longer highlights families under the graph."""
    page = render_overview(syn, tmp_path, title="T").read_text()
    d = embedded(page)
    assert {n["id"] for n in d["full"]["nodes"]} == set(d["full"]["positions"])
    assert set(d["positions"]) == set(syn["papers"])
    assert 'id="view-full"' in page and 'id="view-sources"' in page
    assert "Families of models" not in page
