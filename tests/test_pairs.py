"""Which pairs of papers get a relation job (pipeline/pairs.py).

Relating every paper to every other does not scale; a pair is related when
one cites the other, a model says it comes from the other, two models have
the same shape, or the corpus list asks for it. Each pair says why."""

from pathlib import Path

import yaml

from pipeline.pairs import candidate_pairs


def rec(root: Path, rid: str, authors=None, year=2000, refs=(), models=()):
    d = root / rid
    d.mkdir(parents=True)
    (d / "source.yaml").write_text(yaml.safe_dump({"id": rid, "authors": authors or ["A. Nobody"], "year": year}))
    (d / "references.yaml").write_text(yaml.safe_dump(list(refs)))
    for m in models:
        (d / "models" / m["id"]).mkdir(parents=True)
        (d / "models" / m["id"] / "model.yaml").write_text(yaml.safe_dump(m))


def model(mid, ins, outs, described_from=None):
    m = {"id": mid, "inputs": {f"i{k}": {"unit": u} for k, u in enumerate(ins)},
         "outputs": {f"o{k}": {"unit": u} for k, u in enumerate(outs)}}
    if described_from:
        m["described_from"] = described_from
    return m


def test_a_linked_citation_makes_a_pair(tmp_path):
    """A reference whose source is another record joins the two."""
    rec(tmp_path, "old1978")
    rec(tmp_path, "new2004", refs=[{"id": "ref-1", "text": "G. I. Bell, Science (1978)", "source": "old1978"}])
    got = candidate_pairs(tmp_path, ["old1978", "new2004"])
    assert list(got) == [("new2004", "old1978")] and "cites" in got[("new2004", "old1978")][0]


def test_a_citation_by_name_and_year_makes_a_pair(tmp_path):
    """A reference naming another record's first author and year joins them, for papers read before the other was added."""
    rec(tmp_path, "bell1978", authors=["George I. Bell"], year=1978)
    rec(tmp_path, "later2004", refs=[{"id": "ref-3", "text": "G. I. Bell, Science 200, 618 (1978)."}])
    rec(tmp_path, "other2004", refs=[{"id": "ref-3", "text": "J. Bell, Nature 1, 1 (1990)."}])
    got = candidate_pairs(tmp_path, ["bell1978", "later2004", "other2004"])
    assert ("bell1978", "later2004") in got and ("bell1978", "other2004") not in got


def test_described_from_makes_a_pair(tmp_path):
    """A model that says it is described from another record joins the two."""
    rec(tmp_path, "a2000")
    rec(tmp_path, "b2010", models=[model("m", ["1/s"], ["s"], described_from="a2000")])
    assert ("a2000", "b2010") in candidate_pairs(tmp_path, ["a2000", "b2010"])


def test_models_of_the_same_shape_make_a_pair(tmp_path):
    """Two models with an output of the same dimension and two dimensional inputs in common join their records; one shared input does not."""
    rec(tmp_path, "a2000", models=[model("rate", ["1/s", "pN", "nm"], ["1/s"])])
    rec(tmp_path, "b2010", models=[model("off", ["1/ms", "N", "K"], ["1/min"])])
    rec(tmp_path, "c2020", models=[model("other", ["1/s", "kg"], ["1/s"])])
    rec(tmp_path, "d2020", models=[model("unitless", ["", "dimensionless"], [""])])
    got = candidate_pairs(tmp_path, ["a2000", "b2010", "c2020", "d2020"])
    assert ("a2000", "b2010") in got and "a2000/rate" in got[("a2000", "b2010")][0]
    assert ("a2000", "c2020") not in got and ("b2010", "c2020") not in got
    assert not any("d2020" in p for p in got)


def test_the_corpus_list_can_ask_for_a_pair(tmp_path):
    """relate_with in the corpus list joins two records with no other sign of a relation."""
    rec(tmp_path, "a2000")
    rec(tmp_path, "b2010")
    got = candidate_pairs(tmp_path, ["a2000", "b2010"], manual={"b2010": ["a2000"]})
    assert got == {("a2000", "b2010"): ["the corpus list asks for it (b2010: relate_with)"]}


def test_unrelated_records_and_missing_records_make_no_pair(tmp_path):
    """Records with nothing in common, or not yet read, are not paired."""
    rec(tmp_path, "a2000", models=[model("m", ["s"], ["s"])])
    rec(tmp_path, "b2010", models=[model("n", ["kg"], ["m"])])
    assert candidate_pairs(tmp_path, ["a2000", "b2010", "c2020"]) == {}


def test_the_real_corpus_pairs_every_related_paper():
    """On the three papers read so far, every pair the relate agent linked is found."""
    root = Path(__file__).resolve().parents[1] / "records"
    got = candidate_pairs(root, ["bell1978", "chan2008", "erdmann2004"])
    assert set(got) == {("bell1978", "chan2008"), ("bell1978", "erdmann2004"), ("chan2008", "erdmann2004")}


def test_a_shape_alone_lists_a_pair_but_does_not_relate_it():
    """Only pairs with a citation, a model described from the other, or a request in the corpus list get a relation
    job; a pair whose only sign is two models of the same shape is listed for a person, not run."""
    from pipeline.pairs import split_pairs

    pairs = {("a", "b"): ["a cites b (ref-1)", "a/m and b/n have the same shape (rate from force, rate)"],
             ("a", "c"): ["a/m and c/k have the same shape (rate from force, rate)"],
             ("b", "c"): ["the corpus list asks for it (b: relate_with)"]}
    run, listed = split_pairs(pairs)
    assert sorted(run) == [("a", "b"), ("b", "c")] and list(listed) == [("a", "c")]
