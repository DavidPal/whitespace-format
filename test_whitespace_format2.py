"""Unit tests for whitespace_format2 module."""

import re
import unittest

import whitespace_format2


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


if __name__ == "__main__":
    unittest.main()
