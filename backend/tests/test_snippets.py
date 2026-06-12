import pytest
from backend.terraform.snippets import load_snippet, SNIPPET_FILES


@pytest.mark.parametrize("key", SNIPPET_FILES.keys())
def test_snippet_loads_without_error(key):
    content = load_snippet(key)
    assert content
    assert "resource " in content


def test_unknown_snippet_key_raises():
    with pytest.raises(KeyError):
        load_snippet("does_not_exist")
