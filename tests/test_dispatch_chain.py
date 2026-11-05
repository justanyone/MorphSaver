import ast
from pathlib import Path

from morphsaver.policy import Policy
from morphsaver.scanners import dispatch_chain, repeated_dispatch

FIXTURES = Path(__file__).parent / "fixtures" / "dispatch"


def _scan(name, policy=None):
    src = (FIXTURES / name).read_text()
    return dispatch_chain.scan(ast.parse(src), f"fixtures/dispatch/{name}", policy or Policy())


def test_finds_exactly_the_marked_chains():
    found = {c.sites[0].function: c for c in _scan("chains.py")}
    assert set(found) == {"literal_chain", "enum_chain", "type_chain", "match_chain", "set_membership"}
    assert found["literal_chain"].discriminator_kind == "literal-set"
    assert found["literal_chain"].sites[0].arms == 4 and found["literal_chain"].sites[0].has_else
    assert found["enum_chain"].discriminator_kind == "enum" and found["enum_chain"].values == ("A", "B", "C")
    assert found["type_chain"].discriminator_kind == "type" and found["type_chain"].sites[0].discriminator == "isinstance(node)"
    assert found["match_chain"].sites[0].kind == "match" and found["match_chain"].sites[0].has_else
    assert found["set_membership"].values == ("a", "b", "c", "d")


def test_ids_are_stable_across_runs():
    a = {c.id for c in _scan("chains.py")}
    b = {c.id for c in _scan("chains.py")}
    assert a == b and all(i.startswith("dispatch_chain-") for i in a)


def test_min_arms_from_policy():
    found = _scan("chains.py", Policy(min_arms=4))
    assert [c.sites[0].function for c in found] == ["literal_chain"]


def test_repeated_dispatch_groups_same_value_set():
    singles = _scan("repeated_a.py") + _scan("repeated_b.py")
    groups = repeated_dispatch.scan_all(singles, Policy())
    assert len(groups) == 1
    g = groups[0]
    assert g.values == ("circle", "square", "triangle") and len(g.sites) == 2 and g.shape == "strategy-classes"
