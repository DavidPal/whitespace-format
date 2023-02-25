#!/usr/bin/env python

"""Formatter of whitespace in text files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2023

Usage:

   whitespace_format.py [OPTIONS] [FILES ...]
"""

import argparse
import pathlib
import re
import sys
from typing import List

# Regular expression that does NOT match any string.
UNMATCHABLE_REGEX = "$."

NEW_LINE_MARKERS = {
    "linux": "\n",
    "windows": "\r\n",
    "mac": "\r",
}


def die(error_code: int, message: str = ""):
    """Exits the script."""
    if message:
        print(message)
    sys.exit(error_code)


def read_file_content(file_name: str) -> str:
    """Reads content of a file."""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
    except IOError as exception:
        die(2, f"Cannot read file '{file_name}': {exception}")
    except UnicodeError as exception:
        die(3, f"Cannot decode file '{file_name}': {exception}")
    return ""


def write_file(file_name: str, file_content: str):
    """Writes data to a file."""
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(file_content)
    except IOError as exception:
        die(4, f"Cannot write to file '{file_name}': {exception}")


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


def remove_new_line_marker_from_end_of_file(file_content: str) -> str:
    """Removes the last new line marker from the last line."""
    if file_content.endswith("\r\n"):
        return file_content[:-2]
    if file_content.endswith("\n") or file_content.endswith("\r"):
        return file_content[:-1]
    return file_content


def add_new_line_marker_at_end_of_file(file_content: str, new_line_marker: str) -> str:
    """Adds new line marker to the end of file if it is missing."""
    return remove_new_line_marker_from_end_of_file(file_content) + new_line_marker


def normalize_new_line_markers(file_content: str, new_line_marker: str) -> str:
    """Fixes line endings."""
    file_content = file_content.replace("\r\n", "\n")
    file_content = file_content.replace("\r", "\n")
    return file_content.replace("\n", new_line_marker)


def normalize_empty_file(file_content: str, mode: str, new_line_marker: str) -> str:
    """Replaces file with an empty file."""
    if mode == "empty":
        return ""
    if mode == "one-line":
        return new_line_marker
    return file_content


def is_whitespace_only(file_content: str) -> bool:
    """Determines if file consists only of whitespace."""
    return not file_content.strip(" \n\r\t\v\f")


def normalize_non_standard_whitespace(file_content: str, mode: str) -> str:
    """Removes non-standard whitespace characters."""
    if mode == "ignore":
        return file_content
    if mode == "replace":
        return file_content.translate(str.maketrans("\v\f", "  ", ""))
    return file_content.translate(str.maketrans("", "", "\v\f"))


def replace_tabs_with_spaces(file_content: str, num_spaces: int) -> str:
    """Replaces tabs with spaces."""
    if num_spaces < 0:
        return file_content
    return file_content.replace("\t", num_spaces * " ")


def format_file_content(file_content: str, parsed_arguments: argparse.Namespace) -> str:
    """Formats the content of file represented as a string."""
    new_line_marker = NEW_LINE_MARKERS.get(
        parsed_arguments.new_line_marker, guess_new_line_marker(file_content)
    )

    if is_whitespace_only(file_content):
        if not file_content:
            file_content = normalize_empty_file(
                file_content, parsed_arguments.normalize_empty_files, new_line_marker
            )
        file_content = normalize_empty_file(
            file_content, parsed_arguments.normalize_whitespace_only_files, new_line_marker
        )

    else:
        if parsed_arguments.remove_trailing_whitespace:
            file_content = remove_trailing_whitespace(file_content)

        if parsed_arguments.remove_trailing_empty_lines:
            file_content = remove_trailing_empty_lines(file_content)

        file_content = replace_tabs_with_spaces(
            file_content, parsed_arguments.replace_tabs_with_spaces
        )

        file_content = normalize_non_standard_whitespace(
            file_content, parsed_arguments.normalize_non_standard_whitespace
        )

        if parsed_arguments.normalize_new_line_markers:
            file_content = normalize_new_line_markers(file_content, new_line_marker)

        if parsed_arguments.add_new_line_marker_at_end_of_file:
            file_content = add_new_line_marker_at_end_of_file(file_content, new_line_marker)
        elif parsed_arguments.remove_new_line_marker_from_end_of_file:
            file_content = remove_new_line_marker_from_end_of_file(file_content)

    return file_content


def reformat_file(file_name: str, parsed_argument: argparse.Namespace) -> bool:
    """Reformats a file."""
    print(f"Processing file '{file_name}'...")
    file_content = read_file_content(file_name)
    formatted_file_content = format_file_content(file_content, parsed_argument)
    is_formatted = formatted_file_content != file_content
    if parsed_argument.check_only:
        if is_formatted:
            print(f"✘ would reformat '{file_name}'")
        else:
            print(f"✔ '{file_name}' would be left unchanged")
    else:
        if is_formatted:
            print(f"✘ reformatted '{file_name}'")
            write_file(file_name, formatted_file_content)
        else:
            print(f"✔ '{file_name}' left unchanged.")
    return is_formatted


def reformat_files(file_names: List[str], parsed_arguments: argparse.Namespace):
    """Reformats multiple files."""
    num_format_files = 0
    for file_name in file_names:
        is_formatted = reformat_file(file_name, parsed_arguments)
        if is_formatted:
            num_format_files += 1

    if parsed_arguments.check_only:
        if num_format_files:
            print(
                f"{num_format_files} files would be formatted, "
                f"{len(file_names) - num_format_files} file would be left unchanged."
            )
            die(1)
        else:
            print(f"{len(file_names)} file would be left unchanged.")
    else:
        if num_format_files:
            print(
                f"{num_format_files} formatted, "
                f"{len(file_names) - num_format_files} left unchanged."
            )
        else:
            print(f"{len(file_names)} left unchanged.")


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
        if not re.match(parsed_arguments.exclude, expanded_file_name)
    ]


def parse_command_line() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Formats whitespace in text files",
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--check-only",
        help="Do NOT format files. Only report which files would be formatted.",
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
            "Regular expression that specifies which files or directories to exclude. "
            "The matching is done on the path of the file. "
            "Example #1: --exclude='(.jpeg|.png)$' excludes files "
            "with '.jpeg' or '.png' extension. "
            "Example #2: --exclude='.git/' excludes all files in the git directory. "
        ),
        required=False,
        type=str,
        default=UNMATCHABLE_REGEX,
    )
    parser.add_argument(
        "--new-line-marker",
        help=(
            "Specifies what marker to use. "
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
            "Normalize '\\v' and '\\f' from each file. "
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
    return parser.parse_args()


def main():
    """Formats white space in text files."""
    parsed_arguments = parse_command_line()
    file_names = find_files_to_process(parsed_arguments.input_files, parsed_arguments)
    reformat_files(file_names, parsed_arguments)


if __name__ == "__main__":
    main()
