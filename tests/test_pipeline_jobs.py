"""The job graph for reading the corpus."""

import subprocess
from pathlib import Path

import pytest

import pipeline.run_papers as _rp
from pipeline.run_papers import jobs, papers, pending, plan, relate_jobs, select, validate_jobs


@pytest.fixture(autouse=True)
def _real_paper_list(monkeypatch):
    """The job graph is built from the repository's motor_clutch paper list; paths keep the generic layout."""
    monkeypatch.setattr(_rp, "PAPERS", Path(__file__).resolve().parents[1] / "corpora" / "motor_clutch" / "papers.yaml")


def test_audit_passes_only_with_an_audit_log(tmp_path):
    """An audit job fails its gate unless the record is sound and the audit log was written."""
    js = jobs("m", 1, 1, 1)
    audit = js["audit"][0]
    cmd = " ".join(audit.validate)
    assert "audit.md" in cmd and "boxgraph validate" in cmd
    r = subprocess.run(audit.validate[:2] + [audit.validate[2].replace(".venv/bin/boxgraph validate", "true")],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode != 0 and "audit.md" in r.stdout


def test_agents_can_write_only_inside_their_record():
    """Readers and auditors may write only inside their own record directory."""
    js = jobs("m", 1, 1, 1)
    for j in js["read"] + js["audit"]:
        rid = j.id.split(":")[1]
        writes = [t for t in j.allowed_tools if t.startswith(("Write(", "Edit("))]
        assert writes and all(t.endswith(f"records/{rid}/**)") for t in writes)
        # both the project-relative and the absolute form, so any path an agent uses matches
        assert any(t.startswith("Edit(//") for t in writes) and f"Edit(records/{rid}/**)" in writes


def test_relate_jobs_are_per_pair_and_may_not_change_data():
    """A relation job joins two records and may edit their relations, questions, quantities and models, never data or other records."""
    (j,) = relate_jobs({("bell1978", "erdmann2004"): ["a reason"]}, "m", 1)
    assert j.id == "relate:bell1978+erdmann2004" and sorted(j.locks) == ["bell1978", "erdmann2004"]
    for rid in ("bell1978", "erdmann2004"):
        assert f"Edit(records/{rid}/quantities.yaml)" in j.allowed_tools
        assert f"Edit(records/{rid}/relations.yaml)" in j.allowed_tools
        assert not any(f"records/{rid}/data.yaml" in t for t in j.allowed_tools)
    assert not any("chan2008" in t for t in j.allowed_tools)
    assert "a reason" in j.prompt and "bell1978" in j.prompt and "erdmann2004" in j.prompt


def test_relate_gate_runs_both_records_and_checks_the_relations():
    """A relation job may touch models, so its gate validates both records with their models run (from the shared cache), then tests the pair's relations."""
    (j,) = relate_jobs({("a", "b"): ["r"]}, "m", 1)
    gate = " ".join(j.validate)
    assert "validate records/a records/b" in gate and "--no-run" not in gate
    assert "boxgraph relations records --only a,b" in gate


def test_pair_jobs_check_their_work_in_their_own_folder():
    """Two relation jobs never share a scratch build folder."""
    js = relate_jobs({("a", "b"): ["r"], ("a", "c"): ["r"]}, "m", 1)
    assert "build/relate-check/a+b" in js[0].prompt and "build/relate-check/a+c" in js[1].prompt


def test_digitize_runs_after_the_audit():
    """Each paper's figure job waits for its audit, since both edit the record."""
    js = jobs("m", 1, 1, 1)
    for d in js["digitize"]:
        assert d.depends_on == ["audit:" + d.id.split(":")[1]]


def test_per_paper_gates_share_the_model_run_cache():
    """Read, audit and figure gates validate with the build cache, so a retry does not rerun every simulation."""
    js = jobs("m", 1, 1, 1)
    for j in js["read"] + js["audit"] + js["digitize"]:
        assert "--cache build/cache" in " ".join(j.validate), j.id


def test_finished_jobs_are_not_run_again():
    """Jobs in the ledger are skipped unless a rerun is asked for."""
    js = select(jobs("m", 1, 1, 1), ["read", "audit"], None)
    done = {"read:bell1978": {}, "audit:bell1978": {}}
    left = [j.id for j in pending(js, done)]
    assert "read:bell1978" not in left and "audit:bell1978" not in left and "read:chan2008" in left
    assert len(pending(js, done, rerun=True)) == len(js)


def test_digitize_jobs_may_read_figures_and_must_log_them():
    """Each paper gets a figure-reading job that can use the figure commands, writes only its record, and must log its readings."""
    js = jobs("m", 1, 1, 1)
    ds = js["digitize"]
    assert {j.id for j in ds} == {f"digitize:{p['id']}" for p in papers() if not p.get("kind")}  # papers only
    for j in ds:
        rid = j.id.split(":")[1]
        assert "Bash(.venv/bin/boxgraph figure:*)" in j.allowed_tools
        writes = [t for t in j.allowed_tools if t.startswith(("Write(", "Edit("))]
        assert all(t.endswith(f"records/{rid}/**)") for t in writes)
        gate = " ".join(j.validate)
        assert "figures.md" in gate and "boxgraph validate" in gate


def test_stages_can_be_run_for_some_papers_only():
    """`--papers` keeps only the chosen papers' jobs, and the relation jobs of pairs that include one of them."""
    js = jobs("m", 1, 1, 1)
    ids = [j.id for j in select(js, ["digitize"], ["chan2008"])]
    assert ids == ["digitize:chan2008"]
    rel = relate_jobs({("a", "b"): ["r"], ("b", "c"): ["r"], ("c", "d"): ["r"]}, "m", 1)
    assert [j.id for j in select({"relate": rel}, ["relate"], ["b"])] == ["relate:a+b", "relate:b+c"]


def test_an_extra_instruction_reaches_every_selected_job():
    """`--extra` text is appended to each job's prompt, for a pass with its own purpose."""
    js = jobs("m", 1, 1, 1, extra="Reread each figure with your own code.")
    assert all(j.prompt.rstrip().endswith("Reread each figure with your own code.") for s in js.values() for j in s)
    (r,) = relate_jobs({("a", "b"): ["r"]}, "m", 1, extra="Reread each figure with your own code.")
    assert r.prompt.rstrip().endswith("Reread each figure with your own code.")


def test_the_plan_says_what_will_run_and_what_is_done():
    """The dry-run plan lists each job as done or to run with its budget cap, and the total cap."""
    js = select(jobs("m", 2, 1, 1), ["read"], None)
    text = "\n".join(plan(js, {"read:bell1978": {"date": "2026-10-30", "cost_usd": 3.5}}))
    assert "read:bell1978" in text and "done 2026-10-30" in text
    assert "read:chan2008" in text and "to run" in text
    n = len(js) - 1
    assert f"at most ${2 * n:.0f}" in text


def test_agents_share_the_gates_cache():
    """Every agent job runs with BOXGRAPH_CACHE set to the cache its gate uses, so a gate never reruns what the agent ran."""
    from pipeline.run_papers import CACHE, ROOT

    js = jobs("m", 1, 1, 1)
    rel = relate_jobs({("a", "b"): ["test"]}, "m", 1)
    for j in [*js["read"], *js["audit"], *js["digitize"], *rel]:
        assert j.env.get("BOXGRAPH_CACHE") == str(ROOT / CACHE), j.id


def test_relate_jobs_may_name_cited_values_in_both_records():
    """A relation job may write cited.yaml in both of its records, to say which value a cited value matches, but not data.yaml."""
    (j,) = relate_jobs({("a", "b"): ["test"]}, "m", 1)
    tools = " ".join(j.allowed_tools)
    assert "records/a/cited.yaml" in tools and "records/b/cited.yaml" in tools
    assert "data.yaml" not in tools


def test_single_jobs_can_be_chosen_by_id():
    """`--jobs` keeps only the named jobs, so one job can be run again without its neighbours."""
    rel = relate_jobs({("a", "b"): ["r"], ("b", "c"): ["r"], ("c", "d"): ["r"]}, "m", 1)
    assert [j.id for j in select({"relate": rel}, ["relate"], None, job_ids=["relate:b+c"])] == ["relate:b+c"]



def _pin(rp, monkeypatch, ledger=None):
    """Name the repository's motor_clutch corpus, restore the pipeline's paths afterwards, and keep its ledger in a scratch file."""
    for name in ("PAPERS", "LEDGER", "RECORDS", "BUILD", "OVERVIEW", "STATE"):
        monkeypatch.setattr(rp, name, getattr(rp, name))
    if ledger is not None:
        orig = rp.use_corpus

        def use(name):
            orig(name)
            rp.LEDGER = ledger
        monkeypatch.setattr(rp, "use_corpus", use)
    return ["--corpus", "motor_clutch"]


def test_a_rerun_resets_the_chosen_jobs_state(tmp_path, monkeypatch):
    """`--rerun` forgets the chosen jobs' state on this machine as well as skipping the ledger, so they really run again."""
    import pipeline.run_papers as rp

    seen = {}
    monkeypatch.setattr(rp.Orchestrator, "reset", lambda self, ids: seen.setdefault("reset", sorted(ids)))
    monkeypatch.setattr(rp, "_run", lambda o, todo, done=None: {})
    monkeypatch.setattr(rp, "candidate_pairs", lambda *a, **k: {})
    monkeypatch.setattr(rp, "check_papers", lambda *a: [])  # the PDFs are not in git
    rp.main([*_pin(rp, monkeypatch, tmp_path / "completed.yaml"), "--stages", "read", "--papers", "chan2008", "--rerun",
             "--state", str(tmp_path / "st")])
    assert seen["reset"] == ["read:chan2008"]


def test_every_job_says_where_it_may_write_and_what_it_must_write():
    """Each job lists the paths it may change (anything else fails it) and the log it must write itself."""
    js = jobs("m", 1, 1, 1)
    for j in js["read"]:
        rid = j.id.split(":")[1]
        assert f"records/{rid}/**" in j.writable
        assert [w for w in j.writable if w.startswith("pipeline/")] == ["pipeline/completed.yaml"]  # the run's ledger only
    for stage, log in (("audit", "audit.md"), ("digitize", "figures.md")):
        for j in js[stage]:
            assert j.fresh == [f"records/{j.id.split(':')[1]}/{log}"]
    (r,) = relate_jobs({("a", "b"): ["r"]}, "m", 1)
    assert "records/a/relations.yaml" in r.writable and "records/b/cited.yaml" in r.writable
    assert not any("data.yaml" in w for w in r.writable)


def test_agents_get_no_shell_route_to_write_files():
    """Agents read files with the Read tool; the shell commands they are given cannot write (sed's w command, for one)."""
    js = jobs("m", 1, 1, 1)
    for j in [*js["read"], *js["audit"], *js["digitize"], *relate_jobs({("a", "b"): ["r"]}, "m", 1)]:
        assert not any(t.startswith("Bash(sed") for t in j.allowed_tools), j.id


def _main(monkeypatch, tmp_path, argv, results=None):
    import pipeline.run_papers as rp

    monkeypatch.setattr(rp, "check_papers", lambda *a: [])  # the PDFs are not in git
    corpus = _pin(rp, monkeypatch, tmp_path / "completed.yaml")
    monkeypatch.setattr(rp, "_run", lambda o, todo, done=None: {j.id: dict(results or {}).get(j.id, {"status": "passed"})
                                                                 for j in todo})
    monkeypatch.setattr(rp, "candidate_pairs", lambda *a, **k: {})
    monkeypatch.setattr(rp, "_build", lambda title: 0)
    return rp.main([*corpus, *argv, "--state", str(tmp_path / "st")])


def test_only_one_run_at_a_time(tmp_path, monkeypatch):
    """A second run on the same state folder refuses to start while the first holds its lock."""
    import fcntl

    (tmp_path / "st").mkdir()
    with open(tmp_path / "st" / "run.lock", "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert _main(monkeypatch, tmp_path, ["--stages", "read", "--papers", "chan2008"]) == 3


def test_the_exit_code_says_whether_anything_needs_a_person(tmp_path, monkeypatch):
    """A run exits 0 only when every selected job passed; a parked or blocked job makes it exit 1."""
    assert _main(monkeypatch, tmp_path, ["--stages", "read", "--papers", "chan2008", "--rerun"]) == 0
    bad = {"read:chan2008": {"status": "parked", "error": "x"}}
    assert _main(monkeypatch, tmp_path, ["--stages", "read", "--papers", "chan2008", "--rerun"], bad) == 1


def test_a_job_can_be_reset_from_the_command_line(tmp_path, monkeypatch):
    """`--reset JOB` forgets a job's state on this machine (a parked job then runs again) and runs nothing."""
    import pipeline.run_papers as rp

    seen = {}
    monkeypatch.setattr(rp.Orchestrator, "reset", lambda self, ids: seen.setdefault("reset", list(ids)))
    assert _main(monkeypatch, tmp_path, ["--reset", "read:chan2008"]) == 0
    assert seen["reset"] == ["read:chan2008"]


def test_a_changed_pdf_clears_that_papers_finished_jobs():
    """When a paper's PDF or page range changes, its finished jobs leave the ledger, so they run again on the new file."""
    from pipeline.run_papers import _stale_rows

    done = {"read:a": {}, "audit:a": {}, "digitize:a": {}, "read:b": {}, "relate:a+b": {}, "relate:b+c": {},
            "validate:a+b": {}, "validate:b+c": {}}
    assert sorted(_stale_rows(done, "a")) == ["audit:a", "digitize:a", "read:a", "relate:a+b", "validate:a+b"]


def test_a_changed_pdf_resets_that_papers_jobs_on_this_machine(tmp_path, monkeypatch):
    """When a paper's PDF or page range changes, its finished jobs are also forgotten in this machine's state, so they really run again."""
    import pipeline.run_papers as rp
    from pipeline.corpus import record_completed

    record_completed(tmp_path / "completed.yaml", [{"job": j, "date": "2026-01-01", "cost_usd": 0, "turns": 0}
                                                   for j in ("read:chan2008", "audit:chan2008", "read:other")])
    seen = {}
    monkeypatch.setattr(rp.Orchestrator, "reset", lambda self, ids: seen.setdefault("reset", sorted(ids)))
    monkeypatch.setattr(rp, "_ingest_needed", lambda p: p["id"] == "chan2008")
    monkeypatch.setattr(rp, "ingest", lambda *a, **k: tmp_path / "rec")
    _main(monkeypatch, tmp_path, ["--stages", "ingest", "--papers", "chan2008"])
    assert seen["reset"] == ["audit:chan2008", "read:chan2008"]


def test_code_and_data_get_one_reading_job_after_their_papers(monkeypatch):
    """A software or dataset entry gets one job of its own kind, after its papers are read, writing only its record;
    papers keep read, audit and digitize."""
    import pipeline.run_papers as rp

    monkeypatch.setattr(rp, "papers", lambda: [
        {"id": "p2020", "file": "corpus/p.pdf", "pages": [1, 2]},
        {"id": "p_code", "kind": "software", "file": "corpus/code/p_code", "papers": ["p2020"]},
        {"id": "p_data", "kind": "dataset", "file": "corpus/data/p_data.xlsx", "papers": ["p2020"]}])
    js = rp.jobs("m", 1, 1, 1)
    assert [j.id for j in js["read"]] == ["read:p2020", "read:p_code", "read:p_data"]
    assert [j.id for j in js["audit"]] == ["audit:p2020"] and [j.id for j in js["digitize"]] == ["digitize:p2020"]
    code = next(j for j in js["read"] if j.id == "read:p_code")
    assert code.depends_on == ["read:p2020"] and "records/p_code/**" in code.writable
    assert not any(w.startswith("records/") and w != "records/p_code/**" for w in code.writable)
    assert "Read the code" in code.prompt and "corpus/code/p_code" in code.prompt
    data = next(j for j in js["read"] if j.id == "read:p_data")
    assert "Read the data" in data.prompt
    assert rp.stages_of({"id": "p_code", "kind": "software"}) == ("read",)


def test_the_ledger_written_during_a_run_is_never_a_stray_write():
    """The run writes the ledger as each job passes, so no job's write check counts that as the agent's write."""
    from pipeline.run_papers import LEDGER, ROOT

    rel = LEDGER.relative_to(ROOT).as_posix()
    js = jobs("m", 1, 1, 1)
    for j in [*js["read"], *js["audit"], *js["digitize"], *relate_jobs({("a", "b"): ["r"]}, "m", 1)]:
        assert rel in j.writable, j.id


def test_a_stopped_run_says_how_to_resume(tmp_path, monkeypatch, capsys):
    """When a run is stopped (Ctrl-C, SIGTERM), it says so in a line and exits 130 instead of a traceback."""
    import asyncio

    def stop(*a, **k):
        raise asyncio.CancelledError

    rc = _main(monkeypatch, tmp_path, ["--stages", "read", "--papers", "chan2008", "--rerun"])
    assert rc == 0
    import pipeline.run_papers as rp

    monkeypatch.setattr(rp, "_run", stop)
    rc = rp.main(["--corpus", "motor_clutch", "--stages", "read", "--papers", "chan2008", "--rerun", "--state", str(tmp_path / "st")])
    assert rc == 130 and "run again to resume" in capsys.readouterr().out


def test_validate_jobs_are_per_pair_and_write_only_validations_added_inputs_and_questions():
    """A validation job per pair may write only the two records' validations, added inputs and questions; never their data, models or comparisons."""
    (j,) = validate_jobs({("craig2015", "gardel2008"): ["a reason"]}, "m", 1)
    assert j.id == "validate:craig2015+gardel2008" and j.locks == ["craig2015", "gardel2008"]
    for rid in ("craig2015", "gardel2008"):
        for f in ("validations.yaml", "added.yaml", "questions.yaml"):
            assert f"records/{rid}/{f}" in j.writable
    assert not any(w.endswith(("data.yaml", "comparisons.yaml", "runs.yaml")) or "models" in w for w in j.writable)


def test_validate_gate_runs_both_records_and_checks_their_validations():
    """A validation job passes only when both records are sound with their models run and every validation between them can be checked."""
    (j,) = validate_jobs({("a", "b"): ["r"]}, "m", 1)
    gate = " ".join(j.validate)
    assert "validate records/a records/b" in gate and "validations records --only a,b" in gate


def test_validation_jobs_are_kept_when_their_stage_is_chosen():
    """Validation jobs are selected like relation jobs: by stage, by paper, and by id."""
    val = validate_jobs({("a", "b"): ["r"], ("c", "d"): ["r"]}, "m", 1)
    assert [j.id for j in select({"validate": val}, ["validate"], ["a"])] == ["validate:a+b"]
    assert select({"validate": val}, ["relate"], None) == []


def test_the_eval_readers_prompt_formats_and_points_at_the_eval_records():
    """The eval reader's prompt fills every placeholder of the read prompt and names records_eval/, never records/."""
    from pipeline.evals.run import reader_prompt

    p = reader_prompt("synth1", "pipeline/evals/x (text only)", 3, "text only", "m")
    assert "records_eval/synth1/" in p and "`records/" not in p and "{records}" not in p
