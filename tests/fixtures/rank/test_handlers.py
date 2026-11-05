from handlers import handle


def test_handle():
    assert handle("a") == 1


def test_unrelated_text():
    # A comment or a string is not a function reference.
    assert "untouched"
