"""Text related functions."""
from sublime_ansible_vault.lib.util import loop_last


def unpad(text: str) -> str:
    """Remove all leading whitespaces from a string."""
    new_text = ''
    for last, line in loop_last(text.split('\n')):
        new_text = new_text + line.lstrip()
        if not last:
            new_text = new_text + '\n'
    return new_text


def pad(text: str, padding: int) -> str:
    """Add padding number of spaces to each line of a string."""
    if padding is None or padding == 0:
        return text

    new_text = ''
    for last, line in loop_last(text.split('\n')):
        if line == '':
            continue
        for s in range(0, padding):
            new_text = new_text + ' '
        new_text = new_text + line
        if not last:
            new_text = new_text + '\n'
    return new_text


def yaml_padding_from_line(line: str) -> int:
    """Calculate number of spaces required to create a YAML multiline string.

    eg:
        line='foo: bar' -> 2
        line='  foo: bar' -> 4
    """
    last_c = None
    padding = 0
    for i, c in enumerate(line):
        if i == 0 and c != ' ':
            padding = 2
            break
        if last_c == ' ' and c != ' ':
            padding = i + 2
            break
        last_c = c
        padding = i
    return padding
