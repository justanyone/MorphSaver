import ast
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest

from morphsaver.cli import main
from morphsaver.model import write_file
from morphsaver.policy import Policy
from morphsaver.rank import rank
from morphsaver.scanners.dispatch_chain import scan

FIXTURE = Path(__file__).parent / "fixtures" / "rank"


def candidates():
    source = (FIXTURE / "handlers.py").read_text()
    return scan(ast.parse(source), "handlers.py", Policy())


def test_missing_tools_and_test_references(monkeypatch, capsys):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    ranked = rank(candidates(), Policy(), FIXTURE)
    by_name = {c.sites[0].function: c for c in ranked}
    assert by_name["handle"].tests == ["tests/references.py"]
    assert by_name["untouched"].tests == []
    for c in ranked:
        expected = c.lines_saved - (0 if c.tests else Policy().no_tests_penalty)
        assert c.score == expected
        assert c.callers == -1 and c.hot == []
    warnings = capsys.readouterr().err.splitlines()
    assert len(warnings) == 3
    assert all(sum(tool in line for line in warnings) == 1 for tool in ("ruff", "radon", "codegraph"))


def fake_run(argv, **kwargs):
    tool = Path(argv[0]).name
    if tool == "ruff":
        payload = [{"filename": str((FIXTURE / "handlers.py").resolve()),
                    "code": "C901", "location": {"row": 1}},
                   {"filename": str((FIXTURE / "handlers.py").resolve()),
                    "code": "C901", "location": {"row": 1}}]
        return SimpleNamespace(returncode=1, stdout=json.dumps(payload))
    if tool == "radon":
        payload = {"handlers.py": [{"name": "handle", "lineno": 1, "endline": 7, "rank": "C"}]}
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload))
    return SimpleNamespace(returncode=0, stdout="**Called by ←** first (a.py:1), second (b.py:2)\n")


def test_enriched_reruns_are_deterministic(monkeypatch, tmp_path):
    monkeypatch.setattr(shutil, "which", lambda tool: "/tools/" + tool)
    monkeypatch.setattr(subprocess, "run", fake_run)
    first = rank(candidates(), Policy(), FIXTURE)
    hot = next(c for c in first if c.sites[0].function == "handle")
    assert hot.hot == ["C901", "radon:C"] and hot.callers == 2
    assert hot.score == round(hot.lines_saved + 6 - 0.4, 2)
    write_file(tmp_path / "first.json", "rank", first)
    second = rank(first, Policy(), FIXTURE)
    write_file(tmp_path / "second.json", "rank", second)
    assert (tmp_path / "first.json").read_bytes() == (tmp_path / "second.json").read_bytes()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: [c.to_json() for c in rank(candidates(), Policy(), FIXTURE)], range(2)))
    assert results[0] == results[1]


@pytest.mark.parametrize("output", ["not json", "null", "{}", "[]"])
def test_invalid_tool_output_degrades(monkeypatch, output):
    monkeypatch.setattr(shutil, "which", lambda tool: tool)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=output))
    result = rank(candidates(), Policy(), FIXTURE)
    assert all(c.hot == [] and c.callers == -1 for c in result)


def test_tool_timeout_degrades(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda tool: tool)

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 30)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert len(rank(candidates(), Policy(), FIXTURE)) == 2


def test_cli_without_tools(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(shutil, "which", lambda tool: None)
    shutil.copytree(FIXTURE, tmp_path / "target")
    assert main(["run", str(tmp_path / "target"), "--run", "fixture"]) == 0
    assert len(capsys.readouterr().err.splitlines()) == 3


def test_hot_bonus_loads_from_policy(tmp_path):
    state = tmp_path / ".morphsaver"
    state.mkdir()
    (state / "policy.toml").write_text("[weights]\nhot_bonus = 7.5\n")
    policy = Policy.load(tmp_path)
    c = candidates()[0]
    c.hot = ["C901"]
    assert rank([c], policy)[0].score == c.lines_saved + 7.5 - policy.no_tests_penalty


def test_caller_queries_are_cached_per_function(monkeypatch):
    from dataclasses import replace

    monkeypatch.setattr(shutil, "which", lambda tool: "/tools/" + tool)
    queries = []

    def run(argv, **kwargs):
        if Path(argv[0]).name == "codegraph":
            queries.append(tuple(argv))
        return fake_run(argv, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    first, second = candidates()
    second.sites = [replace(first.sites[0], line=3), first.sites[0]]
    ranked = rank([first, second], Policy(), FIXTURE)
    assert len(queries) == 1
    assert all(c.callers == 2 for c in ranked)


def test_evidence_is_replaced_when_tools_disappear(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda tool: tool)
    monkeypatch.setattr(subprocess, "run", fake_run)
    result = rank(candidates(), Policy(), FIXTURE)
    monkeypatch.setattr(shutil, "which", lambda tool: None)
    result = rank(result, Policy(), FIXTURE)
    assert all(c.hot == [] and c.callers == -1 for c in result)


def test_failed_caller_queries_warn_once_and_are_cached(monkeypatch, capsys):
    monkeypatch.setattr(shutil, "which", lambda tool: tool)
    queries = []

    def run(argv, **kwargs):
        if argv[0] == "codegraph":
            queries.append(tuple(argv))
            return SimpleNamespace(returncode=2, stdout="")
        return fake_run(argv, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    entries = candidates()
    entries.append(candidates()[0])
    result = rank(entries, Policy(), FIXTURE)
    assert all(c.callers == -1 for c in result)
    assert len(queries) == 2
    assert capsys.readouterr().err.splitlines() == [
        "warning: codegraph: unavailable or invalid output; enrichment skipped"
    ]


def test_malformed_records_are_ignored(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda tool: tool)

    def run(argv, **kwargs):
        if argv[0] == "ruff":
            payload = [None, {"code": "C901", "filename": "handlers.py", "location": {"row": "1"}},
                       {"code": "C901", "filename": "../outside.py", "location": {"row": 1}}]
        elif argv[0] == "radon":
            payload = {"handlers.py": [None, {"lineno": "1", "rank": "C"}, {"lineno": 1, "rank": "Z"}]}
        else:
            return SimpleNamespace(returncode=2, stdout="")
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload))

    monkeypatch.setattr(subprocess, "run", run)
    assert all(c.hot == [] and c.callers == -1 for c in rank(candidates(), Policy(), FIXTURE))
