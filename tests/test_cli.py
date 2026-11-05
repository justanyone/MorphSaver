import json
import subprocess
import sys
from pathlib import Path

from morphsaver.cli import main
from morphsaver.model import read_file

FIXTURES = Path(__file__).parent / "fixtures" / "dispatch"


def test_run_pipeline_on_fixture(tmp_path):
    target = tmp_path / "repo"
    target.mkdir()
    for f in FIXTURES.glob("*.py"):
        (target / f.name).write_text(f.read_text())
    assert main(["run", str(target), "--run", "t1", "--top", "3"]) == 0
    rd = target / ".morphsaver" / "runs" / "t1"
    candidates, meta = read_file(rd / "candidates.json")
    assert meta["files"] == 3 and len(candidates) == 9  # 5 chains + 2 repeated singles + 2 groups (a,b,c,d twice in chains.py)
    ranked, _ = read_file(rd / "ranked.json")
    assert ranked[0].scanner == "repeated_dispatch"             # the group outranks every single site
    assert all(c.lines_saved == c.dup_lines - c.overhead_lines for c in ranked)
    packets = sorted((rd / "packets").glob("*.md"))
    assert len(packets) == 3 and "## Judge" in packets[0].read_text()


def test_rank_is_deterministic(tmp_path):
    target = tmp_path / "repo"
    target.mkdir()
    (target / "a.py").write_text((FIXTURES / "chains.py").read_text())
    main(["run", str(target), "--run", "r1"])
    main(["run", str(target), "--run", "r2"])
    a = (target / ".morphsaver/runs/r1/ranked.json").read_text()
    b = (target / ".morphsaver/runs/r2/ranked.json").read_text()
    assert a == b


def test_emit_markdown_from_verdicts(tmp_path):
    target = tmp_path / "repo"
    target.mkdir()
    (target / "a.py").write_text((FIXTURES / "repeated_a.py").read_text())
    (target / "b.py").write_text((FIXTURES / "repeated_b.py").read_text())
    main(["run", str(target), "--run", "v1"])
    rd = target / ".morphsaver/runs/v1"
    payload = json.loads((rd / "ranked.json").read_text())
    for c in payload["candidates"]:
        c["verdict"] = "accept" if c["scanner"] == "repeated_dispatch" else "reject"
        c["rationale"] = "fixture"
    payload["step"] = "judge"
    (rd / "verdicts.json").write_text(json.dumps(payload))
    main(["emit", str(target), "--run", "v1", "--format", "markdown"])
    tasks = list((rd / "tasks").glob("*.md"))
    assert len(tasks) == 1 and "Acceptance criteria" in tasks[0].read_text()


def test_module_entry_point():
    out = subprocess.run([sys.executable, "-m", "morphsaver", "--version"], capture_output=True, text=True, check=False)
    assert out.returncode == 0 and out.stdout.strip()
