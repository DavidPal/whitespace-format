"""Unit tests for whitespace_format2 module."""

import argparse
import re
import unittest

import whitespace_format2
from whitespace_format2 import Change
from whitespace_format2 import ChangeType
from whitespace_format2 import find_most_common_new_line_marker


def extract_version_from_pyproject():
    """Extracts version from pyproject.toml file."""
    with open("pyproject.toml", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        match = re.match(r"^version\s+=\s+\"(.*)\"$", line)
        if match:
            return match.group(1)

    return None


class TestWhitespaceFormat(unittest.TestCase):
    """Unit tests for whitespace_format module."""

    def test_check_version(self):
        """Verify that version numbers are the same in all places."""
        self.assertEqual(whitespace_format2.VERSION, extract_version_from_pyproject())

    def test_read_file_content_windows(self):
        """Tests read_file_content() function."""
        file_content = whitespace_format2.read_file_content(
            "test_data/windows-end-of-line-markers.txt", "utf-8"
        )
        self.assertEqual(file_content, file_content.strip() + "\r\n")

    def test_read_file_content_linux(self):
        """Tests read_file_content() function."""
        file_content = whitespace_format2.read_file_content(
            "test_data/linux-end-of-line-markers.txt", "utf-8"
        )
        self.assertEqual(file_content, file_content.strip() + "\n")

    def test_read_file_content_mac(self):
        """Tests read_file_content() function."""
        file_content = whitespace_format2.read_file_content(
            "test_data/mac-end-of-line-markers.txt", "utf-8"
        )
        self.assertEqual(file_content, file_content.strip() + "\r")

    def test_find_all_files_recursively(self):
        """Tests find_all_files_recursively() function."""
        self.assertEqual(
            [".circleci/config.yml"],
            whitespace_format2.find_all_files_recursively(".circleci", False),
        )
        self.assertEqual(
            [".circleci/config.yml"],
            whitespace_format2.find_all_files_recursively(".circleci/", True),
        )

    def test_is_file_whitespace(self):
        """Tests is_file_whitespace() function."""
        self.assertTrue(whitespace_format2.is_file_whitespace(""))
        self.assertTrue(whitespace_format2.is_file_whitespace("    "))
        self.assertTrue(whitespace_format2.is_file_whitespace("\n\n\n"))
        self.assertTrue(whitespace_format2.is_file_whitespace("\r\r\r"))
        self.assertTrue(whitespace_format2.is_file_whitespace(" \t\n\r"))
        self.assertTrue(whitespace_format2.is_file_whitespace("\t\v\f\n\r "))
        self.assertFalse(whitespace_format2.is_file_whitespace("hello"))
        self.assertFalse(whitespace_format2.is_file_whitespace("hello world\n"))

    def test_find_most_common_new_line_marker(self):
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

    def test_format_file_content__empty_file__ignore(self):
        """Tests format_file_content() function."""
        self.assertEqual(
            ("", []),
            whitespace_format2.format_file_content(
                "",
                argparse.Namespace(
                    new_line_marker="auto",
                    normalize_empty_files="ignore",
                ),
            ),
        )

    def test_format_file_content__empty_file__empty(self):
        """Tests format_file_content() function."""
        self.assertEqual(
            ("", []),
            whitespace_format2.format_file_content(
                "",
                argparse.Namespace(
                    new_line_marker="auto",
                    normalize_empty_files="empty",
                ),
            ),
        )

    def test_format_file_content__empty_file_one__line(self):
        """Tests format_file_content() function."""
        self.assertEqual(
            (
                "\r",
                [
                    Change(
                        ChangeType.REPLACED_EMPTY_FILE_WITH_ONE_LINE,
                        1,
                        changed_from=None,
                        changed_to=None,
                    )
                ],
            ),
            whitespace_format2.format_file_content(
                "",
                argparse.Namespace(
                    new_line_marker="mac",
                    normalize_empty_files="one-line",
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
