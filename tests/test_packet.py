import ast
import dataclasses
import re
from pathlib import Path

from morphsaver.model import SHAPES, Candidate, Site
from morphsaver.packet import build
from morphsaver.policy import Policy

SECTIONS = ["## Sites", "## Proposed shape: ", "## Callers", "## Tests", "## Judge"]


def _candidate(target_file: str, shape: str, values=("a-b", "1x"), disc="kind-x y", sites=1, callers=-1, tests=()):
    site_list = [Site(file=target_file, line=1 + i * 3, end_line=2 + i * 3, function=f"f{i}",
                      arms=2, discriminator=disc, values=values, kind="if-elif")
                 for i in range(sites)]
    return Candidate(id="c-1", scanner="dispatch_chain", sites=site_list, values=tuple(values),
                     shape=shape, callers=callers, tests=list(tests))


def _sketch(text: str) -> str:
    part = text.split("## Proposed shape", 1)[1]
    return re.search(r"```python\n(.*?)\n```", part, re.S).group(1)


def test_sketch_parses_for_every_shape(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\ny = 2\nz = 3\nw = 4\n")
    for shape in SHAPES:
        for values, disc in [(("a-b", "1x"), "kind-x y"), ((), ""), (("with space",), "2nd")]:
            c = _candidate("a.py", shape, values=values, disc=disc)
            ast.parse(_sketch(build(tmp_path, c, Policy())))


def test_packet_has_one_h1_and_all_sections(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\ny = 2\nz = 3\nw = 4\n")
    text = build(tmp_path, _candidate("a.py", "dict-table", callers=3, tests=["tests/test_a.py"]), Policy())
    assert sum(1 for ln in text.splitlines() if ln.startswith("# ")) == 1
    pos = [text.index(s) for s in SECTIONS]
    assert pos == sorted(pos)
    assert "callers: 3" in text and "- tests/test_a.py" in text


def test_callers_unknown_without_codegraph(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n")
    text = build(tmp_path, _candidate("a.py", "split-function", callers=-1), Policy())
    assert "callers: unknown" in text.split("## Callers", 1)[1].split("## Tests", 1)[0]


def test_forty_sites_stay_under_cap_with_cut_note(tmp_path):
    body = "\n".join(f"line {n} = {n}" for n in range(1, 200)) + "\n"
    (tmp_path / "big.py").write_text(body)
    policy = Policy()
    c = _candidate("big.py", "dict-table", sites=40)
    # 40 sites of 20 lines each: far over the cap
    c.sites = [dataclasses.replace(s, end_line=s.line + 19) for s in c.sites]
    text = build(tmp_path, c, policy)
    assert len(text.splitlines()) < policy.packet_max_lines
    assert "cut by packet_max_lines" in text
    assert "## Judge" in text
