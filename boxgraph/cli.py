"""boxgraph: validate records, build the Synthesis, write the report.

  boxgraph validate RECORD [RECORD ...]   check soundness; exit 1 if any is not sound
  boxgraph build RECORDS --out BUILD      build every record, the atlas and the Synthesis
  boxgraph ingest PDF --id ID [--pages A-B] --records RECORDS
                                          extract per-page text (and images) for a new source
  boxgraph figure page PDF PAGE --out PNG  a page with a pixel ruler, to choose a figure's crop
  boxgraph figure axes PDF PAGE --crop X0,Y0,X1,Y1 --out PNG
                                          find axes and number the tick candidates
  boxgraph relations RECORDS [--only ID,ID]
                                          test the relations entered in some records
  boxgraph figure check RECORD FIG_ID --out PNG
                                          read a recorded figure and draw what was read
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from . import __version__


def _validate(args) -> int:
    from .validate import validate_path

    worst = 0
    for p in args.records:
        cache = args.cache or os.environ.get("BOXGRAPH_CACHE")  # shared by agents and their gates
        rep = validate_path(p, run=not args.no_run, cache_dir=Path(cache) if cache else None)
        print(rep.text())
        if not rep.sound:
            worst = 1
    return worst


def _build(args) -> int:
    import yaml

    from .explore import render_explorer
    from .overview import render_overview
    from .report import build_index, render_figure_check, render_html, render_markdown, review, trace_check
    from .synthesis import build_synthesis, to_json

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = Path(args.cache) if args.cache else out / "cache"  # a shared cache reuses runs made elsewhere
    syn = build_synthesis(Path(args.records), cache_dir=cache)
    (out / "records").mkdir(exist_ok=True)
    for sid, b in syn["builds"].items():
        (out / "records" / f"{sid}.json").write_text(json.dumps(b, indent=1, default=str))
    (out / "synthesis.json").write_text(json.dumps(to_json(syn), indent=1, sort_keys=True, default=str))
    sents = review(syn)
    problems = trace_check(sents, build_index(syn))
    (out / "review.json").write_text(json.dumps([vars(s) for s in sents], indent=1))
    (out / "report.md").write_text(render_markdown(syn, sents))
    (out / "report.html").write_text(render_html(syn, sents, title=args.title, figdir=out / "figures"))
    (out / "figures.html").write_text(render_figure_check(syn, figdir=out / "figures", title=f"{args.title}: figure readings"))
    # the overlays go beside the page (explorer_files/), so it stays small however large the corpus;
    # --standalone embeds them in one file instead
    images = None if args.standalone else out / "explorer_files"
    (out / "explorer.html").write_text(render_explorer(to_json(syn), title=f"{args.title}: explorer", figdir=out / "figures",
                                                       image_dir=images, image_prefix="explorer_files/"))
    content = yaml.safe_load(Path(args.overview).read_text()) if args.overview else None
    render_overview(to_json(syn), out / "overview", title=args.title, content=content,
                    content_dir=Path(args.overview).parent if args.overview else None)
    for sid, p in syn["papers"].items():
        state = "sound" if p.get("sound") else "NOT SOUND"
        t = p.get("tally", {})
        print(f"{sid:28} {state:10} reproduction: reproduced {t.get('reproduced', 0)}  close {t.get('close', 0)}  "
              f"not reproduced {t.get('not reproduced', 0)}  no verdict {t.get('no verdict', 0)}")
        for purpose, tp in (p.get("tally_by_purpose") or {}).items():
            if purpose != "reproduction":
                print(f"{'':39}{purpose}: reproduced {tp['reproduced']}  close {tp['close']}  "
                      f"not reproduced {tp['not reproduced']}  no verdict {tp['no verdict']}")
    print(f"findings: {len(syn['findings'])}  relations: {len(syn['relations'])}  families: {len(syn['families'])}  "
          f"cross-paper checks: {sum(1 for x in syn['cross_checks'] if x.get('status') == 'checked')}")
    if problems:
        print("review tracer problems:", *problems, sep="\n  ")
        return 2
    print(f"wrote {out / 'report.html'}, {out / 'figures.html'}, {out / 'explorer.html'} and {out / 'overview' / 'index.html'}")
    return 0


def _digest(args) -> int:
    from .sources import tree_digest

    print(tree_digest(Path(args.path)))
    return 0


def _relations(args) -> int:
    from .atlas import test_relation
    from .store import load_all, model_by_id

    records = {lr.record.source.id: lr for lr in load_all(args.records)}
    only = set(args.only.split(",")) if args.only else set(records)
    bad = 0
    for sid in sorted(only & set(records)):
        for rel in records[sid].record.relations:
            missing = []
            for gid in (rel.a, rel.b):
                src, _, mid = gid.partition("/")
                if src not in records or model_by_id(records[src], mid) is None:
                    missing.append(gid)
            if missing:
                bad += 1
                print(f"{sid}/{rel.id:28} ERROR      no model {', '.join(missing)}")
                continue
            cache = os.environ.get("BOXGRAPH_CACHE")  # shared with the agents and the build
            r = test_relation(rel, records, source=sid, cache_dir=Path(cache) if cache else None)
            err = f"  max error {r.error:.3g}" if r.error is not None else ""
            print(f"{sid}/{rel.id:28} {r.status:10} {rel.kind.value} {rel.a} -> {rel.b}{err}  {r.detail}")
    for sid in sorted(only - set(records)):
        bad += 1
        print(f"{sid}: no such record under {args.records}")
    return 1 if bad else 0


def _validations(args) -> int:
    """The models of these records judged against measurements in the others (validations.yaml)."""
    from .synthesis import check_validations

    only = [s for s in args.only.split(",") if s]
    cache = args.cache or os.environ.get("BOXGRAPH_CACHE")
    res = check_validations(args.records, only, cache_dir=Path(cache) if cache else None)
    bad = 0
    for v in res:
        if v["status"] != "checked":
            bad += 1
            print(f"{v['id']:44} {v['status']}")
            continue
        print(f"{v['id']:44} {v['verdict']:15} {v['model']} against {v['against']}"
              + (f"  ({'; '.join(v['correspondences'])})" if v["correspondences"] else ""))
    if not res:
        print("no validations between these records")
    return 1 if bad else 0


def _ingest(args) -> int:
    from .ingest import ingest

    pages = None
    if args.pages:
        a, b = args.pages.split("-")
        pages = (int(a), int(b))
    d = ingest(Path(args.pdf), args.id, Path(args.records), pages=pages, images=not args.no_images)
    print(f"ingested {args.pdf} into {d}")
    return 0


def _crop(text):
    return tuple(float(v) for v in text.split(",")) if text else None


def _figure_page(args) -> int:
    from PIL import Image, ImageDraw

    from . import digitize as D

    img = D.render(args.pdf, args.page, dpi=args.dpi)
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    H, W = img.shape[:2]
    for x in range(0, W, 100):
        dr.line([(x, 0), (x, H)], fill=(255, 140, 0) if x % 500 else (220, 40, 40), width=1)
        dr.text((x + 2, 2), str(x), fill=(220, 40, 40))
    for y in range(0, H, 100):
        dr.line([(0, y), (W, y)], fill=(255, 140, 0) if y % 500 else (220, 40, 40), width=1)
        dr.text((2, y + 2), str(y), fill=(220, 40, 40))
    im.save(args.out)
    print(f"page {args.page} at {args.dpi} dpi: {W} x {H} px; ruler every 100 px -> {args.out}")
    return 0


def _figure_axes(args) -> int:
    from . import digitize as D

    img = D.render(args.pdf, args.page, dpi=args.dpi, crop=_crop(args.crop))
    skew = D.find_skew(img)
    img = D.deskew(img)
    if abs(skew) >= 0.1:
        print(f"the figure is tilted by {skew:.2f} degrees; positions below are in the straightened crop")
    try:
        f = D.find_axes(img)
    except D.CalibrationError as e:
        print(f"no axes found: {e}")
        return 1
    D.overlay_candidates(img, f, args.out)
    print(f"crop {args.crop or 'whole page'} at {args.dpi} dpi; plot box (c0, r0, c1, r1) = {[round(b, 1) for b in f.box]}")
    print("x candidates (column in the crop); * = in the evenly spaced tick set:")
    print("  " + "  ".join(f"x{i}={c:.1f}{'*' if c in f.x_ticks else ''}" for i, c in enumerate(f.x_candidates)))
    print("y candidates (row in the crop):")
    print("  " + "  ".join(f"y{i}={c:.1f}{'*' if c in f.y_ticks else ''}" for i, c in enumerate(f.y_candidates)))
    print(f"x ticks: {[round(c, 1) for c in f.x_ticks]}")
    print(f"y ticks: {[round(c, 1) for c in f.y_ticks]}")
    print(f"numbered candidates drawn on {args.out}")
    return 0


def _figure_check(args) -> int:
    from .engine import Builder
    from .store import load_record

    lr = load_record(args.record)
    b = Builder(lr)
    if args.fig not in b.figures:
        print(f"no figure reading {args.fig!r} in {args.record}")
        return 1
    res = b.read_figure(args.fig, overlay_to=args.out)
    if res.get("residual_px"):
        print(f"{res['where']}: {res['what']}; calibration misfit x {res['residual_px'][0]:.2f} px, y {res['residual_px'][1]:.2f} px")
    for r in res["readings"]:
        if r["found"]:
            print(f"  x = {r['x']:g}: y = {r['y']:.4g}  [{r['lo']:.4g}, {r['hi']:.4g}]  {r['note']}")
        else:
            print(f"  x = {r['x']:g}: NOT FOUND  {r['note']}")
    for e in res["errors"]:
        print(f"  ERROR {e}")
    if res.get("overlay"):
        print(f"drawn on {res['overlay']}")
    return 1 if res["errors"] else 0


def _figure_read(args) -> int:
    import yaml

    from . import digitize as D
    from . import figures as FG
    from .schema import FigureReading

    spec = yaml.safe_load(Path(args.spec).read_text())
    pdf = Path(spec.pop("pdf"))
    if not pdf.is_absolute():
        pdf = Path(args.spec).parent / pdf
    fr = FigureReading.model_validate(spec)
    img = D.render(pdf, fr.page, dpi=fr.dpi, crop=tuple(fr.crop))
    reader = None
    if fr.mode == "code" and fr.code:
        from .engine import read_with_code

        code = Path(args.spec).parent / fr.code

        def reader(im, at):
            return read_with_code(code, im, at)
    res = FG.apply(fr, img, overlay_to=args.overlay, code_reader=reader)
    Path(args.out).write_text(json.dumps(res, indent=1))
    for r in res["readings"]:
        print(f"  x = {r['x']:g}: " + (f"y = {r['y']:.4g}  [{r['lo']:.4g}, {r['hi']:.4g}]  {r['note']}" if r["found"]
                                         else f"NOT FOUND  {r['note']}"))
    for e in res["errors"]:
        print(f"  ERROR {e}")
    return 1 if res["errors"] else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="boxgraph", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check that records are sound")
    v.add_argument("records", nargs="+")
    v.add_argument("--no-run", action="store_true", help="skip running the models")
    v.add_argument("--cache", help="cache directory for model runs (default: $BOXGRAPH_CACHE, if set)")
    v.set_defaults(fn=_validate)
    b = sub.add_parser("build", help="build the Synthesis and the report")
    b.add_argument("records")
    b.add_argument("--out", default="build")
    b.add_argument("--title", default="BoxGraph Synthesis")
    b.add_argument("--standalone", action="store_true", help="embed the explorer's images in the page (one file)")
    b.add_argument("--overview", help="YAML with the overview's introduction, links and case studies")
    b.add_argument("--cache", help="cache directory for model runs (default: OUT/cache)")
    b.set_defaults(fn=_build)
    vl = sub.add_parser("validations", help="judge the models of some records against measurements in the others")
    vl.add_argument("records")
    vl.add_argument("--only", required=True, help="comma-separated record ids (each record's validations against the others)")
    vl.add_argument("--cache", help="cache directory for model runs (default: $BOXGRAPH_CACHE, if set)")
    vl.set_defaults(fn=_validations)
    rl = sub.add_parser("relations", help="test the relations entered in some records")
    rl.add_argument("records")
    rl.add_argument("--only", help="comma-separated record ids whose relations to test (default: all)")
    rl.set_defaults(fn=_relations)
    dg = sub.add_parser("digest", help="print the sha256 digest that pins a code folder or data file")
    dg.add_argument("path")
    dg.set_defaults(fn=_digest)
    i = sub.add_parser("ingest", help="extract page text and images from a PDF")
    i.add_argument("pdf")
    i.add_argument("--id", required=True)
    i.add_argument("--records", default="records")
    i.add_argument("--pages", help="first-last PDF pages that belong to the source")
    i.add_argument("--no-images", action="store_true")
    i.set_defaults(fn=_ingest)
    f = sub.add_parser("figure", help="read figures: choose a crop, find axes, check a reading")
    fsub = f.add_subparsers(dest="figcmd", required=True)
    fp = fsub.add_parser("page", help="render a page with a pixel ruler")
    fp.add_argument("pdf")
    fp.add_argument("page", type=int)
    fp.add_argument("--dpi", type=int, default=300)
    fp.add_argument("--out", required=True)
    fp.set_defaults(fn=_figure_page)
    fa = fsub.add_parser("axes", help="find axes and number tick candidates in a crop")
    fa.add_argument("pdf")
    fa.add_argument("page", type=int)
    fa.add_argument("--dpi", type=int, default=300)
    fa.add_argument("--crop", help="x0,y0,x1,y1 in pixels at --dpi")
    fa.add_argument("--out", required=True)
    fa.set_defaults(fn=_figure_axes)
    fc = fsub.add_parser("check", help="read a recorded figure and draw the reading")
    fc.add_argument("record")
    fc.add_argument("fig")
    fc.add_argument("--out", required=True)
    fc.set_defaults(fn=_figure_check)
    fr_ = fsub.add_parser("read", help="read a figure from a standalone spec (a figure reading plus `pdf:`)")
    fr_.add_argument("spec")
    fr_.add_argument("--out", required=True, help="JSON file for the readings")
    fr_.add_argument("--overlay", help="PNG to draw the reading on")
    fr_.set_defaults(fn=_figure_read)
    args = ap.parse_args(argv)
    return args.fn(args)
