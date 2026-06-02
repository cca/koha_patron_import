import pytest

from workday.utils import get_entries


@pytest.mark.parametrize(
    "data, expected",
    [(["a", "b"], ["a", "b"]), ({"Report_Entry": ["a", "b"]}, ["a", "b"])],
)
def test_get_entries(data, expected):
    assert get_entries(data) == expected


@pytest.mark.parametrize(
    "data, exception",
    [
        ("string raises .get method error", AttributeError),
        ({"dict": "without Report_Entry"}, ValueError),
    ],
)
def test_get_entries_raises_exception(data, exception):
    with pytest.raises(exception):
        get_entries(data)
