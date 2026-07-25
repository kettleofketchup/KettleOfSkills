"""hooks/scripts/ and skills/.../scripts/ install to unrelated paths and cannot
import each other, so gitpaths.py and receipt.py are vendored to both. Drift
between them is a silent split-brain bug: the gate and the reviewer would
disagree about where receipts live or what makes a receipt valid."""

import pytest

import paths


@pytest.mark.parametrize("name", ["gitpaths.py", "receipt.py"])
def test_vendored_copies_are_byte_identical(name):
    source = (paths.SCRIPTS / name).read_bytes()
    vendored = (paths.HOOK_SCRIPTS / name).read_bytes()
    assert source == vendored, f"run: cp scripts/{name} hooks/scripts/{name}"
