"""Unit tests for the whitespace_format module."""

import argparse
import re
import unittest
from typing import Optional

import whitespace_format
from whitespace_format import Change
from whitespace_format import ChangeType
from whitespace_format import find_most_common_new_line_marker


def extract_version_from_pyproject() -> Optional[str]:
    """Extracts the version from the pyproject.toml file."""
    with open("pyproject.toml", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        match = re.match(r"^version\s+=\s+\"(.*)\"$", line)
        if match:
            return match.group(1)

    return None


class TestWhitespaceFormat(unittest.TestCase):
    """Unit tests for the whitespace_format module."""

    def test_check_version(self) -> None:
        """Verify that version numbers are the same in all places."""
        self.assertEqual(whitespace_format.VERSION, extract_version_from_pyproject())

    def test_escape_chars(self) -> None:
        """Tests escape_chars() function."""
        self.assertEqual(whitespace_format.escape_chars(""), "")
        self.assertEqual(whitespace_format.escape_chars("hello world"), "hello world")
        self.assertEqual(whitespace_format.escape_chars("\r"), "\\r")
        self.assertEqual(whitespace_format.escape_chars("\n"), "\\n")
        self.assertEqual(whitespace_format.escape_chars("\t"), "\\t")
        self.assertEqual(whitespace_format.escape_chars("\v"), "\\v")
        self.assertEqual(whitespace_format.escape_chars("\f"), "\\f")

    def test_read_file_content_windows(self) -> None:
        """Tests read_file_content() function."""
        file_content = whitespace_format.read_file_content(
            "test_data/windows-end-of-line-markers.txt",
            "utf-8",
        )
        self.assertEqual(file_content, file_content.strip() + "\r\n")

    def test_read_file_content_linux(self) -> None:
        """Tests read_file_content() function."""
        file_content = whitespace_format.read_file_content(
            "test_data/linux-end-of-line-markers.txt",
            "utf-8",
        )
        self.assertEqual(file_content, file_content.strip() + "\n")

    def test_read_file_content_mac(self) -> None:
        """Tests read_file_content() function."""
        file_content = whitespace_format.read_file_content(
            "test_data/mac-end-of-line-markers.txt",
            "utf-8",
        )
        self.assertEqual(file_content, file_content.strip() + "\r")

    def test_find_all_files_recursively(self) -> None:
        """Tests find_all_files_recursively() function."""
        self.assertEqual(
            [
                ".github/workflows/build.yaml",
                ".github/workflows/publish-to-pypi.yaml",
                ".github/workflows/publish-to-test-pypi.yaml",
            ],
            whitespace_format.find_all_files_recursively(".github", False),
        )
        self.assertEqual(
            [
                ".github/workflows/build.yaml",
                ".github/workflows/publish-to-pypi.yaml",
                ".github/workflows/publish-to-test-pypi.yaml",
            ],
            whitespace_format.find_all_files_recursively(".github/", True),
        )
        self.assertEqual(
            [
                ".github/../test_data/linux-end-of-line-markers.txt",
                ".github/../test_data/mac-end-of-line-markers.txt",
                ".github/../test_data/windows-end-of-line-markers.txt",
            ],
            whitespace_format.find_all_files_recursively(".github/../test_data/", True),
        )

    def test_is_whitespace_only(self) -> None:
        """Tests is_whitespace_only() function."""
        self.assertTrue(whitespace_format.is_whitespace_only(""))
        self.assertTrue(whitespace_format.is_whitespace_only("    "))
        self.assertTrue(whitespace_format.is_whitespace_only("\n\n\n"))
        self.assertTrue(whitespace_format.is_whitespace_only("\r\r\r"))
        self.assertTrue(whitespace_format.is_whitespace_only(" \t\n\r"))
        self.assertTrue(whitespace_format.is_whitespace_only("\t\v\f\n\r "))
        self.assertFalse(whitespace_format.is_whitespace_only("hello"))
        self.assertFalse(whitespace_format.is_whitespace_only("hello world\n"))

    def test_find_most_common_new_line_marker(self) -> None:
        """Tests find_most_common_new_line_marker() function."""
        self.assertEqual(find_most_common_new_line_marker(""), "\n")
        self.assertEqual(find_most_common_new_line_marker("\n"), "\n")
        self.assertEqual(find_most_common_new_line_marker("\r"), "\r")
        self.assertEqual(find_most_common_new_line_marker("\r\n"), "\r\n")
        self.assertEqual(find_most_common_new_line_marker("hello world"), "\n")
        self.assertEqual(find_most_common_new_line_marker("a\rb\nc\n"), "\n")
        self.assertEqual(find_most_common_new_line_marker("a\rb\rc\r\n"), "\r")
        self.assertEqual(find_most_common_new_line_marker("a\r\nb\r\nc\n"), "\r\n")
        self.assertEqual(find_most_common_new_line_marker("\n\n\r\r\r\n\r\n"), "\n")
        self.assertEqual(find_most_common_new_line_marker("\n\r\r\r\n\r\n"), "\r\n")
        self.assertEqual(find_most_common_new_line_marker("\n\r\r\r\n"), "\r")

    def test_format_file_content__do_nothing(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("hello\r\nworld\n", []),
            whitespace_format.format_file_content(
                "hello\r\nworld\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_empty_files__ignore(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("", []),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_empty_files__empty(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("", []),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="empty",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_empty_files__one_line__auto(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "\n",
                [Change(ChangeType.REPLACED_EMPTY_FILE_WITH_ONE_LINE, 1)],
            ),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="one-line",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_empty_files__one_line__linux(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "\n",
                [Change(ChangeType.REPLACED_EMPTY_FILE_WITH_ONE_LINE, 1)],
            ),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="linux",
                    normalize_empty_files="one-line",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_empty_files__one_line__windows(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "\r\n",
                [Change(ChangeType.REPLACED_EMPTY_FILE_WITH_ONE_LINE, 1)],
            ),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="windows",
                    normalize_empty_files="one-line",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_empty_files__one_line__mac(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "\r",
                [Change(ChangeType.REPLACED_EMPTY_FILE_WITH_ONE_LINE, 1)],
            ),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="mac",
                    normalize_empty_files="one-line",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__whitespace_only_file__ignore(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("   ", []),
            whitespace_format.format_file_content(
                "   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__whitespace_only_file__empty(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("", [Change(ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_EMPTY_FILE, 1)]),
            whitespace_format.format_file_content(
                "   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="empty",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__whitespace_only_file__one_line__auto(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("\n", [Change(ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_ONE_LINE, 1)]),
            whitespace_format.format_file_content(
                "   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="one-line",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__whitespace_only_file__one_line__linux(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("\n", [Change(ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_ONE_LINE, 1)]),
            whitespace_format.format_file_content(
                "   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="linux",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="one-line",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__whitespace_only_file__one_line__windows(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("\r\n", [Change(ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_ONE_LINE, 1)]),
            whitespace_format.format_file_content(
                "   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="windows",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="one-line",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__whitespace_only_file__one_line__mac(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("\r", [Change(ChangeType.REPLACED_WHITESPACE_ONLY_FILE_WITH_ONE_LINE, 1)]),
            whitespace_format.format_file_content(
                "   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="mac",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="one-line",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__add_new_line_marker__auto(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  \r\n",
                [Change(ChangeType.ADDED_NEW_LINE_MARKER_TO_END_OF_FILE, 3)],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=True,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__add_new_line_marker__linux(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  \n",
                [Change(ChangeType.ADDED_NEW_LINE_MARKER_TO_END_OF_FILE, 3)],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=True,
                    new_line_marker="linux",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__add_new_line_marker__windows(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  \r\n",
                [Change(ChangeType.ADDED_NEW_LINE_MARKER_TO_END_OF_FILE, 3)],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=True,
                    new_line_marker="windows",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__add_new_line_marker__mac(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  \r",
                [Change(ChangeType.ADDED_NEW_LINE_MARKER_TO_END_OF_FILE, 3)],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=True,
                    new_line_marker="mac",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker_from_end_of_file_1(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  ",
                [Change(ChangeType.REMOVED_NEW_LINE_MARKER_FROM_END_OF_FILE, 3)],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker_from_end_of_file_2(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  ",
                [
                    Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 4),
                    Change(ChangeType.REMOVED_NEW_LINE_MARKER_FROM_END_OF_FILE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \n\r\n\r",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker_from_end_of_file_3(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("", []),
            whitespace_format.format_file_content(
                "",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker_from_end_of_file_4(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("hello", []),
            whitespace_format.format_file_content(
                "hello",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker_from_end_of_file_5(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld  ",
                [
                    Change(ChangeType.REMOVED_NEW_LINE_MARKER_FROM_END_OF_FILE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \n\r\n\r",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_new_line_markers__auto(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\r\nworld  \r\n",
                [Change(ChangeType.REPLACED_NEW_LINE_MARKER, 2, "\r", "\r\n")],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \r\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=True,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_new_line_markers__linux(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\n\nworld  \n",
                [
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 1, "\r\n", "\n"),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 2, "\r", "\n"),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 3, "\r\n", "\n"),
                ],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \r\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="linux",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=True,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_new_line_markers__windows(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\r\nworld  \r\n",
                [Change(ChangeType.REPLACED_NEW_LINE_MARKER, 2, "\r", "\r\n")],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \r\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="windows",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=True,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__normalize_new_line_markers__mac(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\rworld  \r",
                [
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 1, "\r\n", "\r"),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 3, "\r\n", "\r"),
                ],
            ),
            whitespace_format.format_file_content(
                "hello\r\n\rworld  \r\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="mac",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=True,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_leading_empty_lines_1(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld\r\n\n\n\n\n\n",
                [
                    Change(ChangeType.REMOVED_LEADING_EMPTY_LINES, 1),
                ],
            ),
            whitespace_format.format_file_content(
                "\r\r\n\nhello\r\n\rworld\r\n\n\n\n\n\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=True,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_leading_empty_lines_2(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "   \r\n   \nhello\r\n\rworld\r\n\n\n\n\n\n",
                [Change(ChangeType.REMOVED_LEADING_EMPTY_LINES, 1)],
            ),
            whitespace_format.format_file_content(
                "\r   \r\n   \nhello\r\n\rworld\r\n\n\n\n\n\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=True,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_leading_empty_lines__remove_trailing_whitespace(
        self,
    ) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld\r\n\n\n\n\n\n",
                [
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 2),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                    Change(ChangeType.REMOVED_LEADING_EMPTY_LINES, 1),
                ],
            ),
            whitespace_format.format_file_content(
                "\r   \r\n   \nhello\r\n\rworld\r\n\n\n\n\n\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=True,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_empty_lines_1(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("hello\r\n\rworld\r\n", [Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 4)]),
            whitespace_format.format_file_content(
                "hello\r\n\rworld\r\n\n\n\n\n\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_empty_lines_2(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello   \r\n\rworld   \r\n   \n",
                [Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 5)],
            ),
            whitespace_format.format_file_content(
                "hello   \r\n\rworld   \r\n   \n\n\n\r\n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_1(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("hello world", [Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1)]),
            whitespace_format.format_file_content(
                "hello world   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_2(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("hello\r\n\rworld", [Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3)]),
            whitespace_format.format_file_content(
                "hello\r\n\rworld   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_3(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello\r\n\rworld",
                [
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 2),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello \t  \r\n \t  \rworld   ",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_4(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello world\n\n\n",
                [
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello world   \n\n   \n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_5(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello world\n\n\n",
                [
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello world   \f  \n\n \v \n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_and_normalize_non_standard_whitespace_1(
        self,
    ) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello world\n\n\n",
                [
                    Change(ChangeType.REMOVED_NONSTANDARD_WHITESPACE, 1, "\f", ""),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REMOVED_NONSTANDARD_WHITESPACE, 3, "\v", ""),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello world   \f  \n\n \v \n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="remove",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_and_normalize_non_standard_whitespace_2(
        self,
    ) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello world\n\n\n",
                [
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 1, "\f", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 3, "\v", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "hello world   \f  \n\n \v \n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="replace",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_trailing_whitespace_and_remove_trailing_empty_lines(
        self,
    ) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello world\n",
                [
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                    Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 2),
                ],
            ),
            whitespace_format.format_file_content(
                "hello world   \n\n   \n",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__replace_tabs_with_spaces__ignore(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("\t", []),
            whitespace_format.format_file_content(
                "\t",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-47,
                ),
            ),
        )

    def test_format_file_content__replace_tabs_with_spaces__0(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("hello", [Change(ChangeType.REMOVED_TAB, 1)]),
            whitespace_format.format_file_content(
                "\thello",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=0,
                ),
            ),
        )

    def test_format_file_content__replace_tabs_with_spaces__3(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            ("   hello", [Change(ChangeType.REPLACED_TAB_WITH_SPACES, 1, "\t", "   ")]),
            whitespace_format.format_file_content(
                "\thello",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=False,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=3,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker_from_end_of_file__remove_trailing_empty_lines(
        self,
    ) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "hello   ",
                [
                    Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 2),
                    Change(ChangeType.REMOVED_NEW_LINE_MARKER_FROM_END_OF_FILE, 1),
                ],
            ),
            whitespace_format.format_file_content(
                "hello   \n\r\n\r",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=False,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__remove_new_line_marker__remove_trailing_empty_lines__remove_trailing_whitespace(
        self,
    ) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                " hello\r\n  world",
                [
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 2),
                    Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 3),
                    Change(ChangeType.REMOVED_NEW_LINE_MARKER_FROM_END_OF_FILE, 2),
                ],
            ),
            whitespace_format.format_file_content(
                " hello  \r\n  world \t  \n\r\n\r",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=False,
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                    normalize_new_line_markers=False,
                    normalize_non_standard_whitespace="ignore",
                    normalize_whitespace_only_files="ignore",
                    remove_new_line_marker_from_end_of_file=True,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__comprehensive__1(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                " hello\n world\n",
                [
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 1, "\v", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 1),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 1, "\r\n", "\n"),
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 2, "\f", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 2),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 3, "\r\n", "\n"),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 4, "\r", "\n"),
                    Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 3),
                ],
            ),
            whitespace_format.format_file_content(
                "\vhello  \r\n\fworld \t  \n\r\n\r",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=True,
                    new_line_marker="linux",
                    normalize_empty_files="empty",
                    normalize_new_line_markers=True,
                    normalize_non_standard_whitespace="replace",
                    normalize_whitespace_only_files="empty",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=False,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )

    def test_format_file_content__comprehensive__2(self) -> None:
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                " hello\n world\n",
                [
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 2, "\v", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 2),
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 3, "\v", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 3),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 3, "\r\n", "\n"),
                    Change(ChangeType.REPLACED_NONSTANDARD_WHITESPACE, 4, "\f", " "),
                    Change(ChangeType.REMOVED_TRAILING_WHITESPACE, 4),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 5, "\r\n", "\n"),
                    Change(ChangeType.REPLACED_NEW_LINE_MARKER, 6, "\r", "\n"),
                    Change(ChangeType.REMOVED_LEADING_EMPTY_LINES, 1),
                    Change(ChangeType.REMOVED_TRAILING_EMPTY_LINES, 5),
                ],
            ),
            whitespace_format.format_file_content(
                "\r\n\v\n\vhello  \r\n\fworld \t  \n\r\n\r",
                argparse.Namespace(
                    add_new_line_marker_at_end_of_file=True,
                    new_line_marker="linux",
                    normalize_empty_files="empty",
                    normalize_new_line_markers=True,
                    normalize_non_standard_whitespace="replace",
                    normalize_whitespace_only_files="empty",
                    remove_new_line_marker_from_end_of_file=False,
                    remove_leading_empty_lines=True,
                    remove_trailing_empty_lines=True,
                    remove_trailing_whitespace=True,
                    replace_tabs_with_spaces=-1,
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
