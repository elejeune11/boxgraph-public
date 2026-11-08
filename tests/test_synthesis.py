"""The Synthesis (04-synthesis.md): verdicts, cross-paper checks, cited
values, findings, implications, references; and order independence."""

import shutil
from pathlib import Path

import pytest

from boxgraph.synthesis import build_synthesis

FX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def syn(tmp_path_factory):
    root = tmp_path_factory.mktemp("records")
    for name in ("toy", "toy2"):
        shutil.copytree(FX / name, root / name)
    return build_synthesis(root, cache_dir=tmp_path_factory.mktemp("cache"))


def kinds(syn):
    return {f["kind"] for f in syn["findings"]}


def test_every_sound_record_enters(syn):
    """Every sound record enters the Synthesis."""
    assert set(syn["papers"]) == {"toy", "toy2"}
    assert all(p["sound"] for p in syn["papers"].values()), {k: p["errors"] for k, p in syn["papers"].items()}


def test_entering_never_requires_reproducing(syn):
    """A paper enters the Synthesis even when its results do not reproduce."""
    toy = syn["papers"]["toy"]
    assert any(v["verdict"] == "not reproduced" for v in toy["verdicts"])


def test_per_paper_verdicts(syn):
    """Each paper has verdicts for its comparisons."""
    v = {x["comparison"]: x["verdict"] for x in syn["papers"]["toy"]["verdicts"]}
    assert v["cmp_good"] == "reproduced"
    assert v["cmp_log"] == "not reproduced"


def test_finding_value_does_not_follow(syn):
    """A value that does not follow from its own inputs is a finding that traces to its page."""
    f = [f for f in syn["findings"] if f["kind"] == "not_reproduced"]
    assert any(x["subject"] == "toy/logt_printed" for x in f)
    one = next(x for x in f if x["subject"] == "toy/logt_printed")
    assert one["page"] == 2  # traces to the page


def test_finding_numerics(syn):
    """A result that belongs to its numerics is a finding."""
    assert any(f["kind"] == "belongs_to_numerics" and "ref_drift" in f["subject"] for f in syn["findings"])


def test_finding_refuted_stated_relation(syn):
    """A stated relation that is refuted is a finding."""
    assert any(f["kind"] == "refuted_relation" and f["subject"] == "toy2/rel_wrong" for f in syn["findings"])


def test_finding_depends_on_added_input(syn):
    """A verdict that flips under an alternative added input is a finding."""
    assert any(f["kind"] == "depends_on_added_input" and f["subject"] == "toy/xb_added" for f in syn["findings"])


def test_cited_value_checked_without_any_relation(syn):
    """A value said to come from another paper, named by record or by reference, is checked against it, without any relation."""
    c = {x["datum"]: x for x in syn["cited_values"]}
    assert c["toy2/k0_cited"]["verdict"] == "not reproduced"
    assert c["toy2/k0_cited_ok"]["verdict"] == "reproduced"
    assert c["toy2/k0_cited_elsewhere"]["status"] == "cited source not in the record"
    assert c["toy2/k0_cited_by_ref"]["verdict"] == "reproduced"  # a reference id resolves through references.yaml
    assert c["toy2/k0_cited_linked"]["verdict"] == "reproduced"  # which value, named afterwards in cited.yaml
    neg = c["toy2/k0_cited_negated"]  # a stated sign convention is applied, and shown
    assert neg["verdict"] == "reproduced" and "opposite sign" in neg["convention"]
    assert all(f["subject"] != "toy2/k0_cited_negated" for f in syn["findings"])
    finding = next(f for f in syn["findings"] if f["subject"] == "toy2/k0_cited")
    assert "toy" in finding["detail"]
    assert any(f["kind"] == "cited_value" and f["subject"] == "toy2/k0_cited" for f in syn["findings"])


def test_cross_paper_check_lists_its_correspondences(syn):
    """A cross-paper run lists the quantity correspondences and added inputs it rests on."""
    xs = [x for x in syn["cross_checks"] if x["relation"] == "toy2/rel_same"]
    assert xs, syn["cross_checks"]
    for x in xs:
        assert x["correspondences"], x
        assert x["verdict"] in ("reproduced", "close", "not reproduced", "no verdict")
    # a's model on b's inputs reproduces b's printed result
    fwd = [x for x in xs if x["model"] == "toy/decay" and x["printed"] == "toy2/tau_printed"]
    assert fwd and fwd[0]["verdict"] == "reproduced"
    assert fwd[0]["added"], "inputs the other paper does not state are labelled as added"


def test_linked_is_not_checked(syn):
    """Papers linked only by a limit relation get no cross-paper check."""
    # rel_limit links toy/decay and toy2/zeroforce but gives no cross-paper check
    assert not any(x["relation"] == "toy2/rel_limit" for x in syn["cross_checks"])


def test_families(syn):
    """Families are reported in the Synthesis."""
    assert ["toy/decay", "toy2/lifetime"] in syn["families"]


def test_implications_reach_other_papers(syn):
    """What a finding puts in doubt is followed downstream, into other papers."""
    f = next(f for f in syn["findings"] if f["kind"] == "not_reproduced" and f["subject"] == "toy/logt_printed")
    assert "implicates" in f
    # the cited k0 is upstream, not downstream: nothing should implicate it from logt
    assert "toy2/k0_cited" not in f["implicates"]
    g = syn["implications_of"]("toy/k0")
    assert "toy2/k0_cited" in g and "toy/t_pred" in g


def test_references_rank_what_to_read_next(syn):
    """Cited works not in the record are ranked by how many open questions they would settle."""
    refs = syn["references"]
    absent = next(r for r in refs if r["label"] == "2")
    assert not absent["in_record"] and "toy2/q_absent" in absent["would_settle"]
    assert refs[0]["label"] == "2"  # the most useful next read comes first


def test_order_independence(tmp_path):
    """The Synthesis is the same whatever order papers were added in (principle 11)."""
    a, b = tmp_path / "a", tmp_path / "b"
    for root, order in ((a, ["toy", "toy2"]), (b, ["toy2", "toy"])):
        root.mkdir()
        for n in order:
            shutil.copytree(FX / n, root / n)
    sa = build_synthesis(a, cache_dir=tmp_path / "c")
    sb = build_synthesis(b, cache_dir=tmp_path / "c")
    for k in ("findings", "families", "cross_checks", "cited_values", "references"):
        assert sa[k] == sb[k], k


def test_relation_ids_from_two_records_do_not_collide(tmp_path):
    """Relations with the same local id in two records do not collide."""
    import yaml

    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    # the same local id in toy, for a relation that is refuted
    rel = {"id": "rel_same", "kind": "same_as", "a": "toy/decay", "b": "toy2/wrongsign",
           "mapping": {"tau0": "1/k0", "f": "F", "fb": "kT/xb"},
           "regime": {"k0": [0.01, 10], "F": [1, 20], "xb": [0.1, 2], "kT": [4.0, 4.3]},
           "provenance": "proposed", "reason": "collision test"}
    (root / "toy" / "relations.yaml").write_text(yaml.safe_dump([rel]))
    s = build_synthesis(root, cache_dir=tmp_path / "c")
    assert ["toy/decay", "toy2/lifetime"] in s["families"]
    assert not any("toy2/wrongsign" in f for f in s["families"])


def test_an_unsound_record_is_listed_not_crashed_on(tmp_path):
    """An unsound record is reported as not sound and kept out of the checks; the build goes on."""
    import yaml

    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    qs = yaml.safe_load((root / "toy" / "quantities.yaml").read_text())
    (root / "toy" / "quantities.yaml").write_text(yaml.safe_dump([q for q in qs if q["id"] != "force"]))
    s = build_synthesis(root, cache_dir=tmp_path / "c")
    assert s["papers"]["toy"]["sound"] is False
    assert any("unknown quantity" in e for e in s["papers"]["toy"]["errors"])
    assert s["papers"]["toy2"]["sound"] is True
    assert not any(f["source"] == "toy" for f in s["findings"])


def test_one_finding_per_problem_with_all_its_evidence(syn):
    """Each problem is one finding; several comparisons or alternatives behind it are listed as its evidence."""
    keys = [(f["kind"], f["subject"]) for f in syn["findings"]]
    assert len(keys) == len(set(keys))
    dep = next(f for f in syn["findings"] if f["kind"] == "depends_on_added_input" and f["subject"] == "toy/xb_added")
    assert len(dep["evidence"]) == 2  # the 1.0 nm and the 0.51 nm alternatives


def test_a_table_finding_names_the_rows_that_fail(tmp_path):
    """A not-reproduced table says which rows fail, with printed and computed values, and that the rest reproduce."""
    import yaml

    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    data = yaml.safe_load((root / "toy" / "data.yaml").read_text())
    curve = next(d for d in data if d["id"] == "t_curve")
    curve["table"]["values"][2] = "9.9"
    (root / "toy" / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    s = build_synthesis(root, cache_dir=tmp_path / "c")
    f = next(f for f in s["findings"] if f["kind"] == "not_reproduced" and f["subject"] == "toy/t_curve")
    assert "at force = 10" in f["detail"] and "printed 9.9" in f["detail"]
    assert "2 other values reproduce" in f["detail"]


def test_verdicts_are_tallied_by_purpose(syn):
    """Verdicts are counted for every purpose, not only reproduction."""
    t = syn["papers"]["toy"]["tally_by_purpose"]
    assert t["reproduction"]["reproduced"] == 2 and t["reproduction"]["not reproduced"] == 1


def test_a_build_evaluates_each_record_once(tmp_path, monkeypatch):
    """The Synthesis evaluates each record once (besides its added inputs' alternatives) and reuses that for cross-paper checks."""
    from boxgraph import engine

    for name in ("toy", "toy2"):
        shutil.copytree(FX / name, tmp_path / "r" / name)
    calls = []
    real = engine.Builder.evaluate
    monkeypatch.setattr(engine.Builder, "evaluate",
                        lambda self, overrides=None: (overrides or calls.append(self.rec.source.id)) and None
                        or real(self, overrides))
    syn = build_synthesis(tmp_path / "r", cache_dir=tmp_path / "c")
    assert syn["cross_checks"], "the fixtures must have a cross-paper check for this test to mean anything"
    assert sorted(calls) == ["toy", "toy2"]


def test_a_second_build_runs_nothing_again(tmp_path, monkeypatch):
    """With the cache of an earlier build, a rebuild of unchanged records starts no model, relation test or figure reading."""
    import subprocess

    from boxgraph import engine

    for name in ("toy", "toy2"):
        shutil.copytree(FX / name, tmp_path / "r" / name)
    first = build_synthesis(tmp_path / "r", cache_dir=tmp_path / "c")
    engine._CACHE.clear()  # a new process
    started = []
    real = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: started.append(a[0]) or real(*a, **k))
    second = build_synthesis(tmp_path / "r", cache_dir=tmp_path / "c")
    assert started == []
    for k in ("findings", "families", "cross_checks", "relations"):
        assert first[k] == second[k], k


def test_reordering_a_records_files_changes_nothing(tmp_path):
    """Reversing every list in a record's YAML files gives the same Synthesis (principle 11: sort everything)."""
    import yaml

    for name in ("toy", "toy2"):
        shutil.copytree(FX / name, tmp_path / "a" / name)
        shutil.copytree(FX / name, tmp_path / "b" / name)
        for f in (tmp_path / "b" / name).glob("*.yaml"):
            data = yaml.safe_load(f.read_text())
            if isinstance(data, list):
                f.write_text(yaml.safe_dump(list(reversed(data)), sort_keys=False, allow_unicode=True))
    sa = build_synthesis(tmp_path / "a", cache_dir=tmp_path / "c")
    sb = build_synthesis(tmp_path / "b", cache_dir=tmp_path / "c")
    for k in ("findings", "families", "cross_checks", "cited_values", "references", "relations"):
        assert sa[k] == sb[k], k


def test_each_source_says_what_kind_of_source_it_is(syn):
    """Each source in the Synthesis names its kind (article, software, dataset, ...) and its venue."""
    import yaml
    src = yaml.safe_load((FX / "toy" / "source.yaml").read_text())
    assert syn["papers"]["toy"]["kind"] == src["kind"]
    assert syn["papers"]["toy"]["venue"] == src.get("venue")


def test_correspondences_read_names_that_are_sympy_functions():
    """A mapping whose input is named like a sympy function (gamma, beta) is read as that input."""
    from types import SimpleNamespace as NS

    from boxgraph.synthesis import _correspondences

    port = lambda q: NS(quantity=q)  # noqa: E731
    ma = NS(inputs={"gamma": port("area_ratio"), "beta": port("exponent")})
    mb = NS(inputs={"eta": port("area_ratio")})
    rel = NS(mapping={"eta": "(1 + gamma)/(1 + gamma**(beta/2))**(2/beta)"})
    pairs = _correspondences(rel, "a", ma, "b", mb)
    assert pairs == sorted(pairs) and len(pairs) == 2, pairs


def _verified(monkeypatch, rel_id):
    """Have the atlas call one relation verified, so its cross-paper checks run."""
    from dataclasses import replace

    import boxgraph.synthesis as S

    orig = S.test_relation

    def fake(rel, *a, **k):
        r = orig(rel, *a, **k)
        return replace(r, status="verified", too_plain=False) if rel.id == rel_id else r

    monkeypatch.setattr(S, "test_relation", fake)


def test_a_cross_paper_run_that_gives_no_value_is_not_checked(tmp_path, monkeypatch):
    """A cross-paper run whose model gives no value (NaN) is listed as not checked, with why; the build goes on."""
    import boxgraph.synthesis as S

    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)

    class NoValue(dict):
        def __missing__(self, k):
            return None

    monkeypatch.setattr(S, "execute", lambda *a, **k: [NoValue()])
    s = build_synthesis(root, cache_dir=tmp_path / "c")
    xs = [x for x in s["cross_checks"] if x["relation"] == "toy2/rel_same"]
    assert xs and all(x["status"].startswith("not checked") and "no value" in x["status"] for x in xs), xs


def test_a_mapping_that_cannot_be_evaluated_is_not_checked(tmp_path, monkeypatch):
    """A cross-paper mapping that cannot be evaluated on a run's inputs (a division by zero) is not checked, with why."""
    import yaml

    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    rels = yaml.safe_load((root / "toy2" / "relations.yaml").read_text())
    rels.append({"id": "rel_pole", "kind": "same_as", "a": "toy/decay", "b": "toy2/lifetime",
                 "mapping": {"tau0": "1000/(5*k0 - 1)", "f": "F", "fb": "kT/xb"}, "output_map": {"tau": "t"},
                 "regime": {"k0": [0.01, 10], "F": [0, 20], "xb": [0.1, 2], "kT": [4.0, 4.3]},
                 "provenance": "proposed", "reason": "test fixture; a pole at the run's k0"})
    (root / "toy2" / "relations.yaml").write_text(yaml.safe_dump(rels))
    _verified(monkeypatch, "rel_pole")
    s = build_synthesis(root, cache_dir=tmp_path / "c")
    xs = [x for x in s["cross_checks"] if x["relation"] == "toy2/rel_pole" and x["model"] == "toy2/lifetime"]
    assert xs and all(x["status"].startswith("not checked") for x in xs), xs


def test_finding_inputs_through_a_transcendental_mapping_is_quick():
    """Inverting a mapping with an exponential for the other model's inputs ends within a time budget, never stalling the build."""
    from types import SimpleNamespace as NS

    from boxgraph.synthesis import _solve_inputs

    ma = NS(inputs={n: None for n in ("rho", "k1", "k2", "k3", "D0")})
    rel = NS(mapping={"Lp": "4*rho/(pi*D0**2)", "Cp": "3*pi*D0**2/(8*(k1*exp(k2*D0/2) + k3))"})
    own = {"rho": 1.06, "k1": 2.0e6, "k2": -22.53, "k3": 8.65e4, "D0": 0.79}

    import time

    from boxgraph.synthesis import SOLVE_SECONDS, SolveTooSlow

    t0 = time.monotonic()
    try:
        vals, free = _solve_inputs(rel, ma, None, {"Lp": 0.15, "Cp": 0.000027}, own)
    except SolveTooSlow:
        vals = None  # reported as not checked, with the reason
    assert time.monotonic() - t0 < SOLVE_SECONDS + 5
    if vals is not None:  # whatever is found must satisfy the mapping it came from
        assert abs(4 * vals["rho"] / (3.141592653589793 * vals["D0"] ** 2) - 0.15) < 1e-6 * 0.15


def test_complex_roots_of_a_mapping_are_skipped(monkeypatch):
    """When the solver returns complex roots beside the real one, the real positive input is used and the complex ones are skipped."""
    from types import SimpleNamespace as NS

    import sympy as sp

    import boxgraph.synthesis as syn

    x = sp.Symbol("x", positive=True)
    monkeypatch.setattr(syn.sp, "solve", lambda *a, **k: [{x: 1 + 2 * sp.I}, {x: sp.Integer(3)}])
    vals, free = syn._solve_inputs(NS(mapping={"y": "x**3"}), NS(inputs={"x": None}), None, {"y": 27.0}, None)
    assert vals == {"x": 3.0} and free == []
