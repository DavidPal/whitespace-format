#!/usr/bin/env python

"""Formatter of whitespace in text files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2023

Usage:

   python whitespace_format.py [OPTIONS] [FILES ...]
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import re
import sys
from typing import Dict
from typing import List

VERSION = "0.0.3"

# Regular expression that does NOT match any string.
UNMATCHABLE_REGEX = "$."

END_OF_LINE_MARKERS = {
    "windows": "\r\n",
    "linux": "\n",
    "mac": "\r",
}

COLORS = {
    "RESET_ALL": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "UNDERLINE": "\033[4m",
    "BLINK": "\033[5m",
    "REVERSE": "\033[7m",
    "HIDDEN": "\033[8m",
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "LIGHT_GRAY": "\033[37m",
    "DARK_GRAY": "\033[90m",
    "LIGHT_RED": "\033[91m",
    "LIGHT_GREEN": "\033[92m",
    "LIGHT_YELLOW": "\033[93m",
    "LIGHT_BLUE": "\033[94m",
    "LIGHT_MAGENTA": "\033[95m",
    "LIGHT_CYAN": "\033[96m",
    "WHITE": "\033[97m",
}


def color_print(message: str, parsed_arguments: argparse.Namespace):
    """Outputs a colored message."""
    if parsed_arguments.quiet:
        return
    for color, code in COLORS.items():
        if parsed_arguments.color:
            message = message.replace(f"[{color}]", code)
        else:
            message = message.replace(f"[{color}]", "")
    print(message)


def die(error_code: int, message: str = ""):
    """Exits the script."""
    if message:
        print(message)
    sys.exit(error_code)


def read_file_content(file_name: str, encoding: str) -> str:
    """Reads content of a file."""
    try:
        with open(file_name, "r", encoding=encoding) as file:
            return file.read()
    except IOError as exception:
        die(2, f"Cannot read file '{file_name}': {exception}")
    except UnicodeError as exception:
        die(3, f"Cannot decode file '{file_name}': {exception}")
    return ""


def write_file(file_name: str, file_content: str, encoding: str):
    """Writes data to a file."""
    try:
        with open(file_name, "w", encoding=encoding) as file:
            file.write(file_content)
    except IOError as exception:
        die(4, f"Cannot write to file '{file_name}': {exception}")


@dataclasses.dataclass
class Line:
    """Line of a text file.

    The line is split into two parts:
        1) Content
        2) End of line marker ("\n", or "\r", or "\r\n")
    """

    content: str
    end_of_line_marker: str

    @staticmethod
    def create_from_string(line: str) -> Line:
        """Creates a line from a string.

        The function splits the input into content and end_of_line_marker.
        """
        for end_of_line_marker in ["\r\n", "\n", "\r"]:
            if line.endswith(end_of_line_marker):
                return Line(line[: -len(end_of_line_marker)], end_of_line_marker)
        return Line(line, "")


def split_lines(text: str) -> List[Line]:
    """Splits a string into lines."""
    lines: List[Line] = []
    current_line = ""
    for i, char in enumerate(text):
        current_line += char
        if (char == "\n") or (
            (char == "\r") and ((i >= len(text) - 1) or (not text[i + 1] == "\n"))
        ):
            lines.append(Line.create_from_string(current_line))
            current_line = ""

    if current_line:
        lines.append(Line.create_from_string(current_line))

    return lines


def concatenate_lines(lines: List[Line]) -> str:
    """Concatenates a list of lines into a single string including end-of-line markers."""
    return "".join(line.content + line.end_of_line_marker for line in lines)


def guess_end_of_line_marker(lines: List[Line]) -> str:
    """Guesses the end of line marker.

    The function returns the most common end-of-line marker.
    If no end-of-line marker is present, default to the Linux "\n" end-of-line marker.
    """
    counts: Dict[str, int] = {"\n": 0, "\r": 0, "\r\n": 0}
    for line in lines:
        if line.end_of_line_marker in counts:
            counts[line.end_of_line_marker] += 1
    for end_of_line_marker in counts:
        if counts[end_of_line_marker] == max(counts.values()):
            return end_of_line_marker
    return "\n"


def remove_trailing_empty_lines(lines: List[Line]) -> List[Line]:
    """Removes trailing empty lines.

    If there are no lines, empty list is returned.
    If all lines are empty, the first line is kept.
    """
    num_empty_trailing_lines = 0
    while (num_empty_trailing_lines < len(lines) - 1) and (
        not lines[-num_empty_trailing_lines - 1].content
    ):
        num_empty_trailing_lines += 1
    return copy.deepcopy(lines[: len(lines) - num_empty_trailing_lines])


def remove_trailing_whitespace(lines: List[Line]) -> List[Line]:
    """Removes trailing whitespace from every line."""
    return [
        Line(
            re.sub(r"[ \n\r\t\f\v]*$", "\n", line.content),
            line.end_of_line_marker,
        )
        for line in lines
    ]


def normalize_new_line_markers(lines: List[Line], new_end_of_line_marker: str) -> List[Line]:
    """Replaces end-of-line marker in all lines with a new marker.

    Lines without end-of-line markers (i.e. possibly the last line) are left unchanged.
    """
    return [
        Line(line.content, new_end_of_line_marker) if line.end_of_line_marker else line
        for line in lines
    ]


def add_new_line_marker_at_end_of_file(
    lines: List[Line], new_end_of_line_marker: str
) -> List[Line]:
    """Adds new end-of-line marker to the end of file if it is missing."""
    if not lines:
        return [Line("", new_end_of_line_marker)]
    lines = copy.deepcopy(lines)
    lines[-1] = Line(lines[-1].content, new_end_of_line_marker)
    return lines


def normalize_empty_file(lines: List[Line], mode: str, new_end_of_line_marker: str) -> List[Line]:
    """Replaces file with an empty file."""
    if mode == "empty":
        return []
    if mode == "one-line":
        return [Line("", new_end_of_line_marker)]
    return copy.deepcopy(lines)


def is_whitespace_only(lines: List[Line]) -> bool:
    """Determines if file consists only of whitespace."""
    for line in lines:
        if line.content.strip(" \n\r\t\v\f"):
            return False
    return True


def normalize_non_standard_whitespace(lines: List[Line], mode: str) -> List[Line]:
    """Removes non-standard whitespace characters."""
    if mode == "ignore":
        return copy.deepcopy(lines)
    if mode == "replace":
        return [
            Line(line.content.translate(str.maketrans("\v\f", "  ", "")), line.end_of_line_marker)
            for line in lines
        ]
    return [
        Line(line.content.translate(str.maketrans("", "", "\v\f")), line.end_of_line_marker)
        for line in lines
    ]


def replace_tabs_with_spaces(lines: List[Line], num_spaces: int) -> List[Line]:
    """Replaces tabs with spaces."""
    if num_spaces < 0:
        return copy.deepcopy(lines)
    return [
        Line(line.content.replace("\t", num_spaces * " "), line.end_of_line_marker)
        for line in lines
    ]


def compute_difference(original_lines: List[Line], new_lines: List[Line]) -> List[int]:
    """Computes the indices of lines that differ."""
    line_numbers = [
        line_number
        for line_number, (original_line, new_line) in enumerate(zip(original_lines, new_lines))
        if not original_line == new_line
    ]
    if len(original_lines) != len(new_lines):
        line_numbers.append(min(len(original_lines), len(new_lines)))
    return line_numbers
