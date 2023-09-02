#!/usr/bin/env python

"""Formatter of whitespace in text files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2023

Usage:

   python whitespace_format.py [OPTIONS] [FILES ...]
"""

# pylint: disable=duplicate-code

from __future__ import annotations

import argparse
import copy
import dataclasses
import pathlib
import re
import sys
from typing import Callable
from typing import Dict
from typing import List

VERSION = "0.0.4"

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
    Ties are broken in order Linux "\n", Mac "\r", Windows "\r\n".
    If no end-of-line marker is present, default to the Linux "\n" end-of-line marker.
    """
    counts: Dict[str, int] = {"\n": 0, "\r": 0, "\r\n": 0}
    for line in lines:
        if line.end_of_line_marker in counts:
            counts[line.end_of_line_marker] += 1
    max_count = max(counts.values())
    for end_of_line_marker, count in counts.items():
        if count == max_count:
            return end_of_line_marker
    return "\n"  # This return statement is never executed.


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


def remove_dummy_lines(lines: List[Line]) -> List[Line]:
    """Remove empty lines that also have empty end-of-line markers."""
    return [line for line in lines if line.content or line.end_of_line_marker]


def remove_trailing_whitespace(lines: List[Line]) -> List[Line]:
    """Removes trailing whitespace from every line."""
    lines = [
        Line(
            re.sub(r"[ \n\r\t\f\v]*$", "", line.content),
            line.end_of_line_marker,
        )
        for line in lines
    ]
    return remove_dummy_lines(lines)


def normalize_end_of_line_markers(lines: List[Line], new_end_of_line_marker: str) -> List[Line]:
    """Replaces end-of-line marker in all lines with a new end-of-line marker.

    Lines without end-of-line markers (i.e. possibly the last line) are left unchanged.
    """
    return [
        Line(line.content, new_end_of_line_marker) if line.end_of_line_marker else line
        for line in lines
    ]


def remove_all_end_of_line_markers_from_end_of_file(lines: List[Line]) -> List[Line]:
    """Removes all end-of-line markers from the end of the file."""
    lines = remove_trailing_empty_lines(lines)
    if not lines:
        return []
    lines[-1] = Line(lines[-1].content, "")
    return remove_dummy_lines(lines)


def add_end_of_line_marker_at_end_of_file(
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


@dataclasses.dataclass
class ChangeDescription:
    """Description of a change of the content of a file."""

    check_only: str
    change: str


@dataclasses.dataclass
class LineChange:
    """Description of a change on a particular line."""

    check_only: str
    change: str
    line_number: int


class FileContentTracker:
    """Tracks changes of the content of a file as it undergoes formatting."""

    def __init__(self, lines: List[Line]):
        """Initializes an instance of the file content tracker."""
        self.initial_lines = lines
        self.lines = copy.deepcopy(lines)
        self.line_changes: List[LineChange] = []

    def format(self, change: ChangeDescription, function: Callable[..., List[Line]], *args):
        """Applies a change to the content of the file."""
        previous_content = self.lines
        self.lines = function(self.lines, *args)
        if previous_content != self.lines:
            line_numbers = compute_difference(previous_content, self.lines)
            for line_number in line_numbers:
                self.line_changes.append(LineChange(change.check_only, change.change, line_number))

    def is_changed(self) -> bool:
        """Determines if the file content has changed."""
        return self.lines != self.initial_lines


def format_file_content(
    file_content_tracker: FileContentTracker,
    parsed_arguments: argparse.Namespace,
):
    """Formats the content of file represented as a string."""
    new_line_marker = END_OF_LINE_MARKERS.get(
        parsed_arguments.new_line_marker,
        guess_end_of_line_marker(file_content_tracker.initial_lines),
    )

    if is_whitespace_only(file_content_tracker.initial_lines):
        changes = {
            "ignore": ChangeDescription("", ""),
            "empty": ChangeDescription(
                check_only="File needs to be replaced with an empty file.",
                change="File was replaced with an empty file.",
            ),
            "one-line": ChangeDescription(
                check_only=(
                    f"File must be replaced with a single-line empty line {repr(new_line_marker)}."
                ),
                change=(
                    f"File was replaced with a single-line empty line {repr(new_line_marker)}."
                ),
            ),
        }
        if not file_content_tracker.initial_lines:
            file_content_tracker.format(
                changes[parsed_arguments.normalize_empty_files],
                normalize_empty_file,
                parsed_arguments.normalize_empty_files,
                new_line_marker,
            )
        else:
            file_content_tracker.format(
                changes[parsed_arguments.normalize_whitespace_only_files],
                normalize_empty_file,
                parsed_arguments.normalize_whitespace_only_files,
                new_line_marker,
            )

    else:
        if parsed_arguments.remove_trailing_whitespace:
            file_content_tracker.format(
                ChangeDescription(
                    check_only="Whitespace at the end of line needs to be removed.",
                    change="Whitespace at the end of line was removed.",
                ),
                remove_trailing_whitespace,
            )

        if parsed_arguments.remove_trailing_empty_lines:
            file_content_tracker.format(
                ChangeDescription(
                    check_only="Empty line(s) at the end of file need to be removed.",
                    change="Empty line(s) at the end of file were removed.",
                ),
                remove_trailing_empty_lines,
            )

        file_content_tracker.format(
            ChangeDescription(
                check_only="Tabs need to be replaced with spaces.",
                change="Tabs were replaced by spaces.",
            ),
            replace_tabs_with_spaces,
            parsed_arguments.replace_tabs_with_spaces,
        )

        file_content_tracker.format(
            ChangeDescription(
                check_only=(
                    "Non-standard whitespace characters need to be removed or replaced by spaces."
                ),
                change="Non-standard whitespace characters were removed or replaced by spaces.",
            ),
            normalize_non_standard_whitespace,
            parsed_arguments.normalize_non_standard_whitespace,
        )

        if parsed_arguments.normalize_new_line_markers:
            file_content_tracker.format(
                ChangeDescription(
                    check_only=(
                        f"New line marker(s) need to be replaced with {repr(new_line_marker)}."
                    ),
                    change=f"New line marker(s) were replaced with {repr(new_line_marker)}.",
                ),
                normalize_end_of_line_markers,
                new_line_marker,
            )

        if parsed_arguments.add_new_line_marker_at_end_of_file:
            file_content_tracker.format(
                ChangeDescription(
                    check_only=f"New line marker needs to be added to the end of the file, "
                    f"or replaced with {repr(new_line_marker)}.",
                    change=f"New line marker was added to the end of the file, "
                    f"or replaced with {repr(new_line_marker)}.",
                ),
                add_end_of_line_marker_at_end_of_file,
                new_line_marker,
            )
        elif parsed_arguments.remove_new_line_marker_from_end_of_file:
            file_content_tracker.format(
                ChangeDescription(
                    check_only="New line marker(s) need to removed from the end of the file.",
                    change="New line marker(s) were removed from the end of the file.",
                ),
                remove_all_end_of_line_markers_from_end_of_file,
            )


def reformat_file(file_name: str, parsed_arguments: argparse.Namespace) -> bool:
    """Reformats a file."""
    file_content = read_file_content(file_name, parsed_arguments.encoding)
    lines = split_lines(file_content)
    file_content_tracker = FileContentTracker(lines)
    format_file_content(file_content_tracker, parsed_arguments)
    is_changed = file_content_tracker.is_changed()
    if parsed_arguments.verbose:
        color_print(f"Processing file '{file_name}'...", parsed_arguments)
    if parsed_arguments.check_only:
        if is_changed:
            color_print(
                f"[RED]✘[RESET_ALL] [BOLD][WHITE]{file_name} "
                f"[RED]needs to be formatted[RESET_ALL]",
                parsed_arguments,
            )
            for line_change in file_content_tracker.line_changes:
                color_print(
                    f"   [BOLD][BLUE]↳ line {line_change.line_number + 1}: "
                    f"[WHITE]{line_change.check_only}[RESET_ALL]",
                    parsed_arguments,
                )
        else:
            if parsed_arguments.verbose:
                color_print(
                    f"[GREEN]✔[RESET_ALL] [WHITE]{file_name} "
                    f"[BLUE]would be left unchanged[RESET_ALL]",
                    parsed_arguments,
                )
    else:
        if is_changed:
            color_print(f"[WHITE]Reformatted [BOLD]{file_name}[RESET_ALL]", parsed_arguments)
            for line_change in file_content_tracker.line_changes:
                color_print(
                    f"   [BOLD][BLUE]↳ line {line_change.line_number + 1}: "
                    f"[WHITE]{line_change.change}[RESET_ALL]",
                    parsed_arguments,
                )
            write_file(
                file_name, concatenate_lines(file_content_tracker.lines), parsed_arguments.encoding
            )
        else:
            if parsed_arguments.verbose:
                color_print(f"[WHITE]{file_name} [BLUE]left unchanged[RESET_ALL]", parsed_arguments)
    return is_changed


def reformat_files(file_names: List[str], parsed_arguments: argparse.Namespace):
    """Reformats multiple files."""
    color_print(f"Processing {len(file_names)} file(s)...", parsed_arguments)
    num_changed_files = 0
    for file_name in file_names:
        is_formatted = reformat_file(file_name, parsed_arguments)
        if is_formatted:
            num_changed_files += 1

    if parsed_arguments.check_only:
        message = ""
        if num_changed_files > 0:
            message += f"[BOLD][BLUE]{num_changed_files} file(s) "
            message += "[WHITE]need to be formatted,[RESET_ALL] "
        message += f"[BLUE]{len(file_names) - num_changed_files} file(s) "
        message += "[WHITE]would be left unchanged.[RESET_ALL]"
        color_print(message, parsed_arguments)
        if num_changed_files > 0:
            die(1)
    else:
        message = ""
        if num_changed_files > 0:
            message += f"[BOLD][BLUE]{num_changed_files} file(s) "
            message += "[WHITE]changed,[RESET_ALL] "
        message += f"[BLUE]{len(file_names) - num_changed_files} files(s) "
        message += "[WHITE]left unchanged.[RESET_ALL]"
        color_print(message, parsed_arguments)


def find_all_files_recursively(file_name: str, follow_symlinks: bool) -> List[str]:
    """Finds files in directories recursively."""
    if (not follow_symlinks) and pathlib.Path(file_name).is_symlink():
        return []

    if pathlib.Path(file_name).is_file():
        return [file_name]

    if pathlib.Path(file_name).is_dir():
        return [
            expanded_file_name
            for inner_file in sorted(pathlib.Path(file_name).iterdir())
            for expanded_file_name in find_all_files_recursively(str(inner_file), follow_symlinks)
        ]

    return []


def find_files_to_process(file_names: List[str], parsed_arguments: argparse.Namespace) -> List[str]:
    """Finds files that need to be processed.

    The function excludes files that match the regular expression specified
    by the --exclude command line option.
    """
    return [
        expanded_file_name
        for file_name in file_names
        for expanded_file_name in find_all_files_recursively(
            file_name, parsed_arguments.follow_symlinks
        )
        if not re.search(parsed_arguments.exclude, expanded_file_name)
    ]


def parse_command_line() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        prog="whitespace-format",
        description="Linter and formatter for source code files and text files",
        allow_abbrev=False,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--check-only",
        help="Do not format files. Only report which files would be formatted.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--encoding",
        help=(
            "Text encoding for both reading and writing files. Default encoding is utf-8. "
            "List of supported encodings can be found at "
            "https://docs.python.org/3/library/codecs.html#standard-encodings"
        ),
        required=False,
        default="utf-8",
        type=str,
    )
    parser.add_argument(
        "--verbose",
        help="Print more messages than normally.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--quiet",
        help="Do not print any messages, except for errors when reading or writing files.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--color",
        help="Print messages in color.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--follow-symlinks",
        help="Follow symlinks when looking for files. By default this option is turned off.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--exclude",
        help=(
            "Regular expression that specifies which files to exclude. "
            "The regular expression is evaluated on the path of each file. "
            "Example #1: --exclude=\"(.jpeg|.png)$\" excludes files "
            "with '.jpeg' or '.png' extension. "
            "Example #2: --exclude=\".git/\" excludes all files in the '.git' directory. "
        ),
        required=False,
        type=str,
        default=UNMATCHABLE_REGEX,
    )
    parser.add_argument(
        "--new-line-marker",
        help=(
            "Specifies what new line marker to use. "
            "auto: Use new line marker that is the most common in each individual file. "
            "If no new line marker is present in the file, Linux '\\n' is used."
            "linux: Use Linux new line marker '\\n'. "
            "mac: Use Mac new line marker '\\r'. "
            "windows: Use Windows new line marker '\\r\\n'. "
        ),
    )
    parser.add_argument(
        "--normalize-new-line-markers",
        help=(
            "Make new line markers consistent in each file "
            "by replacing '\\r\\n', '\\n', and `\\r` with a consistent new line marker. "
        ),
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--normalize-empty-files",
        help=(
            "Replace files of zero length. "
            "ignore: Leave empty files as is. "
            "empty: Same as ignore. "
            "one-line: Replace the file with a single empty line with an end of line marker. "
            "If --whitespace-only-files is set to value other than 'ignore', "
            "it overrides --empty-files setting. "
        ),
        required=False,
        default="ignore",
        choices=["ignore", "empty", "one-line"],
    )
    parser.add_argument(
        "--normalize-whitespace-only-files",
        help=(
            "Replace files consisting of whitespace only. "
            "ignore: Leave empty files as is. "
            "empty: Replace each file with an empty file. "
            "one-line: Replace the file with a single empty line with an end of line marker. "
            "If --normalize-whitespace-only-files is set to value other than 'ignore', "
            "it overrides --normalize-empty-files setting. "
        ),
        required=False,
        default="ignore",
        choices=["ignore", "empty", "one-line"],
    )
    parser.add_argument(
        "--add-new-line-marker-at-end-of-file",
        help="Add missing new line marker at end of each file.",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--remove-new-line-marker-from-end-of-file",
        help="Remove new line markers from the end of each file.",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--remove-trailing-whitespace",
        help="Remove whitespace at the end of each line.",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--remove-trailing-empty-lines",
        help="Remove empty lines at the end of each file.",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--normalize-non-standard-whitespace",
        help=(
            "Replace or remove non-standard whitespace characters '\\v' and '\\f' in each file. "
            "ignore: Leave '\\v' and '\\f' as is. "
            "remove: Remove all occurrences of '\\v' and '\\f'. "
            "replace: Replace each occurrence of '\\v' and '\\f' with a single space. "
        ),
        required=False,
        default="ignore",
        type=str,
        choices=["ignore", "remove", "replace"],
    )
    parser.add_argument(
        "--replace-tabs-with-spaces",
        help=(
            "Replace tabs with spaces. "
            "The parameter specifies number of spaces to use. "
            "If the parameter is negative, tabs are not replaced."
        ),
        required=False,
        default=-1,
        type=int,
    )
    parser.add_argument("input_files", help="List of input files", nargs="+", default=[], type=str)

    parsed_arguments = parser.parse_args()

    # Fix command line arguments.
    if parsed_arguments.normalize_whitespace_only_files == "empty":
        parsed_arguments.normalize_empty_files = parsed_arguments.normalize_whitespace_only_files

    if parsed_arguments.verbose:
        parsed_arguments.quiet = False

    return parsed_arguments


def main():
    """Formats white space in text files."""
    parsed_arguments = parse_command_line()
    file_names = find_files_to_process(parsed_arguments.input_files, parsed_arguments)
    reformat_files(file_names, parsed_arguments)


if __name__ == "__main__":
    main()
