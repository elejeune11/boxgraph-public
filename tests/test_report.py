"""The written review: every sentence traces back to the records
(04-synthesis.md), and a tracer refuses any that does not."""

import shutil
from pathlib import Path

import pytest

from boxgraph.report import Sentence, build_index, render_html, render_markdown, review, trace_check
from boxgraph.synthesis import build_synthesis

FX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def syn(tmp_path_factory):
    root = tmp_path_factory.mktemp("records")
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    return build_synthesis(root, cache_dir=tmp_path_factory.mktemp("cache"))


def test_every_generated_sentence_traces(syn):
    """Every sentence of the generated review traces to the records."""
    sents = review(syn)
    assert len(sents) > 5
    assert all(s.trace for s in sents)
    assert trace_check(sents, build_index(syn)) == []


def test_review_mentions_every_finding(syn):
    """The review mentions every finding."""
    text = " ".join(s.text for s in review(syn))
    for f in syn["findings"]:
        assert f["subject"] in " ".join(t for s in review(syn) for t in s.trace)
    assert "not reproduced" in text


def test_tracer_refuses_untraced_sentence(syn):
    """A sentence with no trace is refused."""
    bad = [Sentence("The literature agrees.", [])]
    assert trace_check(bad, build_index(syn))


def test_tracer_refuses_unknown_ids(syn):
    """A sentence tracing to an unknown id is refused."""
    bad = [Sentence("Something about a ghost.", ["toy/ghost"])]
    assert any("unknown" in p for p in trace_check(bad, build_index(syn)))


def test_tracer_refuses_numbers_not_in_the_record(syn):
    """A sentence with a number that is not in what it traces to is refused."""
    bad = [Sentence("Toy prints log t = -99.9.", ["toy/logt_printed"])]
    assert any("-99.9" in p for p in trace_check(bad, build_index(syn)))
    good = [Sentence("Toy prints log t = -14.7.", ["toy/logt_printed"])]
    assert trace_check(good, build_index(syn)) == []


def test_markdown_and_html(syn, tmp_path):
    """The report renders as Markdown and as HTML with a dark theme."""
    md = render_markdown(syn, review(syn))
    html = render_html(syn, review(syn))
    for f in syn["findings"]:
        assert f["subject"] in md and f["subject"] in html
    assert html.lstrip().lower().startswith("<!doctype html>")
    assert "prefers-color-scheme" in html
    assert "overflow-wrap:anywhere" in html
    # findings come in order of importance: a result that does not follow comes first
    assert html.index("does not follow from the paper") < html.index("depends on an input the paper does not state")  # long ids wrap instead of widening the page on a phone
