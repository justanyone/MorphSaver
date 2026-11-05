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


REPEATED = Path(__file__).parent / "fixtures" / "repeated"


def _repeated_singles(folder, policy=None):
    policy = policy or Policy()
    return [candidate for path in sorted((REPEATED / folder).glob("*.py"))
            for candidate in dispatch_chain.scan(ast.parse(path.read_text()), path.name, policy)]


def test_repeated_jaccard_across_files_and_policy():
    policy = Policy(caution=["second.py"], deny=["third.py"])
    singles = _repeated_singles("overlap", policy)
    groups = repeated_dispatch.scan_all(singles, policy)
    assert len(groups) == 1
    group = groups[0]
    assert group.values == ("A", "B", "C", "D")
    assert len(group.sites) == 3 and group.policy == "deny"
    assert group.shape == "strategy-classes"
    assert {s.discriminator for s in group.sites} == {"kind", "category", "tag"}
    assert repeated_dispatch.scan_all(singles, Policy(jaccard=0.8))[0].sites == group.sites[:2]
    assert repeated_dispatch.scan_all(singles, Policy(min_sites=4)) == []


def test_repeated_weak_overlap_is_not_a_group():
    assert repeated_dispatch.scan_all(_repeated_singles("weak"), Policy()) == []


def test_repeated_enum_bare_and_literal_names_group():
    groups = repeated_dispatch.scan_all(_repeated_singles("enum"), Policy())
    assert len(groups) == 1 and len(groups[0].sites) == 3
    assert groups[0].values == ("A", "B", "C", "D")


def test_repeated_is_order_independent_and_does_not_keep_state():
    from concurrent.futures import ThreadPoolExecutor

    singles = _repeated_singles("overlap")
    before = [c.to_json() for c in singles]
    expected = [c.to_json() for c in repeated_dispatch.scan_all(singles, Policy())]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda items: [c.to_json() for c in repeated_dispatch.scan_all(items, Policy())],
                                [singles, list(reversed(singles)), singles + singles]))
    assert results == [expected] * 3
    assert [c.to_json() for c in singles] == before
    assert repeated_dispatch.scan_all([], Policy()) == []


def test_repeated_id_depends_only_on_value_union():
    from dataclasses import replace

    singles = _repeated_singles("overlap")
    original = repeated_dispatch.scan_all(singles, Policy())[0]
    moved = [replace(c, id=f"moved-{i}", sites=[replace(s, file=f"moved-{i}.py", line=s.line + 20)
                                              for s in c.sites]) for i, c in enumerate(singles)]
    assert repeated_dispatch.scan_all(moved, Policy())[0].id == original.id
    assert repeated_dispatch.scan_all(singles[:2], Policy())[0].id == original.id


def test_repeated_rejects_invalid_jaccard():
    import pytest

    for threshold in (-0.1, 1.1, float("nan")):
        with pytest.raises(ValueError, match="jaccard"):
            repeated_dispatch.scan_all([], Policy(jaccard=threshold))


def test_repeated_threshold_boundary_and_transitive_union():
    from dataclasses import replace

    singles = _repeated_singles("overlap")
    # Adjacent sets share 3 of 5 union values (0.6). The end sets share only 2 of 6.
    values = [("A", "B", "C", "D"), ("B", "C", "D", "E"), ("C", "D", "E", "F")]
    singles = [replace(c, values=v, sites=[replace(c.sites[0], values=v)]) for c, v in zip(singles, values)]
    groups = repeated_dispatch.scan_all(singles, Policy())
    assert len(groups) == 1 and len(groups[0].sites) == 3
    assert groups[0].values == ("A", "B", "C", "D", "E", "F")
    assert repeated_dispatch.scan_all(singles, Policy(jaccard=0.61)) == []
    assert repeated_dispatch.scan_all(list(reversed(singles)), Policy())[0].to_json() == groups[0].to_json()
