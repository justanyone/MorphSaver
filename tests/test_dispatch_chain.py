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
    assert set(found) == {"literal_chain", "enum_chain", "type_chain", "match_chain", "set_membership",
                          "flag_chain", "type_is_chain"}
    assert found["flag_chain"].discriminator_kind == "flag" and found["flag_chain"].sites[0].discriminator == "ready"
    assert found["type_is_chain"].discriminator_kind == "type"
    assert found["type_is_chain"].sites[0].discriminator == "type(node)"
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


def test_false_positive_fixture_yields_nothing_by_default():
    assert _scan("false_positives.py") == []


def _scan_src(src):
    return dispatch_chain.scan(ast.parse(src), "inline.py", Policy())


def test_nested_chain_counts_once_per_chain():
    src = (
        "def f(kind, x):\n"
        "    if kind == 'a':\n"
        "        if x == 1:\n"
        "            return 1\n"
        "        elif x == 2:\n"
        "            return 2\n"
        "        elif x == 3:\n"
        "            return 3\n"
        "    elif kind == 'b':\n"
        "        return 4\n"
        "    elif kind == 'c':\n"
        "        return 5\n"
    )
    found = _scan_src(src)
    assert sorted(c.sites[0].discriminator for c in found) == ["kind", "x"]
    outer = next(c for c in found if c.sites[0].discriminator == "kind")
    assert outer.sites[0].arms == 3 and outer.sites[0].line == 2


def test_all_return_flag_on_site():
    found = {c.sites[0].function: c.sites[0] for c in _scan("chains.py")}
    assert found["literal_chain"].all_return is True
    assert found["match_chain"].all_return is True
    src = "def g(k):\n    if k == 1:\n        y = 1\n    elif k == 2:\n        return 2\n    elif k == 3:\n        return 3\n"
    assert _scan_src(src)[0].sites[0].all_return is False


def test_attribute_and_call_subjects_are_one_discriminator():
    src = (
        "def h(token):\n"
        "    if token.kind() == 'a':\n"
        "        return 1\n"
        "    elif token.kind() == 'b':\n"
        "        return 2\n"
        "    elif token.kind() == 'c':\n"
        "        return 3\n"
    )
    found = _scan_src(src)
    assert len(found) == 1 and found[0].sites[0].discriminator == "token.kind()"
    assert found[0].values == ("a", "b", "c")
