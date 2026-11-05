import ast
from pathlib import Path

from morphsaver.policy import Policy
from morphsaver.scanners import flag_argument

FIXTURE = Path(__file__).parent / "fixtures" / "flag" / "flags.py"
REL = "fixtures/flag/flags.py"


def test_true_positives_and_no_false_positives():
    found = {c.sites[0].function: c for c in flag_argument.scan(ast.parse(FIXTURE.read_text()), REL, Policy())}
    assert set(found) == {"report", "run"}
    report = found["report"]
    assert report.discriminator_kind == "flag" and report.values == ("verbose",)
    assert report.shape == "split-function" and report.sites[0].discriminator == "verbose"
    assert report.sites[0].arms == 2 and len(report.sites) == 1
    assert found["run"].values == ("strict",) and found["run"].sites[0].arms == 2


def test_pass_through_and_single_test_are_not_reported():
    functions = {c.sites[0].function for c in flag_argument.scan(ast.parse(FIXTURE.read_text()), REL, Policy())}
    assert "forward" not in functions
    assert "once" not in functions


def test_id_does_not_depend_on_line_numbers():
    src = "def f(x: bool):\n    if x:\n        pass\n    if x:\n        pass\n"
    shifted = "\n\n\n" + src
    a = flag_argument.scan(ast.parse(src), "m.py", Policy())
    b = flag_argument.scan(ast.parse(shifted), "m.py", Policy())
    assert [c.id for c in a] == [c.id for c in b] and a[0].sites[0].line != b[0].sites[0].line


def test_negated_test_and_default_false_count():
    src = "def f(x=False):\n    if not x:\n        pass\n    if x:\n        pass\n"
    found = flag_argument.scan(ast.parse(src), "m.py", Policy())
    assert len(found) == 1 and found[0].sites[0].arms == 2


def test_non_bool_parameter_is_not_a_flag():
    src = "def f(x, y=None):\n    if x:\n        pass\n    if x:\n        pass\n    if y:\n        pass\n"
    assert not flag_argument.scan(ast.parse(src), "m.py", Policy())


def test_elif_chain_tests_are_counted():
    src = "def f(x: bool):\n    if x:\n        pass\n    elif other():\n        pass\n    elif not x:\n        pass\n"
    found = flag_argument.scan(ast.parse(src), "m.py", Policy())
    assert len(found) == 1 and found[0].sites[0].arms == 2
