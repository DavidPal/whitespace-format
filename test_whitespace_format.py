"""Unit tests for whitespace_format module."""

import argparse
import re
import unittest

import whitespace_format


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
        self.assertEqual(whitespace_format.VERSION, extract_version_from_pyproject())

    def test_guess_new_line_marker(self):
        """Tests guess_new_line_marker() function."""

        # If no line ending is present, prefer Linux line ending "\n".
        self.assertEqual("\n", whitespace_format.guess_new_line_marker(""))
        self.assertEqual("\n", whitespace_format.guess_new_line_marker("hello"))

        # Single line ending.
        self.assertEqual("\n", whitespace_format.guess_new_line_marker("\n"))
        self.assertEqual("\r\n", whitespace_format.guess_new_line_marker("\r\n"))
        self.assertEqual("\r", whitespace_format.guess_new_line_marker("\r"))

        # Single line ending with some text.
        self.assertEqual("\n", whitespace_format.guess_new_line_marker("hello\n"))
        self.assertEqual("\r\n", whitespace_format.guess_new_line_marker("hello\r\n"))
        self.assertEqual("\r", whitespace_format.guess_new_line_marker("hello\r"))

        # Linux vs. Windows line endings.
        # White spaces between are *very* important.
        self.assertEqual("\n", whitespace_format.guess_new_line_marker("\r \n \r \n"))
        self.assertEqual("\r\n", whitespace_format.guess_new_line_marker("\r\n \r\n"))
        self.assertEqual("\r\n", whitespace_format.guess_new_line_marker("\r\n\r\n"))

        # Mac vs. Windows line endings.
        # White spaces between are *very* important.
        self.assertEqual("\r", whitespace_format.guess_new_line_marker("\r \r \n \r \n"))
        self.assertEqual("\r\n", whitespace_format.guess_new_line_marker("\r \r\n \r\n"))
        self.assertEqual("\r\n", whitespace_format.guess_new_line_marker("\r\r\n\r\n"))

    def test_is_whitespace_only(self):
        """Tests is_whitespace_only() function."""
        self.assertTrue(whitespace_format.is_whitespace_only(""))
        self.assertTrue(whitespace_format.is_whitespace_only("  "))
        self.assertTrue(whitespace_format.is_whitespace_only(" \t \v \f \n \r "))

        self.assertFalse(whitespace_format.is_whitespace_only("hello"))
        self.assertFalse(whitespace_format.is_whitespace_only("   hello   "))

    def test_remove_trailing_empty_lines(self):
        """Tests remove_trailing_empty_lines() function."""
        self.assertEqual("", whitespace_format.remove_trailing_empty_lines(""))
        self.assertEqual("hello", whitespace_format.remove_trailing_empty_lines("hello"))

        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n"))
        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\n"))
        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\n\n"))
        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\n\n\n"))

        self.assertEqual("hello\n", whitespace_format.remove_trailing_empty_lines("hello\n"))
        self.assertEqual("hello\n", whitespace_format.remove_trailing_empty_lines("hello\n\n"))
        self.assertEqual("hello\n", whitespace_format.remove_trailing_empty_lines("hello\n\n\n"))
        self.assertEqual("hello\n", whitespace_format.remove_trailing_empty_lines("hello\n\n\n\n"))

        self.assertEqual("\r", whitespace_format.remove_trailing_empty_lines("\r"))
        self.assertEqual("\r", whitespace_format.remove_trailing_empty_lines("\r\r"))
        self.assertEqual("\r", whitespace_format.remove_trailing_empty_lines("\r\r\r"))
        self.assertEqual("\r", whitespace_format.remove_trailing_empty_lines("\r\r\r\r"))

        self.assertEqual("hello\r", whitespace_format.remove_trailing_empty_lines("hello\r"))
        self.assertEqual("hello\r", whitespace_format.remove_trailing_empty_lines("hello\r\r"))
        self.assertEqual("hello\r", whitespace_format.remove_trailing_empty_lines("hello\r\r\r"))
        self.assertEqual("hello\r", whitespace_format.remove_trailing_empty_lines("hello\r\r\r\r"))

        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n"))
        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r\n"))
        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r\n\r\n"))
        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r\n\r\n\r\n"))

        self.assertEqual("hello\r\n", whitespace_format.remove_trailing_empty_lines("hello\r\n"))
        self.assertEqual(
            "hello\r\n", whitespace_format.remove_trailing_empty_lines("hello\r\n\r\n")
        )
        self.assertEqual(
            "hello\r\n", whitespace_format.remove_trailing_empty_lines("hello\r\n\r\n\r\n")
        )
        self.assertEqual(
            "hello\r\n", whitespace_format.remove_trailing_empty_lines("hello\r\n\r\n\r\n\r\n")
        )

        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\r"))
        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\r\r"))
        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\r\r\r"))
        self.assertEqual("\n", whitespace_format.remove_trailing_empty_lines("\n\r\r\r\r"))

        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r"))
        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r\r"))
        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r\r\r"))
        self.assertEqual("\r\n", whitespace_format.remove_trailing_empty_lines("\r\n\r\r\r\r"))

    def test_remove_trailing_whitespace(self):
        """Tests remove_trailing_empty_lines() function."""
        self.assertEqual("", whitespace_format.remove_trailing_whitespace(""))
        self.assertEqual("", whitespace_format.remove_trailing_whitespace("    "))
        self.assertEqual("", whitespace_format.remove_trailing_whitespace(" \t \v \f "))

        self.assertEqual(
            "\t\v\f hello\n", whitespace_format.remove_trailing_whitespace("\t\v\f hello  \n")
        )
        self.assertEqual(
            "\t\v\f hello\r", whitespace_format.remove_trailing_whitespace("\t\v\f hello  \r")
        )
        self.assertEqual(
            "\t\v\f hello\r\n", whitespace_format.remove_trailing_whitespace("\t\v\f hello  \r\n")
        )

        self.assertEqual(
            "\t\v\f hello\n",
            whitespace_format.remove_trailing_whitespace("\t\v\f hello  \n \t\v\f "),
        )
        self.assertEqual(
            "\t\v\f hello\r",
            whitespace_format.remove_trailing_whitespace("\t\v\f hello  \r  \t\v\f "),
        )
        self.assertEqual(
            "\t\v\f hello\r\n",
            whitespace_format.remove_trailing_whitespace("\t\v\f hello  \r\n \t\v\f "),
        )

        self.assertEqual(
            " line1\n  line2", whitespace_format.remove_trailing_whitespace(" line1  \n  line2    ")
        )
        self.assertEqual(
            " line1\r  line2", whitespace_format.remove_trailing_whitespace(" line1  \r  line2    ")
        )
        self.assertEqual(
            " line1\r\n  line2",
            whitespace_format.remove_trailing_whitespace(" line1  \r\n  line2    "),
        )

        self.assertEqual(
            " line1\n  line2\n",
            whitespace_format.remove_trailing_whitespace(" line1  \n  line2  \n"),
        )
        self.assertEqual(
            " line1\r  line2\r",
            whitespace_format.remove_trailing_whitespace(" line1  \r  line2  \r"),
        )
        self.assertEqual(
            " line1\r\n  line2\r\n",
            whitespace_format.remove_trailing_whitespace(" line1  \r\n  line2   \r\n"),
        )

        self.assertEqual(
            " line1\n  line2\r",
            whitespace_format.remove_trailing_whitespace(" line1  \n  line2  \r"),
        )
        self.assertEqual(
            " line1\r  line2\n",
            whitespace_format.remove_trailing_whitespace(" line1  \r  line2  \n"),
        )

    def test_remove_all_new_line_marker_from_end_of_file(self):
        """Tests remove_all_new_line_marker_from_end_of_file() function."""
        self.assertEqual("", whitespace_format.remove_all_new_line_marker_from_end_of_file(""))
        self.assertEqual("  ", whitespace_format.remove_all_new_line_marker_from_end_of_file("  "))
        self.assertEqual(
            "\nhello", whitespace_format.remove_all_new_line_marker_from_end_of_file("\nhello\n\n")
        )
        self.assertEqual("", whitespace_format.remove_all_new_line_marker_from_end_of_file("\n"))
        self.assertEqual(
            "", whitespace_format.remove_all_new_line_marker_from_end_of_file("\n\n\n\n")
        )
        self.assertEqual(
            "", whitespace_format.remove_all_new_line_marker_from_end_of_file("\n\n\r\r")
        )
        self.assertEqual(
            "", whitespace_format.remove_all_new_line_marker_from_end_of_file("\r\r\n\n")
        )
        self.assertEqual(
            "", whitespace_format.remove_all_new_line_marker_from_end_of_file("\n\n\n\n")
        )

    def test_remove_new_line_marker_from_end_of_file(self):
        """Tests remove_new_line_marker_from_end_of_file() function."""
        self.assertEqual("", whitespace_format.remove_new_line_marker_from_end_of_file(""))
        self.assertEqual(
            "hello", whitespace_format.remove_new_line_marker_from_end_of_file("hello")
        )
        self.assertEqual(
            "hello", whitespace_format.remove_new_line_marker_from_end_of_file("hello\n")
        )
        self.assertEqual(
            "hello", whitespace_format.remove_new_line_marker_from_end_of_file("hello\r")
        )
        self.assertEqual(
            "hello", whitespace_format.remove_new_line_marker_from_end_of_file("hello\r\n")
        )
        self.assertEqual(
            "hello\n", whitespace_format.remove_new_line_marker_from_end_of_file("hello\n\r")
        )
        self.assertEqual(" ", whitespace_format.remove_new_line_marker_from_end_of_file(" \n"))
        self.assertEqual(" ", whitespace_format.remove_new_line_marker_from_end_of_file(" \r"))
        self.assertEqual(" ", whitespace_format.remove_new_line_marker_from_end_of_file(" \r\n"))
        self.assertEqual(" \n", whitespace_format.remove_new_line_marker_from_end_of_file(" \n\r"))

    def test_normalize_empty_file(self):
        """Tests normalize_empty_file() function."""
        self.assertEqual("", whitespace_format.normalize_empty_file("", "ignore", "\n"))
        self.assertEqual("", whitespace_format.normalize_empty_file("", "empty", "\n"))
        self.assertEqual("\n", whitespace_format.normalize_empty_file("", "one-line", "\n"))
        self.assertEqual("\r", whitespace_format.normalize_empty_file("", "one-line", "\r"))
        self.assertEqual("\r\n", whitespace_format.normalize_empty_file("", "one-line", "\r\n"))

        self.assertEqual(" \t ", whitespace_format.normalize_empty_file(" \t ", "ignore", "\n"))
        self.assertEqual("", whitespace_format.normalize_empty_file(" \t ", "empty", "\n"))
        self.assertEqual("\n", whitespace_format.normalize_empty_file(" \t ", "one-line", "\n"))
        self.assertEqual("\r", whitespace_format.normalize_empty_file(" \t ", "one-line", "\r"))
        self.assertEqual("\r\n", whitespace_format.normalize_empty_file(" \t ", "one-line", "\r\n"))

    def test_add_new_line_marker_at_end_of_file(self):
        """Tests add_new_line_marker_at_end_of_file() function."""
        self.assertEqual("\n", whitespace_format.add_new_line_marker_at_end_of_file("", "\n"))
        self.assertEqual("  \n", whitespace_format.add_new_line_marker_at_end_of_file("  ", "\n"))
        self.assertEqual(
            "hello\n",
            whitespace_format.add_new_line_marker_at_end_of_file("hello", "\n"),
        )

        self.assertEqual("\n", whitespace_format.add_new_line_marker_at_end_of_file("\n", "\n"))
        self.assertEqual(
            "\n\n\n", whitespace_format.add_new_line_marker_at_end_of_file("\n\n\n", "\n")
        )
        self.assertEqual(
            "\r\n", whitespace_format.add_new_line_marker_at_end_of_file("\r\r\n", "\n")
        )
        self.assertEqual("  \n", whitespace_format.add_new_line_marker_at_end_of_file("  \n", "\n"))
        self.assertEqual(
            "hello\n",
            whitespace_format.add_new_line_marker_at_end_of_file("hello\n", "\n"),
        )

        self.assertEqual("\r", whitespace_format.add_new_line_marker_at_end_of_file("\n", "\r"))
        self.assertEqual(
            "\n\n\r", whitespace_format.add_new_line_marker_at_end_of_file("\n\n\n", "\r")
        )
        self.assertEqual(
            "\r\r", whitespace_format.add_new_line_marker_at_end_of_file("\r\r\n", "\r")
        )
        self.assertEqual("  \r", whitespace_format.add_new_line_marker_at_end_of_file("  \n", "\r"))
        self.assertEqual(
            "hello\r",
            whitespace_format.add_new_line_marker_at_end_of_file("hello\n", "\r"),
        )

        self.assertEqual("\r", whitespace_format.add_new_line_marker_at_end_of_file("\r\n", "\r"))
        self.assertEqual(
            "  \r", whitespace_format.add_new_line_marker_at_end_of_file("  \r\n", "\r")
        )
        self.assertEqual(
            "hello\r",
            whitespace_format.add_new_line_marker_at_end_of_file("hello\r\n", "\r"),
        )

    def test_normalize_new_line_markers(self):
        """Tests normalize_new_line_markers() function."""
        self.assertEqual("", whitespace_format.normalize_new_line_markers("", "\n"))
        self.assertEqual("  ", whitespace_format.normalize_new_line_markers("  ", "\n"))
        self.assertEqual("\n\n\n\n", whitespace_format.normalize_new_line_markers("\n\n\r\r", "\n"))
        self.assertEqual(
            "hello\nworld\n",
            whitespace_format.normalize_new_line_markers("hello\nworld\r", "\n"),
        )
        self.assertEqual(
            "\n\n\n\n\n\n",
            whitespace_format.normalize_new_line_markers("\r\r\r\n\r\n\n\n", "\n"),
        )

        self.assertEqual("", whitespace_format.normalize_new_line_markers("", "\r"))
        self.assertEqual("  ", whitespace_format.normalize_new_line_markers("  ", "\r"))
        self.assertEqual("\r\r\r\r", whitespace_format.normalize_new_line_markers("\n\n\r\r", "\r"))
        self.assertEqual(
            "hello\rworld\r",
            whitespace_format.normalize_new_line_markers("hello\nworld\r", "\r"),
        )
        self.assertEqual(
            "\r\r\r\r\r\r",
            whitespace_format.normalize_new_line_markers("\r\r\r\n\r\n\n\n", "\r"),
        )

        self.assertEqual("", whitespace_format.normalize_new_line_markers("", "\r\n"))
        self.assertEqual("  ", whitespace_format.normalize_new_line_markers("  ", "\r\n"))
        self.assertEqual(
            "\r\n\r\n\r\n\r\n",
            whitespace_format.normalize_new_line_markers("\n\n\r\r", "\r\n"),
        )
        self.assertEqual(
            "hello\r\nworld\r\n",
            whitespace_format.normalize_new_line_markers("hello\nworld\r", "\r\n"),
        )
        self.assertEqual(
            "\r\n\r\n\r\n\r\n\r\n\r\n",
            whitespace_format.normalize_new_line_markers("\r\r\r\n\r\n\n\n", "\r\n"),
        )

    def test_normalize_non_standard_whitespace(self):
        """Tests remove_non_standard_whitespace() function."""
        self.assertEqual("", whitespace_format.normalize_non_standard_whitespace("", "ignore"))
        self.assertEqual("  ", whitespace_format.normalize_non_standard_whitespace("  ", "ignore"))
        self.assertEqual(
            "hello", whitespace_format.normalize_non_standard_whitespace("hello", "ignore")
        )
        self.assertEqual(
            "\v\f\t  \n",
            whitespace_format.normalize_non_standard_whitespace("\v\f\t  \n", "ignore"),
        )

        self.assertEqual("", whitespace_format.normalize_non_standard_whitespace("", "remove"))
        self.assertEqual("  ", whitespace_format.normalize_non_standard_whitespace("  ", "remove"))
        self.assertEqual(
            "hello", whitespace_format.normalize_non_standard_whitespace("hello", "remove")
        )
        self.assertEqual(
            "\t  \n", whitespace_format.normalize_non_standard_whitespace("\v\f\t  \n", "remove")
        )

        self.assertEqual("", whitespace_format.normalize_non_standard_whitespace("", "replace"))
        self.assertEqual("  ", whitespace_format.normalize_non_standard_whitespace("  ", "replace"))
        self.assertEqual(
            "hello", whitespace_format.normalize_non_standard_whitespace("hello", "replace")
        )
        self.assertEqual(
            "  \t  \n", whitespace_format.normalize_non_standard_whitespace("\v\f\t  \n", "replace")
        )

    def test_find_all_files_recursively(self):
        """Tests find_all_files_recursively() function."""
        self.assertEqual(
            [".circleci/config.yml"],
            whitespace_format.find_all_files_recursively(".circleci", False),
        )
        self.assertEqual(
            [".circleci/config.yml"],
            whitespace_format.find_all_files_recursively(".circleci/", True),
        )

    def test_format_file_content_1(self):
        """Tests format_file_content() function."""
        file_content_tracker = whitespace_format.FileContentTracker("")
        whitespace_format.format_file_content(
            file_content_tracker,
            argparse.Namespace(
                new_line_marker="auto",
                normalize_empty_files="ignore",
            ),
        )
        self.assertEqual("", file_content_tracker.file_content)

    def test_format_file_content_2(self):
        """Tests format_file_content() function."""
        file_content_tracker = whitespace_format.FileContentTracker(" \n \n \r \r\n \r\n \t \v \f ")
        whitespace_format.format_file_content(
            file_content_tracker,
            argparse.Namespace(
                new_line_marker="auto",
                normalize_empty_files="ignore",
                normalize_whitespace_only_files="empty",
            ),
        )
        self.assertEqual("", file_content_tracker.file_content)

    def test_format_file_content_3(self):
        """Tests format_file_content() function."""
        file_content_tracker = whitespace_format.FileContentTracker("hello\r\nworld   ")
        whitespace_format.format_file_content(
            file_content_tracker,
            argparse.Namespace(
                new_line_marker="linux",
                add_new_line_marker_at_end_of_file=True,
                remove_trailing_whitespace=True,
                remove_trailing_empty_lines=True,
                replace_tabs_with_spaces=-1,
                normalize_non_standard_whitespace="ignore",
                normalize_new_line_markers=True,
            ),
        )
        self.assertEqual("hello\nworld\n", file_content_tracker.file_content)


if __name__ == "__main__":
    unittest.main()
