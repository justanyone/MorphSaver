import ast
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from morphsaver.policy import Policy
from morphsaver.rank import rank
from morphsaver.scanners import parallel_functions as scanner

FIXTURES = Path(__file__).parent / "fixtures" / "parallel"


def records(name, prefix=""):
    path = FIXTURES / name
    return scanner.collect(ast.parse(path.read_text()), prefix + name, Policy())


def test_module_family_and_cost():
    found = scanner.scan_all([records("results.py")], Policy())
    assert len(found) == 1
    candidate = rank(found, Policy())[0]
    assert len(candidate.sites) == 4
    assert all(s.arms == 1 and s.lines == 2 for s in candidate.sites)
    assert candidate.discriminator_kind == "family"
    assert candidate.shape == "template-method"
    assert candidate.dup_lines == 8
    assert candidate.overhead_lines == 6 + 4 * 4
    assert candidate.lines_saved == -14
    assert scanner.scan_all([records("unrelated.py")], Policy()) == []


def test_package_table_and_alias():
    inputs = [records("package/first.py"), records("package/second.py")]
    found = scanner.scan_all(inputs, Policy())
    assert len(found) == 1 and len(found[0].sites) == 3
    assert {s.function for s in found[0].sites} == {"render", "encode", "decode"}
    assert scanner.scan_all(inputs[:1], Policy()) == []
    assert scanner.scan_all([inputs[0], records("package/second.py", "other/")], Policy()) == []


def test_stable_ids_order_and_duplicate_launch():
    inputs = [records("package/first.py"), records("package/second.py")]
    first = scanner.scan_all(inputs, Policy())
    again = scanner.scan_all(list(reversed(inputs)) + inputs, Policy())
    assert [c.to_json() for c in first] == [c.to_json() for c in again]
    source = (FIXTURES / "results.py").read_text()
    before = scanner.scan(ast.parse(source), "results.py", Policy())
    after = scanner.scan(ast.parse("\n\n" + source), "results.py", Policy())
    assert before[0].id == after[0].id


def test_runs_and_threads_do_not_share_state():
    def run(name):
        return scanner.scan_all([records(name)], Policy())
    with ThreadPoolExecutor(max_workers=4) as pool:
        output = list(pool.map(run, ["results.py", "unrelated.py"] * 4))
    assert [len(result) for result in output] == [1, 0] * 4
    assert scanner.scan_all([], Policy()) == []


@pytest.mark.parametrize("threshold", [-0.1, 1.1, float("nan")])
def test_invalid_similarity(threshold):
    with pytest.raises(ValueError, match="skeleton_similarity"):
        scanner.scan_all([], Policy(skeleton_similarity=threshold))


def test_similarity_threshold_and_package_name_affinity():
    source = (FIXTURES / "results.py").read_text()
    source = source.replace("result = value + 4", "result = -(value + 4)")
    tree = ast.parse(source)
    assert len(scanner.scan(tree, "results.py", Policy())[0].sites) == 4
    assert len(scanner.scan(tree, "results.py", Policy(skeleton_similarity=1))[0].sites) == 3
    nodes = tree.body
    inputs = [scanner.collect(ast.Module(body=nodes[:2], type_ignores=[]), "pkg/a.py", Policy()),
              scanner.collect(ast.Module(body=nodes[2:], type_ignores=[]), "pkg/b.py", Policy())]
    assert len(scanner.scan_all(inputs, Policy())[0].sites) == 4
    separate = [scanner.collect(ast.Module(body=nodes[:2], type_ignores=[]), "a.py", Policy()),
                scanner.collect(ast.Module(body=nodes[2:], type_ignores=[]), "b.py", Policy())]
    assert scanner.scan_all(separate, Policy()) == []


def test_cli_cross_file_side_output(tmp_path):
    from argparse import Namespace
    from morphsaver.cli import cmd_scan
    from morphsaver.model import read_file

    package = tmp_path / "package"
    package.mkdir()
    for name in ("first.py", "second.py"):
        (package / name).write_text((FIXTURES / "package" / name).read_text())
    args = Namespace(target=str(tmp_path), out=str(tmp_path / "out.json"), run="test")
    cmd_scan(args)
    output = (tmp_path / "out.json").read_bytes()
    candidates, _ = read_file(tmp_path / "out.json")
    assert len(candidates) == 1 and len(candidates[0].sites) == 3
    cmd_scan(args)
    assert (tmp_path / "out.json").read_bytes() == output
