#!/usr/bin/env python

"""Formatter of white space in text files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2023

Usage:

   whitespace_format.py [OPTIONS] [FILES ...]
"""

import argparse
import re
import sys

LINE_ENDINGS = {
    "linux": "\n",
    "windows": "\r\n",
    "mac": "\r",
}

EMPTY_FILES = {
    "empty": "",
    "one-line-linux": "\n",
    "one-line-windows": "\r\n",
    "one-line-mac": "\r",
}


def die(error_code: int, message: str):
    """Exits the script."""
    print(message)
    print("Exiting.")
    sys.exit(error_code)


def read_file_content(file_name: str) -> str:
    """Reads content of a file."""
    try:
        with open(file_name, "rt", encoding="utf-8") as file:
            return file.read()
    except IOError as exception:
        die(1, f"Cannot open file '{file_name}': {exception}")
    except UnicodeError as exception:
        die(2, f"Cannot decode file '{file_name}': {exception}")
    return ""


def remove_trailing_empty_lines(file_content: str) -> str:
    """Removes trailing empty lines."""
    reduced_file_content = file_content.rstrip("\r\n")
    i = len(reduced_file_content)
    if i >= len(file_content) - 1:
        return file_content
    if file_content[i : i + 2] == "\r\n":
        return file_content[: i + 2]
    return file_content[: i + 1]


def remove_trailing_whitespace(file_content: str) -> str:
    """Removes trailing whitespace from every line."""
    file_content = re.sub(r"[ \t\f\v]*\n", "\n", file_content)
    file_content = re.sub(r"[ \t\f\v]*\r", "\r", file_content)
    file_content = re.sub(r"[ \t\f\v]*$", "", file_content)
    return file_content


def remove_last_end_of_line(file_content: str) -> str:
    """Removes last of line character."""
    if file_content.endswith("\r\n"):
        return file_content[:-2]
    if file_content.endswith("\n") or file_content.endswith("\r"):
        return file_content[:-1]
    return file_content


def fix_end_of_file(file_content: str, mode: str, new_line_marker_guess: str) -> str:
    """Fixes end of line character at the end of the file."""
    if mode == "ignore":
        return file_content

    if mode == "remove":
        return file_content.rstrip("\r\n")

    if mode == "auto":
        new_line_marker = new_line_marker_guess
    else:
        new_line_marker = LINE_ENDINGS[mode]

    return remove_last_end_of_line(file_content) + new_line_marker


def fix_line_endings(file_content: str, mode: str, new_line_marker_guess: str) -> str:
    """Fixes line endings."""
    if mode == "ignore":
        return file_content

    if mode == "auto":
        new_line_marker = new_line_marker_guess
    else:
        new_line_marker = LINE_ENDINGS[mode]

    file_content = file_content.replace("\r\n", "\n")
    file_content = file_content.replace("\r", "\n")
    return file_content.replace("\n", new_line_marker)


def fix_empty_file(file_content: str, mode: str) -> str:
    """Replaces file with an empty file."""
    if mode == "ignore":
        return file_content
    return EMPTY_FILES[mode]


def is_whitespace_only(file_content: str) -> bool:
    """Determines if file consists only of whitespace."""
    return not file_content.strip(" \n\r\t\v\f")


def remove_non_standard_whitespace(file_content: str) -> str:
    """Removes non-standard whitespace characters."""
    return file_content.translate(str.maketrans("", "", "\v\f"))


def replace_tabs(file_content: str, num_spaces: int) -> str:
    """Replaces tabs with spaces."""
    if num_spaces < 0:
        return file_content
    return file_content.replace("\t", num_spaces * " ")


def format_file_content(file_content: str, parsed_argument: argparse.Namespace) -> str:
    """Formats the content of file represented as a string."""
    new_line_marker_guess = guess_new_line_marker(file_content)

    if not file_content:
        return fix_empty_file(file_content, parsed_argument.empty_files)

    if is_whitespace_only(file_content):
        return fix_empty_file(file_content, parsed_argument.whitespace_only_files)

    if parsed_argument.remove_trailing_whitespace:
        file_content = remove_trailing_whitespace(file_content)

    if parsed_argument.remove_trailing_empty_lines:
        file_content = remove_trailing_empty_lines(file_content)

    file_content = replace_tabs(file_content, parsed_argument.replace_tabs_with_spaces)

    if parsed_argument.remove_non_standard_whitespace:
        file_content = remove_non_standard_whitespace(file_content)

    file_content = fix_line_endings(
        file_content, parsed_argument.line_ending, new_line_marker_guess
    )

    file_content = fix_end_of_file(
        file_content, parsed_argument.new_line_at_end_of_file, new_line_marker_guess
    )

    return file_content


def process_file(file_name: str, parsed_argument: argparse.Namespace):
    """Processes a file."""
    file_content = read_file_content(file_name)
    formatted_file_content = format_file_content(file_content, parsed_argument)
    print(formatted_file_content, end="")


def guess_new_line_marker(file_content: str) -> str:
    """Guesses newline character for a file.

    The guess is based on the counts of "\n", "\r" and "\rn" in the file.
    """
    windows_count = file_content.count("\r\n")
    linux_count = file_content.count("\n") - windows_count
    mac_count = file_content.count("\r") - windows_count

    # Pick the new line marker with the highest count.
    # Break ties according to the ordering: Linux > Windows > Mac.
    _, _, new_line_marker_guess = max(
        (linux_count, 3, "\n"),
        (windows_count, 2, "\r\n"),
        (mac_count, 1, "\r"),
    )

    return new_line_marker_guess


def main():
    """Formats white space in text files."""
    parser = argparse.ArgumentParser(
        description="Formats whitespace in text files",
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--check", required=False, action="store_true", default=False)
    parser.add_argument("--diff", required=False, action="store_true", default=False)
    parser.add_argument(
        "--new-line-marker",
        help=(
            "Make new line markers consistent in each file "
            "by replacing '\\r\\n', '\\n', and `\\r` with a consistent new line marker. "
            "auto: Use new line marker that is the most common in each individual file. "
            "ignore: Leave new line markers as is. "
            "linux: Use Linux new line marker '\\n'. "
            "mac: Use Mac new line marker '\\r'. "
            "windows: Use Windows new line marker '\\r\\n'. "
        ),
        required=False,
        default="auto",
        type=str,
        choices=["auto", "ignore", "linux", "windows", "mac"],
    )
    parser.add_argument(
        "--empty-files",
        help=(
            "Replace files of zero length. "
            "ignore: leave empty files as is. "
            "one-line-linux: Replace them with '\\n'. "
            "one-line-mac: Replace them with '\\r'. "
            "one-line-windows: Replace them with '\\r\\n'. "
        ),
        required=False,
        default="ignore",
        choices=["ignore", "one-line-linux", "one-line-windows", "one-line-mac"],
    )
    parser.add_argument(
        "--whitespace-only-files",
        help=(
            "Replace files consisting of whitespace only. "
            "ignore: Leave empty files as is. "
            "empty: Replace each file with an empty file. "
            "one-line-linux: Replace each file with a file consisting of single byte '\\n'. "
            "one-line-mac: Replace each file with a file consisting of single byte '\\r'. "
            "one-line-windows: Replace each file with a file consisting of two bytes '\\r\\n'. "
        ),
        required=False,
        default="ignore",
        choices=["ignore", "empty", "one-line-linux", "one-line-windows", "one-line-mac"],
    )
    parser.add_argument(
        "--new-line-marker-at-end-of-file",
        help=(
            "Fix new line marker at end of each file. "
            "auto: Ensure that the file ends with a new line marker. "
            "Use the marker that is the most commonly occurring in each individual file. "
            "ignore: Leave the end of file as is. "
            "remove: Ensure that file doesn't end with any new line marker "
            "by removing any occurrences of '\n' and '\r' at the end of the file. "
            "linux: Ensure that the file ends with '\\n'. "
            "mac: Ensure that each file ends with '\\r'. "
            "windows: Ensure that each file ends with '\\r\\n'. "
        ),
        required=False,
        default="auto",
        type=str,
        choices=["auto", "ignore", "remove", "linux", "windows", "mac"],
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
        "--remove-non-standard-whitespace",
        help="Remove '\v' and '\f' from each file.",
        required=False,
        default=False,
        action="store_true",
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

    for file_name in parsed_arguments.input_files:
        process_file(file_name, parsed_arguments)


if __name__ == "__main__":
    main()
