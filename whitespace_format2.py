#!/usr/bin/env python

"""Formatter of whitespace in text files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2023 - 2024
License: MIT License

Usage:

   python whitespace_format.py [OPTIONS] [FILES ...]
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import sys
from typing import List
from typing import Tuple
from enum import Enum

VERSION = "0.0.6"

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


class ChangeType(Enum):
    """Type of change that happened to a file."""

    # New line marker was added to the end of the file (because it was missing).
    NEW_LINE_MARKER_ADDED_TO_END_OF_FILE = 1

    # New line marker was removed from the end of the file.
    NEW_LINE_MARKER_REMOVED_FROM_END_OF_FILE = 2

    # New line marker was replaced by another one.
    REPLACED_NEW_LINE_MARKER = 3

    # White at the end of a line was removed.
    REMOVED_TRAILING_WHITESPACE = 4

    # Empty line(s) at the end of file were removed.
    REMOVED_EMPTY_LINES = 5

    # An empty file was replaced by a file consisting of single empty line.
    REPLACED_EMPTY_FILE_WITH_ONE_LINE = 6

    # A file consisting of only whitespace was replaced by an empty file.
    REPLACED_WHITESPACE_ONLY_FILE_WITH_EMPTY_FILE = 7

    # A file consisting of only whitespace was replaced by a file consisting of single empty line.
    REPLACED_WHITESPACE_ONLY_FILE_WITH_ONE_LINE = 8

    # A tab character was replaces by space character(s).
    REPLACED_TAB_WITH_SPACES = 9

    # A tab character was removed.
    REMOVED_TAB = 10

    # A non-standard whitespace character (`\f` or `\v`) was replaced by a space character.
    REPLACED_NONSTANDARD_WHITESPACE = 11

    # A non-standard whitespace character (`\f` or `\v`) was removed.
    REMOVED_NONSTANDARD_WHITESPACE = 12


@dataclasses.dataclass
class Change:
    """Description of a change of the content of a file."""

    change_type: ChangeType
    line_number: int
    changed_from: str
    changed_to: str

    def message(self, check_only: bool) -> str:
        """Returns a message describing the change."""
        check_only_word = "would be" if check_only else " "

        if self.change_type == ChangeType.NEW_LINE_MARKER_ADDED_TO_END_OF_FILE:
            return f"New line marker{check_only_word}added to the end of the file."

        if self.change_type == ChangeType.NEW_LINE_MARKER_REMOVED_FROM_END_OF_FILE:
            return f"New line marker{check_only_word}removed from the end of the file."

        if self.change_type == ChangeType.REPLACED_NEW_LINE_MARKER:
            return (
                f"New line marker '{self.changed_from}'"
                f"{check_only_word}replaced by '{self.changed_to}'."
            )

        if self.change_type == ChangeType.REMOVED_TRAILING_WHITESPACE:
            return f"Trailing whitespace{check_only_word}removed."

        if self.change_type == ChangeType.REMOVED_EMPTY_LINES:
            return f"Empty line(s) at the end of the file{check_only_word}removed."

        if self.change_type == ChangeType.REPLACED_EMPTY_FILE_WITH_ONE_LINE:
            return f"Empty file{check_only_word}replaced with a single empty line."

        if self.change_type == ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_EMPTY_FILE:
            return f"File{check_only_word}replaced with an empty file."

        if self.change_type == ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_ONE_LINE:
            return f"File{check_only_word}replaced with a single empty line."

        if self.change_type == ChangeType.REPLACED_TAB_WITH_SPACES:
            return f"Tab{check_only_word}replaced with spaces."

        if self.change_type == ChangeType.REMOVED_TAB:
            return f"Tab{check_only_word}removed."

        if self.change_type == ChangeType.REPLACED_NONSTANDARD_WHITESPACE:
            return (
                f"Non-standard whitespace character '{self.changed_from}'"
                f"{check_only_word}replaced by a space."
            )

        if self.change_type == ChangeType.REMOVED_NONSTANDARD_WHITESPACE:
            return (
                f"Non-standard whitespace character '{self.changed_from}'{check_only_word}removed."
            )

        raise ValueError(f"Unknown change type: {self.change_type}")

    def color_print(self, parsed_arguments: argparse.Namespace) -> None:
        """Prints a message in color."""
        color_print(
            f"[BOLD][BLUE]↳ line {self.line_number + 1}: "
            f"[WHITE]{self.message(parsed_arguments.check_only)}[RESET_ALL]",
            parsed_arguments,
        )


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


def string_to_hex(text: str) -> str:
    """Converts a string into a human-readable hexadecimal representation.

    This function is for debugging purposes only. It is used only during development.
    """
    return ":".join(f"{ord(character):02x}" for character in text)


def die(error_code: int, message: str = ""):
    """Exits the script."""
    if message:
        print(message)
    sys.exit(error_code)


def read_file_content(file_name: str, encoding: str) -> str:
    """Reads content of a file."""
    try:
        with open(file_name, "r", encoding=encoding, newline="") as file:
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


def format_file_content(
    file_content: str, parsed_arguments: argparse.Namespace  # pylint: disable=unused-argument
) -> Tuple[str, List[Change]]:
    """Applies a function to the content of a file.

    Args:
        file_content: Content of the file.
        parsed_arguments: Parsed command line arguments.

    Returns:
        A pair consisting of the formatted file content and a list of changes.
    """
    # TODO: Implement this function.
    return "", []


def reformat_file(file_name: str, parsed_arguments: argparse.Namespace) -> bool:
    """Reformats a file.

    Args:
        file_name: Name of the file to reformat.
        parsed_arguments: Parsed command line arguments.

    Returns:
         True if the file was changed, False otherwise.
    """
    file_content = read_file_content(file_name, parsed_arguments.encoding)
    formatted_file_content, file_changes = format_file_content(file_content, parsed_arguments)
    if parsed_arguments.verbose:
        color_print(f"Processing file '{file_name}'...", parsed_arguments)
    if parsed_arguments.check_only:
        if file_changes:
            color_print(
                f"[RED]✘[RESET_ALL] [BOLD][WHITE]{file_name} "
                f"[RED]needs to be formatted[RESET_ALL]",
                parsed_arguments,
            )
            for line_change in file_changes:
                print("   ", end="")
                line_change.color_print(parsed_arguments)
        else:
            if parsed_arguments.verbose:
                color_print(
                    f"[GREEN]✔[RESET_ALL] [WHITE]{file_name} "
                    f"[BLUE]would be left unchanged[RESET_ALL]",
                    parsed_arguments,
                )
    else:
        if file_changes:
            color_print(f"[WHITE]Reformatted [BOLD]{file_name}[RESET_ALL]", parsed_arguments)
            for line_change in file_changes:
                print("   ", end="")
                line_change.color_print(parsed_arguments)
            write_file(
                file_name,
                formatted_file_content,
                parsed_arguments.encoding,
            )
        else:
            if parsed_arguments.verbose:
                color_print(f"[WHITE]{file_name} [BLUE]left unchanged[RESET_ALL]", parsed_arguments)

    return bool(file_changes)


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
