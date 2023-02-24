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
        die(1, f"Cannot open file '{file_name}': {exception.strerror}")
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
    if mode == "keep":
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
    if mode == "keep":
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


def format_file_content(file_content: str, parsed_argument: argparse.Namespace) -> str:
    """Formats the content of file represented as a string."""
    new_line_marker_guess = guess_new_line_marker(file_content)

    if not file_content:
        return fix_empty_file(file_content, parsed_argument.empty_files)

    if not file_content.strip():
        return fix_empty_file(file_content, parsed_argument.whitespace_only_files)

    if parsed_argument.remove_trailing_whitespace:
        file_content = remove_trailing_whitespace(file_content)

    if parsed_argument.remove_trailing_empty_lines:
        file_content = remove_trailing_empty_lines(file_content)

    file_content = fix_line_endings(
        file_content, parsed_argument.line_endings, new_line_marker_guess
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
    """Guesses newline character for a file."""
    crlf_count = file_content.count("\r\n")
    lf_count = file_content.count("\n") - crlf_count
    cr_count = file_content.count("\r") - crlf_count

    # Pick the new line marker with the highest count.
    # Break ties in favor of "\n".
    _, _, new_line_marker_guess = max(
        (lf_count, 3, "\n"),
        (crlf_count, 2, "\r\n"),
        (cr_count, 1, "\r"),
    )

    return new_line_marker_guess


def main():
    """Reads the input files and outputs their properly formatted versions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=False, action="store_true", default=False)
    parser.add_argument("--diff", required=False, action="store_true", default=False)
    parser.add_argument(
        "--line-endings",
        required=False,
        default="auto",
        type=str,
        choices=["auto", "keep", "linux", "windows", "mac"],
    )
    parser.add_argument(
        "--empty-files",
        required=False,
        default="ignore",
        choices=["ignore", "empty", "one-line-linux", "one-line-windows", "one-line-mac"],
    )
    parser.add_argument(
        "--whitespace-only-files",
        required=False,
        default="ignore",
        choices=["ignore", "empty", "one-line-linux", "one-line-windows", "one-line-mac"],
    )
    parser.add_argument(
        "--new-line-at-end-of-file",
        required=False,
        default="auto",
        type=str,
        choices=["auto", "keep", "remove", "linux", "windows", "mac"],
    )
    parser.add_argument(
        "--remove-trailing-whitespace",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--remove-trailing-empty-lines",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument("input_files", help="List of input files", nargs="+", default=[], type=str)
    parsed_arguments = parser.parse_args()

    for file_name in parsed_arguments.input_files:
        process_file(file_name, parsed_arguments)


if __name__ == "__main__":
    main()
