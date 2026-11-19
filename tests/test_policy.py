"""Path globs: each `**/` also matches no directory."""
import pytest

from morphsaver.policy import Policy, match


@pytest.mark.parametrize("rel,glob,expected", [
    ("a.py", "**/*.py", True),
    ("src/a.py", "**/*.py", True),
    ("src/pkg/a.py", "src/pkg/**/*.py", True),        # top level of the folder: the bug this fixes
    ("src/pkg/sub/a.py", "src/pkg/**/*.py", True),
    ("src/pkg/sub/deep/a.py", "src/pkg/**/*.py", True),
    ("src/other/a.py", "src/pkg/**/*.py", False),
    ("src/pkga.py", "src/pkg**/*.py", False),          # `**/` glued to a name is not a folder wildcard
    ("pkg/tests/t.py", "**/tests/**", True),
    ("tests/t.py", "**/tests/**", True),
    ("pkg/a/b/c.py", "pkg/**/b/**/*.py", True),
    ("pkg/b/c.py", "pkg/**/b/**/*.py", True),
])
def test_match(rel, glob, expected):
    assert match(rel, glob) is expected


def test_include_under_a_folder_takes_its_top_level_files():
    policy = Policy(include=["src/pkg/**/*.py"], exclude=[])
    assert policy.wants("src/pkg/store.py") and policy.wants("src/pkg/sub/x.py")
