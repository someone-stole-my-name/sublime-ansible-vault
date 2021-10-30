import os
import pytest
import sys
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))
import lib.text as text_util  # noqa: E402


@pytest.mark.parametrize(
    "text,expected",
    [
        ("text", "text"),
        ("text\n", "text\n"),
        ("\ntext\n", "\ntext\n"),
        (" text\n text text \n  text", "text\ntext text \ntext"),
    ],
)
def test_unpad(text: str, expected: str):
    assert text_util.unpad(text) == expected


@pytest.mark.parametrize(
    "text,padding,expected",
    [
        ("text", 0, "text"),
        ("text", 1, " text"),
        ("text", 2, "  text"),
        ("text\ntext", 1, " text\n text"),
        ("text\ntext", 2, "  text\n  text"),
        ("text\n", 1, " text\n"),
        ("text\n", 2, "  text\n"),
        ("text\ntext\n", 1, " text\n text\n"),
        ("text\ntext\n", 2, "  text\n  text\n"),
    ],
)
def test_pad(text: str, padding: int, expected: str):
    assert text_util.pad(text, padding) == expected


@pytest.mark.parametrize(
    "line,expected",
    [
        ("foo: bar", 2),
        ("  foo: bar", 4),
        ("    foo: bar", 6),
        ("foo: bar\n", 2),
        ("  foo: bar\n", 4),
        ("    foo: bar\n", 6),
    ],
)
def test_yaml_padding_from_line(line: str, expected: int):
    assert text_util.yaml_padding_from_line(line) == expected
