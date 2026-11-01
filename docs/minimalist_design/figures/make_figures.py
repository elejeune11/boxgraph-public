# ruff: noqa: E501  (SVG markup and figure text read better on one line)
"""The figures of the minimalist design, each generated from its definition
here.

    python docs/minimalist_design/figures/make_figures.py

They show the ideas only: what is recorded, what is checked, how papers
connect. None of them says how the code is written or how agents work.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent

STYLE = """<style>
text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.th{font-size:14px;font-weight:500;fill:#2C2C2A}.ts{font-size:12px;fill:#5F5E5A}.tl{font-size:12px;fill:#444441;font-style:italic}
.box{fill:#F1EFE8;stroke:#888780}.rec{fill:none;stroke:#888780;stroke-dasharray:1.5 3}.region{fill:none;stroke:#B4B2A9;stroke-dasharray:6 4}
.c-purple>rect{fill:#EEEDFE;stroke:#534AB7}.c-purple>.th{fill:#3C3489}.c-purple>.ts{fill:#534AB7}
.c-teal>rect{fill:#E1F5EE;stroke:#0F6E56}.c-teal>.th{fill:#085041}.c-teal>.ts{fill:#0F6E56}
.c-coral>rect{fill:#FAECE7;stroke:#993C1D}.c-coral>.th{fill:#712B13}.c-coral>.ts{fill:#993C1D}
.c-green>rect{fill:#EAF3DE;stroke:#3B6D11}.c-green>.ts{fill:#27500A}
.c-amber>rect{fill:#FAEEDA;stroke:#854F0B}.c-amber>.ts{fill:#633806}
.c-red>rect{fill:#FCEBEB;stroke:#A32D2D}.c-red>.ts{fill:#791F1F}
rect.added{stroke-dasharray:5 3;stroke-width:1.5}
.arr{stroke:#888780;stroke-width:1.5;fill:none}.dash{stroke-dasharray:5 4}.dot{stroke-dasharray:1.5 3}.head{stroke:#888780}
.line{stroke:#888780;stroke-width:1;fill:none}.pt{fill:#534AB7}.pt2{fill:#993C1D}
@media (prefers-color-scheme:dark){.th{fill:#F1EFE8}.ts{fill:#B4B2A9}.tl{fill:#D3D1C7}.box{fill:#2C2C2A}
.c-purple>rect{fill:#3C3489;stroke:#AFA9EC}.c-purple>.th{fill:#EEEDFE}.c-purple>.ts{fill:#CECBF6}
.c-teal>rect{fill:#085041;stroke:#5DCAA5}.c-teal>.th{fill:#E1F5EE}.c-teal>.ts{fill:#9FE1CB}
.c-coral>rect{fill:#712B13;stroke:#F0997B}.c-coral>.th{fill:#FAECE7}.c-coral>.ts{fill:#F5C4B3}
.c-green>rect{fill:#27500A;stroke:#97C459}.c-green>.ts{fill:#EAF3DE}
.c-amber>rect{fill:#633806;stroke:#EF9F27}.c-amber>.ts{fill:#FAEEDA}
.c-red>rect{fill:#791F1F;stroke:#F09595}.c-red>.ts{fill:#FCEBEB}.pt{fill:#AFA9EC}.pt2{fill:#F0997B}}
</style>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path class="head" d="M2 1L8 5L2 9" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>"""


class Figure:
    def __init__(self, title, desc):
        self.title, self.desc, self.out = title, desc, []

    def text(self, x, y, s, cls="ts", anchor="start"):
        self.out.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central">{s}</text>')

    def node(self, cls, x, y, w, h, title, lines=(), added=False):
        """A box: cls is box (record or source), rec (a definition), or a colour."""
        extra = " added" if added else ""
        if cls in ("box", "rec"):
            rect = f'<rect class="{cls}{extra}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6" stroke-width="{1 if cls == "rec" else 0.5}"/>'
            group = ""
        else:
            rect = f'<rect{" class=" + chr(34) + extra.strip() + chr(34) if added else ""} x="{x}" y="{y}" width="{w}" height="{h}" rx="6" stroke-width="0.5"/>'
            group = f' class="{cls}"'
        top = y + h / 2 - 9 * len(lines)
        body = [rect, f'<text class="th" x="{x + w / 2}" y="{top}" text-anchor="middle" dominant-baseline="central">{title}</text>']
        for i, s in enumerate(lines, 1):
            body.append(f'<text class="ts" x="{x + w / 2}" y="{top + 19 * i}" text-anchor="middle" dominant-baseline="central">{s}</text>')
        self.out.append(f"<g{group}>" + "".join(body) + "</g>")

    def band(self, cls, x, y, w, h, label):
        self.out.append(f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" stroke-width="0.5"/>'
                        f'<text class="ts" x="{x + w / 2}" y="{y + h / 2}" text-anchor="middle" dominant-baseline="central">{label}</text></g>')

    def region(self, x, y, w, h):
        self.out.append(f'<rect class="region" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" stroke-width="1"/>')

    def edge(self, d, style="", arrow=True, both=False):
        marker = ' marker-end="url(#arrow)"' if arrow else ""
        if both:
            marker += ' marker-start="url(#arrow)"'
        self.out.append(f'<path class="arr {style}" d="{d}"{marker}/>')

    def raw(self, s):
        self.out.append(s)

    def svg(self, width, height):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">\n'
                f"<title>{self.title}</title>\n<desc>{self.desc}</desc>\n{STYLE}\n" + "\n".join(self.out) + "\n</svg>\n")


def evaluating_models():
    f = Figure("A syntax for evaluating models", "Left: a usual knowledge graph records claims about models: a paper proposes a model, "
               "the model predicts something, another paper uses it. Nothing in it can be run or checked. Right: BoxGraph records what it "
               "takes to evaluate a model: the paper's inputs as printed, its model in runnable form, a run of the model on those inputs, "
               "the result the paper printed, and a comparison of the two that gives a verdict.")
    f.text(20, 30, "A usual knowledge graph", "th")
    f.text(20, 50, "records claims about models")
    f.node("box", 40, 84, 120, 36, "Paper A")
    f.node("box", 260, 84, 140, 36, "Model X")
    f.node("box", 40, 190, 120, 36, "Paper B")
    f.node("box", 260, 190, 140, 36, "bond lifetime")
    f.edge("M160 102 H258")
    f.text(209, 90, "proposes", anchor="middle")
    f.edge("M330 120 V188")
    f.text(338, 156, "predicts")
    f.edge("M160 208 H210 V114 H258")
    f.text(218, 160, "uses")
    f.text(20, 270, "It says a model exists and what it is about.")
    f.text(20, 290, "Nothing in it can be run, or checked against the paper.")

    f.raw('<path class="line" d="M440 20 V300" stroke-dasharray="2 4"/>')
    f.text(470, 30, "BoxGraph", "th")
    f.text(470, 50, "records what it takes to evaluate a model")
    f.node("box", 480, 140, 100, 36, "Paper A")
    f.node("c-teal", 620, 80, 140, 36, "inputs, as printed")
    f.node("c-purple", 620, 140, 140, 36, "model, runnable")
    f.node("c-teal", 620, 220, 140, 36, "result, as printed")
    f.node("c-coral", 790, 80, 80, 36, "Run")
    f.node("c-teal", 900, 80, 90, 36, "prediction")
    f.node("c-coral", 870, 220, 120, 36, "Comparison")
    f.edge("M580 150 H600 V98 H618")
    f.edge("M580 162 H618")
    f.edge("M530 176 V238 H618")
    f.text(524, 210, "reports,", anchor="end")
    f.text(524, 226, "describes", anchor="end")
    f.edge("M760 98 H788")
    f.edge("M830 116 V158 H762")
    f.text(838, 140, "applies")
    f.edge("M870 98 H898")
    f.edge("M945 116 V218")
    f.edge("M760 238 H868")
    f.text(814, 228, "compared", anchor="middle")
    f.text(990, 276, "gives a verdict: reproduced,", anchor="end")
    f.text(990, 292, "close, or not reproduced", anchor="end")
    f.text(20, 340, "BoxGraph's syntax is specific to evaluating models: its kinds of node and edge are the ones needed to state a model, its inputs "
           "and results as printed,")
    f.text(20, 358, "run it, and compare. A claim becomes something that can be checked, and every node traces to the page it came from.")
    return f.svg(1010, 378)


def nodes_and_edges():
    f = Figure("Nodes and edges", "The nodes and edges BoxGraph defines, and those ModelAtlas adds. BoxGraph: four kinds of node (source, "
               "datum, model, run) and nine kinds of edge, each written as a sentence with an example. ModelAtlas: the model nodes of every "
               "paper, five kinds of relation between them, each tested and given a status, and families computed from verified relations.")
    kinds = {"Source": "box", "Datum": "c-teal", "Model": "c-purple", "Run": "c-coral"}

    def nodes_row(y, items):
        for i, (kind, desc) in enumerate(items):
            x = 30 + 230 * i
            if kind == "Family":
                f.raw(f'<rect class="region" x="{x}" y="{y}" width="100" height="32" rx="10" stroke-width="1"/>')
                f.text(x + 50, y + 16, "Family", "th", "middle")
            else:
                f.node(kinds[kind], x, y, 100, 32, kind)
            f.text(x, y + 48, desc)

    def edge_rows(y, rows):
        for subj, verb, obj, style, example in rows:
            f.node(kinds[subj], 30, y, 100, 32, subj)
            f.node(kinds[obj], 300, y, 100, 32, obj)
            f.edge(f"M130 {y + 16} H298", style)
            f.text(214, y + 6, verb, anchor="middle")
            f.text(440, y + 16, example)
            y += 44
        return y

    f.text(30, 26, "BoxGraph", "th")
    f.text(130, 26, "defines what one paper's record can hold")
    f.text(30, 58, "Nodes", "tl")
    nodes_row(70, [("Source", "where something comes from"), ("Datum", "a value, table or curve, as printed"),
                   ("Model", "a model, as the paper states it"), ("Run", "one run of one model")])
    y = 150
    for title, rows in [
        ("Edges: where things come from", [
            ("Source", "reports", "Datum", "", "Paper A prints k = 0.2 /s, on p. 3"),
            ("Source", "describes", "Model", "", "Paper A states its model as Eq. 2"),
            ("Source", "reports, indirectly", "Datum", "dash", "Paper B says its k comes from Paper A: recorded, not checked there"),
            ("Source", "describes, indirectly", "Model", "dash", "Paper B says its model is Paper A's: recorded, not checked there")]),
        ("Edges: how results are produced", [
            ("Datum", "input", "Run", "", "k is given to the run, as the model's input k"),
            ("Run", "applies", "Model", "", "the run runs Eq. 2"),
            ("Run", "output", "Datum", "", "the run produces t = 4.7 s, a predicted value")]),
        ("Edges: how things are built and tuned", [
            ("Model", "built from", "Model", "", "a model assembled from Eq. 2 computes with it"),
            ("Datum", "tuned to", "Datum", "", "a value set by hand to match a measurement: comparing them is in-sample")]),
    ]:
        f.text(30, y, title, "tl")
        y = edge_rows(y + 14, rows) + 16
    f.text(30, y, "A comparison is a run too: it measures how far two data agree, for a stated purpose, and outputs an assessed datum.")
    y += 36
    f.raw(f'<path class="line" d="M30 {y} H970" stroke-dasharray="2 4"/>')
    y += 30
    f.text(30, y, "ModelAtlas", "th")
    f.text(130, y, "joins the models of every paper")
    f.text(30, y + 32, "Nodes", "tl")
    nodes_row(y + 44, [("Model", "the same model nodes, from every paper"), ("Family", "computed: what verified same-as relations join")])
    y += 124
    f.text(30, y, "Edges: relations between models, each tested and given a status", "tl")
    y = edge_rows(y + 14, [
        ("Model", "same as", "Model", "", "Paper 1's rate law is Paper 2's, in other variables, under a mapping"),
        ("Model", "reduces to", "Model", "", "Model A becomes Model C in a stated limit, e.g. small force"),
        ("Model", "derived from", "Model", "", "Model D is derived from Model B"),
        ("Model", "scales as", "Model", "", "Model E follows Model B's scaling"),
        ("Model", "approximated by", "Model", "dot", "a mean-field model approximates a stochastic simulation"),
    ]) + 4
    f.text(30, y, "Status: verified, ambiguous, refuted, not verified, pending, unverifiable. Each relation is stated by a paper (with quote and page) "
           "or proposed, and labelled.")
    f.text(30, y + 18, "Only a verified same-as relation joins a family. A relation joins models, never quantities.")
    return f.svg(1000, y + 40)


def one_paper():
    f = Figure("How one paper becomes a graph", "Paper A, on the left, as the items it prints. Each printed item becomes a node, through "
               "an edge from the paper: its model is described, its inputs and its result are reported. One input the model needs is not "
               "printed: it becomes a node too, added and labelled. A run applies the model to the inputs and outputs a predicted value. A "
               "comparison takes the predicted and printed values and outputs their difference, ten decades. The verdict, computed from it at "
               "the printed precision, is not reproduced, and an open question about the printed value records a possible error in the "
               "paper. The printed value is never corrected.")
    f.text(130, 16, "Paper A, as printed", "th", "middle")
    f.raw('<rect class="box" x="30" y="30" width="200" height="440" rx="6" stroke-width="0.5"/>')
    for y, s, cls in ((64, "Eq. 2: t = …", "ts"), (138, "k₀ = 0.2 /s  (p. 3)", "ts"), (198, "F = 5 pN  (p. 4)", "ts"),
                      (258, "x_b: not stated", "tl"), (424, "log t = −14.7  (p. 5)", "ts")):
        f.text(46, y, s, cls)
    f.node("c-purple", 300, 40, 170, 48, "Model", ["as printed: Eq. 2"])
    f.node("c-teal", 300, 114, 170, 48, "k₀", ["as printed, p. 3"])
    f.node("c-teal", 300, 174, 170, 48, "F", ["as printed, p. 4"])
    f.node("c-teal", 300, 234, 170, 48, "x_b", ["not printed: added"], added=True)
    f.node("c-teal", 300, 400, 170, 48, "log t = −14.7", ["as printed, p. 5"])
    for y, verb in ((64, "describes"), (138, "reports"), (198, "reports"), (424, "reports")):
        f.edge(f"M230 {y} H298")
        f.text(264, y - 10, verb, anchor="middle")
    f.text(264, 248, "labelled", anchor="middle")
    f.node("c-coral", 570, 160, 150, 48, "Run")
    f.node("c-teal", 810, 160, 190, 48, "log t = −4.7", ["predicted"])
    f.node("c-coral", 570, 400, 150, 48, "Comparison", ["for reproduction"])
    f.node("c-teal", 810, 400, 190, 48, "differs by 10 decades", ["assessed"])
    f.node("c-red", 810, 500, 190, 48, "Not reproduced", ["verdict, computed when asked"])
    f.node("rec", 810, 590, 190, 56, "Open question", ["possible error in paper"])
    f.edge("M470 138 H520 V170 H568")
    f.edge("M470 198 H520 V184 H568")
    f.edge("M470 258 H520 V198 H568")
    f.text(495, 126, "input", anchor="middle")
    f.edge("M645 160 V64 H472")
    f.text(653, 110, "applies")
    f.edge("M720 184 H808")
    f.text(764, 172, "output", anchor="middle")
    f.edge("M905 208 V370 H645 V398")
    f.text(780, 360, "input", anchor="middle")
    f.edge("M470 424 H568")
    f.text(519, 412, "input", anchor="middle")
    f.edge("M720 424 H808")
    f.text(764, 412, "output", anchor="middle")
    f.edge("M905 448 V498", "dot")
    f.text(913, 474, "at printed precision")
    f.edge("M810 618 H385 V450", "dot")
    f.text(600, 608, "about the printed value", anchor="middle")
    f.text(30, 690, "x_b is labelled as added wherever it is used, and run with its alternative: if the verdict changes, that is reported too.")
    f.text(30, 710, "The printed −14.7 is never corrected to −4.7. The difference is the finding.")
    return f.svg(1040, 730)


def verdicts():
    f = Figure("Verdicts at the printed precision", "A value printed as 4.7 allows anything that rounds to 4.7, from 4.65 to 4.75: a result inside is reproduced. "
               "Outside by at most twice the half-width (the width of the range again) it is close, if it keeps the printed sign and is within a factor of ten; beyond that it is not reproduced. A value printed with no precision gets no verdict.")

    def x(v):
        return 80 + (v - 4.4) * 1233.33

    f.text(450, 34, "Printed: 4.7, to one decimal: anything that rounds to 4.7 agrees", "th", "middle")
    f.raw(f'<path class="line" d="M{x(4.7)} 48 V78"/>')
    f.band("c-red", x(4.4), 80, x(4.55) - x(4.4), 50, "not reproduced")
    f.band("c-amber", x(4.55), 80, x(4.65) - x(4.55), 50, "close")
    f.band("c-green", x(4.65), 80, x(4.75) - x(4.65), 50, "reproduced")
    f.band("c-amber", x(4.75), 80, x(4.85) - x(4.75), 50, "close")
    f.band("c-red", x(4.85), 80, x(5.0) - x(4.85), 50, "not reproduced")
    f.raw(f'<path class="line" d="M{x(4.4)} 140 H{x(5.0)}"/>')
    for v in (4.4, 4.55, 4.65, 4.7, 4.75, 4.85, 5.0):
        f.raw(f'<path class="line" d="M{x(v)} 136 V144"/>')
        f.text(x(v), 158, f"{v:g}", anchor="middle")
    f.text(80, 196, "The verdict is computed from the data whenever it is asked for, never stored. A value printed with no precision (\"about 5\") gets none.")
    return f.svg(900, 216)


def numerics():
    f = Figure("The model or the numerics", "Two results that both reproduce the paper at the paper's own numerical setting. Refining the setting, the first settles "
               "inside a tolerance declared in advance: it belongs to the model. The second keeps moving: it belongs to the numerics, and that is a finding.")
    levels = ["paper's setting", "2× finer", "4× finer", "8× finer"]

    def panel(x0, title, sub, values, cls, band=None):
        f.text(x0, 30, title, "th")
        f.text(x0, 50, sub)
        left, right, top, bottom = x0 + 20, x0 + 360, 70, 250

        def y(v):
            return bottom - (v / 2.6) * (bottom - top)

        xs = [left + 30 + i * 100 for i in range(4)]
        if band:
            lo, hi = band
            f.raw(f'<rect x="{left}" y="{y(hi)}" width="{right - left}" height="{y(lo) - y(hi)}" fill="#888780" opacity="0.15"/>')
            f.text(right - 4, y(lo) + 14, "tolerance, declared in advance", anchor="end")
        f.raw(f'<path class="line" d="M{left} {top} V{bottom} H{right}"/>')
        f.raw(f'<path class="line dash" d="M{left} {y(2.4)} H{right}" stroke-dasharray="3 3"/>')
        f.text(right - 4, y(2.4) - 10, "the paper's result", anchor="end")
        pts = " ".join(f"{px},{y(v)}" for px, v in zip(xs, values, strict=True))
        f.raw(f'<polyline class="line" points="{pts}"/>')
        for px, v in zip(xs, values, strict=True):
            f.raw(f'<circle class="{cls}" cx="{px}" cy="{y(v)}" r="4.5"/>')
        for px, lab in zip(xs, levels, strict=True):
            f.text(px, bottom + 16, lab, anchor="middle")

    panel(40, "Belongs to the model", "it settles as the setting is refined", [2.4, 2.32, 2.3, 2.3], "pt", band=(2.2, 2.42))
    panel(500, "Belongs to the numerics", "it keeps moving: a finding, though it reproduced", [2.4, 1.7, 1.1, 0.6], "pt2")
    f.text(40, 306, "A step size, a mesh, a sample count or a scheme is a setting, not part of the model. Reproduced is not the same as verified.")
    return f.svg(900, 324)


def atlas():
    f = Figure("ModelAtlas", "Every model enters as its paper states it, and is never merged or overwritten. Verified relations join models: models that are "
               "the same under a mapping form a family. Special cases and derived models are structure around a family. An approximation is checked "
               "but never joins one. A stated relation that is refuted is a finding.")
    f.region(60, 40, 410, 160)
    f.text(75, 60, "A family: the same model in different forms")
    f.node("c-purple", 90, 106, 150, 56, "Model A", ["Paper 1, Eq. 3"])
    f.node("c-purple", 300, 106, 150, 56, "Model B", ["Paper 2, Eq. 7"])
    f.edge("M242 134 H298", both=True)
    f.text(270, 92, "A and B: the same, under a mapping", anchor="middle")
    f.node("c-purple", 90, 280, 150, 56, "Model C", ["Paper 3"])
    f.node("c-purple", 300, 280, 150, 56, "Model D", ["Paper 4"])
    f.node("c-purple", 610, 106, 150, 56, "Model E", ["Paper 5"])
    f.node("c-purple", 610, 280, 150, 56, "Model F", ["Paper 6"])
    f.edge("M165 162 V278")
    f.text(175, 236, "reduces to C, in a limit")
    f.edge("M375 162 V278")
    f.text(385, 236, "D derived from B")
    f.edge("M450 134 H608", "dot")
    f.text(540, 120, "approximated by", anchor="middle")
    f.text(540, 150, "never joins", anchor="middle")
    f.edge("M450 308 H608", "dash", arrow=False)
    f.text(530, 296, "stated: same", anchor="middle")
    f.text(530, 356, "the paper says D and F are the same; the check refutes it: a finding", anchor="middle")
    f.text(60, 396, "Inside a family, results that don't follow from each other's inputs are a finding.")
    f.text(60, 414, "A relation joins models, never quantities: two models' k can still be different things.")
    return f.svg(820, 432)


def two_checks():
    f = Figure("Two kinds of check", "A paper against itself: its inputs run through its model, compared with its own results; this needs only the paper. "
               "A paper against another: one paper's inputs run through another paper's model, compared with its results; this needs a verified "
               "relation that maps one model onto the other.")
    f.text(30, 30, "A paper against itself", "th")
    f.text(30, 50, "needs only this paper")
    f.node("c-teal", 30, 140, 110, 56, "A's inputs")
    f.node("c-purple", 210, 140, 110, 56, "A's model")
    f.node("c-teal", 390, 140, 110, 56, "A's results", ["as printed"])
    f.edge("M140 168 H208")
    f.text(175, 156, "run", anchor="middle")
    f.edge("M320 168 H388", both=True)
    f.text(355, 156, "compared", anchor="middle")
    f.text(560, 30, "A paper against another", "th")
    f.text(560, 50, "needs a verified relation")
    f.node("rec", 695, 66, 200, 44, "Verified relation", ["A ↔ B, with a mapping"])
    f.node("c-teal", 560, 140, 110, 56, "B's inputs")
    f.node("c-purple", 740, 140, 110, 56, "A's model")
    f.node("c-teal", 920, 140, 110, 56, "B's results", ["as printed"])
    f.edge("M670 168 H738")
    f.text(704, 156, "mapped", anchor="middle")
    f.edge("M850 168 H918", both=True)
    f.text(885, 156, "compared", anchor="middle")
    f.edge("M795 110 V138", "dot")
    f.text(30, 240, "Linked is not checked: a cross-paper check exists only where a verified relation lets one paper's model run on another's inputs.")
    f.text(30, 258, "A paper enters the Synthesis when its record is sound, whether or not it reproduces. Not reproduced is a result.")
    return f.svg(1060, 276)


FIGURES = {
    "fig1-evaluating-models.svg": evaluating_models,
    "fig2-nodes-and-edges.svg": nodes_and_edges,
    "fig3-one-paper.svg": one_paper,
    "fig4-verdicts.svg": verdicts,
    "fig5-model-or-numerics.svg": numerics,
    "fig6-modelatlas.svg": atlas,
    "fig7-two-checks.svg": two_checks,
}

if __name__ == "__main__":
    for name, make in FIGURES.items():
        (HERE / name).write_text(make())
