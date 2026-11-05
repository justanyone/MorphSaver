"""morphsaver: scan | rank | packet | emit | run. Each step reads and writes one JSON file under <target>/.morphsaver/runs/<run>/.

    morphsaver scan   <target> [--run NAME] [--out FILE]
    morphsaver rank   <target> [--run NAME]
    morphsaver packet <target> [--run NAME] [--top N]
    morphsaver emit   <target> [--run NAME] --format markdown|github|skybuild
    morphsaver run    <target> [--run NAME] [--top N]      # scan, rank, packet
The judge step is a session, not a CLI command: it reads packets/ and writes verdicts.json (skills/morphsaver-judge).
"""
from __future__ import annotations

import argparse
import ast
import sys
import time
from pathlib import Path

from . import __version__, scanners
from . import emit as emit_mod
from . import packet as packet_mod
from . import rank as rank_mod
from .model import read_file, write_file
from .policy import STATE_DIR, Policy, iter_files


def run_dir(target: Path, run: str | None) -> Path:
    name = run or time.strftime("%Y%m%d-%H%M%S")
    return target / STATE_DIR / "runs" / name


def latest_run(target: Path) -> Path:
    runs = sorted((target / STATE_DIR / "runs").glob("*"))
    if not runs:
        sys.exit(f"no runs under {target / STATE_DIR / 'runs'}; run `morphsaver scan` first")
    return runs[-1]


def cmd_scan(a) -> Path:
    target, policy = Path(a.target).resolve(), Policy.load(Path(a.target).resolve())
    found, files, errors = [], 0, 0
    records = {s.NAME: [] for s in scanners.CROSS_FILE if hasattr(s, "collect")}
    for path, rel in iter_files(target, policy):
        files += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=rel)
        except SyntaxError:
            errors += 1
            continue
        for scanner in scanners.PER_FILE:
            found.extend(scanner.scan(tree, rel, policy))
        for scanner in scanners.CROSS_FILE:
            if scanner.NAME in records:
                records[scanner.NAME].append(scanner.collect(tree, rel, policy))
    for scanner in scanners.CROSS_FILE:
        found.extend(scanner.scan_all(records.get(scanner.NAME, found), policy))
    found = [c for c in found if not (c.scanner == "data_clump" and c.discriminator_kind == "fact")]
    out = Path(a.out) if a.out else run_dir(target, a.run) / "candidates.json"
    write_file(out, "scan", found, {"target": str(target), "files": files, "syntax_errors": errors,
                                    "scanners": sorted(scanners.ALL), "morphsaver": __version__})
    print(f"scan: {files} files, {len(found)} candidates -> {out}")
    return out.parent


def cmd_rank(a, rd: Path | None = None):
    target = Path(a.target).resolve()
    rd = rd or (run_dir(target, a.run) if a.run else latest_run(target))
    candidates, _ = read_file(rd / "candidates.json")
    ranked = rank_mod.rank(candidates, Policy.load(target), target)
    write_file(rd / "ranked.json", "rank", ranked, {"target": str(target)})
    print(f"rank: {len(ranked)} candidates -> {rd / 'ranked.json'}")
    return rd


def cmd_packet(a, rd: Path | None = None):
    target = Path(a.target).resolve()
    rd = rd or (run_dir(target, a.run) if a.run else latest_run(target))
    policy = Policy.load(target)
    candidates, _ = read_file(rd / "ranked.json")
    top = a.top or policy.top
    pdir = rd / "packets"
    pdir.mkdir(exist_ok=True)
    for c in candidates[:top]:
        (pdir / f"{c.id}.md").write_text(packet_mod.build(target, c, policy), encoding="utf-8")
    print(f"packet: {min(top, len(candidates))} packets -> {pdir}")
    return rd


def cmd_emit(a):
    target = Path(a.target).resolve()
    rd = run_dir(target, a.run) if a.run else latest_run(target)
    candidates, meta = read_file(rd / "verdicts.json")
    written = emit_mod.ALL[a.format].emit(candidates, rd / "tasks", meta)
    print(f"emit: {len(written)} tasks -> {rd / 'tasks'}")


def cmd_run(a):
    rd = cmd_scan(a)
    cmd_rank(a, rd)
    cmd_packet(a, rd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="morphsaver", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("scan", cmd_scan), ("rank", cmd_rank), ("packet", cmd_packet), ("emit", cmd_emit), ("run", cmd_run)):
        p = sub.add_parser(name)
        p.add_argument("target")
        p.add_argument("--run", help="run name under .morphsaver/runs (default: newest, or a timestamp for scan)")
        if name in ("scan", "run"):
            p.add_argument("--out", help="scan: write candidates.json here instead of the run directory")
        if name in ("packet", "run"):
            p.add_argument("--top", type=int, help="how many packets (default policy.top)")
        if name == "emit":
            p.add_argument("--format", choices=sorted(emit_mod.ALL), default="markdown")
        p.set_defaults(fn=fn)
    a = ap.parse_args(argv)
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
