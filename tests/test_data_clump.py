import ast
from pathlib import Path

from morphsaver.policy import Policy
from morphsaver.scanners import data_clump

FIXTURES = Path(__file__).parent / "fixtures" / "clump"


def _scan_dir(sub):
    """Run the per-file pass and the cross-file pass over one fixture directory."""
    facts = []
    for path in sorted((FIXTURES / sub).rglob("*.py")):
        rel = f"fixtures/clump/{path.relative_to(FIXTURES).as_posix()}"
        facts.extend(data_clump.scan(ast.parse(path.read_text()), rel, Policy()))
    return data_clump.scan_all(facts, Policy())


def test_true_positive_five_functions_across_two_modules():
    found = _scan_dir("pkg")
    assert len(found) == 1
    clump = found[0]
    assert clump.discriminator_kind == "clump" and clump.shape == "dataclass-param"
    assert clump.values == ("host", "port", "token")
    assert len(clump.sites) == 5
    assert {s.function for s in clump.sites} == {"connect", "ping", "login", "sync", "stop"}
    assert {s.file.rsplit("/", 1)[-1] for s in clump.sites} == {"a.py", "b.py"}
    assert all(s.lines >= 1 and s.end_line >= s.line for s in clump.sites)


def test_false_positive_self_and_single_letter_names_give_nothing():
    assert _scan_dir("neg") == []


def test_dict_key_clump_in_four_functions():
    found = _scan_dir("keys")
    assert len(found) == 1
    assert found[0].values == ("host", "port", "token")
    assert len(found[0].sites) == 4
    assert found[0].sites[0].discriminator == "keys:d"


def test_non_string_and_single_letter_keys_never_count():
    # d[0] is not a string key; the keys fixture has exactly three usable keys.
    found = _scan_dir("keys")
    assert all("0" not in s.values and "h" not in s.values for c in found for s in c.sites)


def test_output_is_deterministic():
    first = [c.id for c in _scan_dir("pkg")] + [c.id for c in _scan_dir("keys")]
    second = [c.id for c in _scan_dir("pkg")] + [c.id for c in _scan_dir("keys")]
    assert first == second and all("-" in i and not i.endswith("-") for i in first)


def test_fewer_than_four_sites_is_not_a_clump(tmp_path):
    (tmp_path / "x.py").write_text("def f(host, port, token):\n    return host\n\n\ndef g(host, port, token):\n    return port\n")
    facts = data_clump.scan(ast.parse((tmp_path / "x.py").read_text()), "x.py", Policy())
    assert data_clump.scan_all(facts, Policy()) == []
