import pytest

from workday.utils import get_entries


@pytest.mark.parametrize(
    "data, expected",
    [(["a", "b"], ["a", "b"]), ({"Report_Entry": ["a", "b"]}, ["a", "b"])],
)
def test_get_entries(data, expected):
    assert get_entries(data) == expected


@pytest.mark.parametrize("data", ["not a list", {"foo": "bar"}])
def test_get_entries_raises_exception(data):
    with pytest.raises(Exception):  # type: ignore
        get_entries(data)
