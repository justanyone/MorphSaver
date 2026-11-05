"""Packaging checks: version string and the `run --out` misuse path."""
import re
from pathlib import Path

import pytest

from morphsaver import __version__
from morphsaver.cli import main

ROOT = Path(__file__).resolve().parent.parent


def test_version_is_0_1_0_everywhere(capsys):
    assert __version__ == "0.1.0"
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "0.1.0"
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'^version = "0\.1\.0"$', pyproject, re.MULTILINE)


def test_run_with_out_fails_cleanly_instead_of_crashing(tmp_path, capsys):
    # Before the fix, `run --out` wrote candidates.json to --out, then rank read
    # candidates.json from its parent directory and crashed with FileNotFoundError.
    out = tmp_path / "cands.json"
    with pytest.raises(SystemExit) as exc:
        main(["run", str(ROOT / "tests" / "fixtures" / "dispatch"), "--out", str(out)])
    assert "--out is not supported" in str(exc.value.code)
    assert not out.exists()
