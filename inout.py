import sys

_input_buffer = ''


def input_word():
    global _input_buffer
    if _input_buffer == '':
        while _input_buffer == '':
            _input_buffer = input('> ')
        _input_buffer += '\n'
    ch = _input_buffer[0]
    _input_buffer = _input_buffer[1:]
    return ord(ch) % 32768


def output_word(w):
    w %= 32768
    print(chr(w), end='')
