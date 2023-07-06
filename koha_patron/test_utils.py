import re

import pytest

from koha_patron.utils import trim_first_two_lines


@pytest.fixture
def text_files(tmp_path):
    trimfile = tmp_path / 'trim.txt'
    notrimfile = tmp_path / 'notrim.txt'
    with open(trimfile, 'w+') as fh:
        fh.write('first line\nsecond line\nthird line\n')
    with open(notrimfile, 'w+') as fh:
        fh.write('does not match\nsecond line\nthird line\n')
    return trimfile, notrimfile


def test_trim(text_files):
    string = 'first line'
    trim_line_count = 0
    notrim_line_count = 0

    with open(text_files[0], 'r') as fh:
        trim_line_count = len(fh.readlines())

    with open(text_files[1], 'r') as fh:
        notrim_line_count = len(fh.readlines())

    trim_first_two_lines(text_files[0], string)
    with open(text_files[0], 'r') as fh:
        lines = fh.readlines()
        # first line no longer matches
        assert re.match(string, lines[0]) == None
        assert trim_line_count - 2 == len(lines)

    trim_first_two_lines(text_files[1], string)
    with open(text_files[1], 'r') as fh:
        lines = fh.readlines()
        assert string != lines[0].rstrip()
        assert notrim_line_count == len(lines)
