from pathlib import Path

from morphsaver.emit import markdown
from morphsaver.model import Candidate, Site

FIX = Path(__file__).parent / "fixtures" / "emit" / "shared_fn.py"


def _site(fn, file="shared_fn.py"):
    return Site(file=file, line=1, end_line=8, function=fn, arms=3, discriminator="kind")


def _cands():
    dispatch = Candidate(id="d1", scanner="repeated_dispatch", sites=[_site("handle")], shape="dict-table",
                         verdict="accept", lines_saved=5)
    clump = Candidate(id="c1", scanner="data_clump", sites=[_site("handle"), _site("other")], shape="dataclass",
                      verdict="accept", lines_saved=3)
    unrelated = Candidate(id="c2", scanner="data_clump", sites=[_site("other")], shape="dataclass",
                          verdict="accept", lines_saved=2)
    return [dispatch, clump, unrelated]


def _snapshot(d):
    return {p.name: p.read_bytes() for p in d.iterdir()}


def test_depends_on_written_under_title_of_shared_function(tmp_path):
    cands = _cands()
    assert FIX.exists()
    assert markdown.depends_map(cands) == {"d1": ["c1"]}
    markdown.emit(cands, tmp_path, {})
    lines = (tmp_path / "d1.md").read_text().splitlines()
    assert lines[0].startswith("# refactor:") and lines[1] == "depends_on: c1"
    assert b"depends_on" not in (tmp_path / "c1.md").read_bytes()


def test_unchanged_task_is_not_rewritten(tmp_path):
    cands = _cands()
    first = markdown.emit(cands, tmp_path, {})
    assert len(first) == 4  # three tasks + README
    before = {p.name: p.stat().st_mtime_ns for p in tmp_path.iterdir()}
    assert not markdown.emit(cands, tmp_path, {})
    assert {p.name: p.stat().st_mtime_ns for p in tmp_path.iterdir()} == before


def test_emit_twice_is_byte_identical(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    markdown.emit(_cands(), a, {})
    markdown.emit(_cands(), b, {})
    assert _snapshot(a) == _snapshot(b)


def test_readme_lists_each_title_once_with_delta_and_dependency(tmp_path):
    markdown.emit(_cands(), tmp_path, {})
    readme = (tmp_path / "README.md").read_text()
    assert readme.count("| `d1.md`") == 1 == readme.count("| `c1.md`")
    assert "| -5 | c1 |" in readme and "| -3 | - |" in readme
