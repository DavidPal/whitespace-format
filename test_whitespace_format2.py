"""Unit tests for whitespace_format2 module."""

import argparse
import re
import unittest

import whitespace_format2
from whitespace_format2 import Line


def extract_version_from_pyproject():
    """Extracts version from pyproject.toml file."""
    with open("pyproject.toml", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        match = re.match(r"^version\s+=\s+\"(.*)\"$", line)
        if match:
            return match.group(1)

    return None


class TestLine(unittest.TestCase):
    """Unit tests for Line class."""

    def test_line_equality(self):
        """Tests equality of Lines."""
        self.assertEqual(
            Line("hello world", "\n"),
            Line("hello world", "\n"),
        )
        self.assertNotEqual(Line("hello", "\n"), Line("hello world", "\n"))
        self.assertNotEqual(
            Line("hello world", "\r"),
            Line("hello world", "\n"),
        )
        self.assertTrue(Line("hello world", "\n") == Line("hello world", "\n"))
        self.assertFalse(Line("hello world", "\n") == Line("hello", "\n"))
        self.assertFalse(Line("hello world", "\r") == Line("hello world", "\n"))

    def test_create_from_string(self):
        """Tests Line.create_from_string() function."""
        self.assertEqual(Line("", ""), Line.create_from_string(""))
        self.assertEqual(Line("", "\n"), Line.create_from_string("\n"))
        self.assertEqual(Line("", "\r"), Line.create_from_string("\r"))
        self.assertEqual(Line("", "\r\n"), Line.create_from_string("\r\n"))
        self.assertEqual(
            Line("hello world", "\n"),
            Line.create_from_string("hello world\n"),
        )
        self.assertEqual(
            Line("hello world", "\r"),
            Line.create_from_string("hello world\r"),
        )
        self.assertEqual(
            Line("hello world", "\r\n"),
            Line.create_from_string("hello world\r\n"),
        )

    def test_split_lines(self):
        """Tests split_lines() function."""
        self.assertListEqual([], whitespace_format2.split_lines(""))
        self.assertListEqual([Line("", "\n")], whitespace_format2.split_lines("\n"))
        self.assertListEqual([Line("", "\r")], whitespace_format2.split_lines("\r"))
        self.assertListEqual([Line("", "\r\n")], whitespace_format2.split_lines("\r\n"))
        self.assertListEqual(
            [Line("hello world", "")],
            whitespace_format2.split_lines("hello world"),
        )
        self.assertListEqual(
            [Line("line1", "\n"), Line("line2", "")],
            whitespace_format2.split_lines("line1\nline2"),
        )
        self.assertListEqual(
            [Line("line1", "\n"), Line("line2", "\n")],
            whitespace_format2.split_lines("line1\nline2\n"),
        )
        self.assertListEqual(
            [Line("line1", "\r"), Line("line2", "\n")],
            whitespace_format2.split_lines("line1\rline2\n"),
        )
        self.assertListEqual(
            [Line("line1", "\r\n"), Line("line2", "\n")],
            whitespace_format2.split_lines("line1\r\nline2\n"),
        )
        self.assertListEqual(
            [
                Line("line1", "\r\n"),
                Line("", "\n"),
                Line("line3", "\r"),
            ],
            whitespace_format2.split_lines("line1\r\n\nline3\r"),
        )

    def test_concatenate_lines(self):
        """Tests concatenate_lines() function."""
        self.assertEqual("", whitespace_format2.concatenate_lines([]))
        self.assertEqual("", whitespace_format2.concatenate_lines([Line("", "")]))
        self.assertEqual(
            "hello world",
            whitespace_format2.concatenate_lines([Line("hello world", "")]),
        )
        self.assertEqual(
            "hello world\n",
            whitespace_format2.concatenate_lines([Line("hello world", "\n")]),
        )
        self.assertEqual(
            "hello world\r\n",
            whitespace_format2.concatenate_lines([Line("hello world", "\r\n")]),
        )
        self.assertEqual(
            "line1\r\nline2\n",
            whitespace_format2.concatenate_lines([Line("line1", "\r\n"), Line("line2", "\n")]),
        )


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

    def test_guess_new_end_of_line_marker(self):
        """Tests guess_new_end_of_line_marker() function."""

        # If no line ending is present, prefer Linux line ending "\n".
        self.assertEqual("\n", whitespace_format2.guess_end_of_line_marker([]))
        self.assertEqual("\n", whitespace_format2.guess_end_of_line_marker([Line("hello", "")]))

        # Single line ending.
        self.assertEqual("\n", whitespace_format2.guess_end_of_line_marker([Line("", "\n")]))
        self.assertEqual("\r\n", whitespace_format2.guess_end_of_line_marker([Line("", "\r\n")]))
        self.assertEqual("\r", whitespace_format2.guess_end_of_line_marker([Line("", "\r")]))

        # Single line ending with some text.
        self.assertEqual("\n", whitespace_format2.guess_end_of_line_marker([Line("hello", "\n")]))
        self.assertEqual(
            "\r\n", whitespace_format2.guess_end_of_line_marker([Line("hello", "\r\n")])
        )
        self.assertEqual("\r", whitespace_format2.guess_end_of_line_marker([Line("hello", "\r")]))

        # Linux vs. Windows line endings.
        # White spaces between are *very* important.
        self.assertEqual(
            "\n",
            whitespace_format2.guess_end_of_line_marker(
                [Line("", "\r"), Line("", "\n"), Line("", "\r"), Line("", "\n")]
            ),
        )
        self.assertEqual(
            "\r\n",
            whitespace_format2.guess_end_of_line_marker([Line("", "\r\n"), Line("", "\r\n")]),
        )
        self.assertEqual(
            "\r\n",
            whitespace_format2.guess_end_of_line_marker([Line("", "\r\n"), Line("", "\r\n")]),
        )

        # Mac vs. Windows line endings.
        # White spaces between are *very* important.
        self.assertEqual(
            "\r",
            whitespace_format2.guess_end_of_line_marker(
                [Line("", "\r"), Line("", "\r"), Line("", "\n"), Line("", "\r"), Line("", "\n")]
            ),
        )
        self.assertEqual(
            "\r\n",
            whitespace_format2.guess_end_of_line_marker(
                [Line("", "\r"), Line("", "\r\n"), Line("", "\r\n")]
            ),
        )
        self.assertEqual(
            "\r\n",
            whitespace_format2.guess_end_of_line_marker(
                [Line("", "\r"), Line("", "\r\n"), Line("", "\r\n")]
            ),
        )

    def test_is_whitespace_only(self):
        """Tests is_whitespace_only() function."""
        self.assertTrue(whitespace_format2.is_whitespace_only([]))
        self.assertTrue(whitespace_format2.is_whitespace_only([Line("  ", "")]))
        self.assertTrue(
            whitespace_format2.is_whitespace_only([Line(" \t \v \f ", "\n"), Line(" ", "\r")])
        )

        self.assertFalse(whitespace_format2.is_whitespace_only([Line("hello", "")]))
        self.assertFalse(whitespace_format2.is_whitespace_only([Line("   hello   ", "")]))

    def test_remove_trailing_empty_lines(self):
        """Tests remove_trailing_empty_lines() function."""
        self.assertListEqual([], whitespace_format2.remove_trailing_empty_lines([]))
        self.assertListEqual(
            [Line("hello", "")], whitespace_format2.remove_trailing_empty_lines([Line("hello", "")])
        )

        self.assertListEqual(
            [Line("", "\n")], whitespace_format2.remove_trailing_empty_lines([Line("", "\n")])
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("", "\n"), Line("", "\n")]),
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\n"), Line("", "\n"), Line("", "\n")]
            ),
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\n"), Line("", "\n"), Line("", "\n"), Line("", "\n")]
            ),
        )

        self.assertListEqual(
            [Line("hello", "\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("hello", "\n")]),
        )
        self.assertListEqual(
            [Line("hello", "\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("hello", "\n"), Line("", "\n")]),
        )
        self.assertListEqual(
            [Line("hello", "\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("hello", "\n"), Line("", "\n"), Line("", "\n")]
            ),
        )

        self.assertListEqual(
            [Line("", "\r")], whitespace_format2.remove_trailing_empty_lines([Line("", "\r")])
        )
        self.assertListEqual(
            [Line("", "\r")],
            whitespace_format2.remove_trailing_empty_lines([Line("", "\r"), Line("", "\r")]),
        )
        self.assertListEqual(
            [Line("", "\r")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )
        self.assertListEqual(
            [Line("", "\r")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r"), Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )

        self.assertListEqual(
            [Line("hello", "\r")],
            whitespace_format2.remove_trailing_empty_lines([Line("hello", "\r")]),
        )
        self.assertListEqual(
            [Line("hello", "\r")],
            whitespace_format2.remove_trailing_empty_lines([Line("hello", "\r"), Line("", "\r")]),
        )
        self.assertListEqual(
            [Line("hello", "\r")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("hello", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )

        self.assertListEqual(
            [Line("", "\r\n")], whitespace_format2.remove_trailing_empty_lines([Line("", "\r\n")])
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("", "\r\n"), Line("", "\r\n")]),
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r\n"), Line("", "\r\n"), Line("", "\r\n")]
            ),
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r\n"), Line("", "\r\n"), Line("", "\r\n"), Line("", "\r\n")]
            ),
        )

        self.assertListEqual(
            [Line("hello", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("hello", "\r\n")]),
        )
        self.assertListEqual(
            [Line("hello", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("hello", "\r\n"), Line("", "\r\n")]
            ),
        )
        self.assertListEqual(
            [Line("hello", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("hello", "\r\n"), Line("", "\r\n"), Line("", "\r\n")]
            ),
        )

        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("", "\n"), Line("", "\r")]),
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\n"), Line("", "\r"), Line("", "\r")]
            ),
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\n"), Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\n"), Line("", "\r"), Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )

        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines([Line("", "\r\n"), Line("", "\r")]),
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r\n"), Line("", "\r"), Line("", "\r")]
            ),
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r\n"), Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.remove_trailing_empty_lines(
                [Line("", "\r\n"), Line("", "\r"), Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )

    def test_remove_trailing_whitespace(self):
        """Tests remove_trailing_empty_lines() function."""
        self.assertListEqual([], whitespace_format2.remove_trailing_whitespace([]))
        self.assertListEqual([], whitespace_format2.remove_trailing_whitespace([Line("    ", "")]))
        self.assertListEqual(
            [], whitespace_format2.remove_trailing_whitespace([Line(" \t \v \f ", "")])
        )

        self.assertListEqual(
            [Line("\t\v\f hello", "\n")],
            whitespace_format2.remove_trailing_whitespace([Line("\t\v\f hello  ", "\n")]),
        )
        self.assertListEqual(
            [Line("\t\v\f hello", "\r")],
            whitespace_format2.remove_trailing_whitespace([Line("\t\v\f hello  ", "\r")]),
        )
        self.assertListEqual(
            [Line("\t\v\f hello", "\r\n")],
            whitespace_format2.remove_trailing_whitespace([Line("\t\v\f hello  ", "\r\n")]),
        )

        self.assertListEqual(
            [Line("\t\v\f hello", "\n")],
            whitespace_format2.remove_trailing_whitespace(
                [Line("\t\v\f hello  ", "\n"), Line(" \t\v\f ", "")]
            ),
        )
        self.assertListEqual(
            [Line("\t\v\f hello", "\r")],
            whitespace_format2.remove_trailing_whitespace(
                [Line("\t\v\f hello  ", "\r"), Line(" \t\v\f ", "")]
            ),
        )
        self.assertListEqual(
            [Line("\t\v\f hello", "\r\n")],
            whitespace_format2.remove_trailing_whitespace(
                [Line("\t\v\f hello  ", "\r\n"), Line(" \t\v\f ", "")]
            ),
        )

        self.assertListEqual(
            [Line(" line1", "\n"), Line("  line2", "")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\n"), Line("  line2    ", "")]
            ),
        )
        self.assertListEqual(
            [Line(" line1", "\r"), Line("  line2", "")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\r"), Line("  line2    ", "")]
            ),
        )
        self.assertListEqual(
            [Line(" line1", "\r\n"), Line("  line2", "")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\r\n"), Line("  line2    ", "")]
            ),
        )

        self.assertListEqual(
            [Line(" line1", "\n"), Line("  line2", "\n")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\n"), Line("  line2  ", "\n")]
            ),
        )
        self.assertListEqual(
            [Line(" line1", "\r"), Line("  line2", "\r")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\r"), Line("  line2  ", "\r")]
            ),
        )
        self.assertListEqual(
            [Line(" line1", "\r\n"), Line("  line2", "\r\n")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\r\n"), Line("  line2  ", "\r\n")]
            ),
        )

        self.assertListEqual(
            [Line(" line1", "\n"), Line("  line2", "\r")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\n"), Line("  line2  ", "\r")]
            ),
        )
        self.assertListEqual(
            [Line(" line1", "\r"), Line("  line2", "\n")],
            whitespace_format2.remove_trailing_whitespace(
                [Line(" line1  ", "\r"), Line("  line2  ", "\n")]
            ),
        )

    def test_remove_all_new_line_marker_from_end_of_file(self):
        """Tests remove_all_new_line_marker_from_end_of_file() function."""
        self.assertListEqual(
            [], whitespace_format2.remove_all_end_of_line_markers_from_end_of_file([])
        )
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.remove_all_end_of_line_markers_from_end_of_file([Line("  ", "")]),
        )
        self.assertListEqual(
            [Line("", "\n"), Line("hello", "")],
            whitespace_format2.remove_all_end_of_line_markers_from_end_of_file(
                [Line("", "\n"), Line("hello", "\n"), Line("", "\n")]
            ),
        )
        self.assertListEqual(
            [], whitespace_format2.remove_all_end_of_line_markers_from_end_of_file([Line("", "\n")])
        )
        self.assertListEqual(
            [],
            whitespace_format2.remove_all_end_of_line_markers_from_end_of_file(
                [Line("", "\n"), Line("", "\n"), Line("", "\n"), Line("", "\n")]
            ),
        )
        self.assertListEqual(
            [],
            whitespace_format2.remove_all_end_of_line_markers_from_end_of_file(
                [Line("", "\n"), Line("", "\n"), Line("", "\r"), Line("", "\r")]
            ),
        )
        self.assertListEqual(
            [],
            whitespace_format2.remove_all_end_of_line_markers_from_end_of_file(
                [Line("", "\r"), Line("", "\r\n"), Line("", "\n")]
            ),
        )
        self.assertListEqual(
            [],
            whitespace_format2.remove_all_end_of_line_markers_from_end_of_file(
                [Line("", "\r"), Line("", "\r"), Line("", "\r"), Line("", "\r")]
            ),
        )

    def test_normalize_empty_file(self):
        """Tests normalize_empty_file() function."""
        self.assertListEqual([], whitespace_format2.normalize_empty_file([], "ignore", "\n"))
        self.assertListEqual([], whitespace_format2.normalize_empty_file([], "empty", "\n"))
        self.assertListEqual(
            [Line("", "\n")], whitespace_format2.normalize_empty_file([], "one-line", "\n")
        )
        self.assertListEqual(
            [Line("", "\r")], whitespace_format2.normalize_empty_file([], "one-line", "\r")
        )
        self.assertListEqual(
            [Line("", "\r\n")], whitespace_format2.normalize_empty_file([], "one-line", "\r\n")
        )

        self.assertListEqual(
            [Line(" \t ", "")],
            whitespace_format2.normalize_empty_file([Line(" \t ", "")], "ignore", "\n"),
        )
        self.assertListEqual(
            [], whitespace_format2.normalize_empty_file([Line(" \t ", "")], "empty", "\n")
        )
        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.normalize_empty_file([Line(" \t ", "")], "one-line", "\n"),
        )
        self.assertListEqual(
            [Line("", "\r")],
            whitespace_format2.normalize_empty_file([Line(" \t ", "")], "one-line", "\r"),
        )
        self.assertListEqual(
            [Line("", "\r\n")],
            whitespace_format2.normalize_empty_file([Line(" \t ", "")], "one-line", "\r\n"),
        )

    def test_add_end_of_line_marker_at_end_of_file(self):
        """Tests add_end_of_line_marker_at_end_of_file() function."""
        self.assertListEqual(
            [Line("", "\n")], whitespace_format2.add_end_of_line_marker_at_end_of_file([], "\n")
        )
        self.assertListEqual(
            [Line("  ", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("  ", "")], "\n"),
        )
        self.assertListEqual(
            [Line("hello", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("hello", "")], "\n"),
        )

        self.assertListEqual(
            [Line("", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("", "\n")], "\n"),
        )
        self.assertListEqual(
            [Line("", "\n"), Line("", "\n"), Line("", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file(
                [Line("", "\n"), Line("", "\n"), Line("", "\n")], "\n"
            ),
        )
        self.assertListEqual(
            [Line("", "\r"), Line("", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file(
                [Line("", "\r"), Line("", "\r\n")], "\n"
            ),
        )
        self.assertListEqual(
            [Line("  ", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("  ", "\n")], "\n"),
        )
        self.assertListEqual(
            [Line("hello", "\n")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("hello", "\n")], "\n"),
        )

        self.assertListEqual(
            [Line("", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("", "\n")], "\r"),
        )
        self.assertListEqual(
            [Line("", "\n"), Line("", "\n"), Line("", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file(
                [Line("", "\n"), Line("", "\n"), Line("", "\n")], "\r"
            ),
        )
        self.assertListEqual(
            [Line("", "\r"), Line("", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file(
                [Line("", "\r"), Line("", "\r\n")], "\r"
            ),
        )
        self.assertListEqual(
            [Line("  ", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("  ", "\n")], "\r"),
        )
        self.assertListEqual(
            [Line("hello", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("hello", "\n")], "\r"),
        )

        self.assertListEqual(
            [Line("", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("", "\r\n")], "\r"),
        )
        self.assertListEqual(
            [Line("  ", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("  ", "\r\n")], "\r"),
        )
        self.assertListEqual(
            [Line("hello", "\r")],
            whitespace_format2.add_end_of_line_marker_at_end_of_file([Line("hello", "\r\n")], "\r"),
        )

    def test_normalize_end_of_line_markers(self):
        """Tests normalize_end_of_line_markers() function."""
        self.assertListEqual([], whitespace_format2.normalize_end_of_line_markers([], "\n"))
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.normalize_end_of_line_markers([Line("  ", "")], "\n"),
        )
        self.assertListEqual(
            [Line("", "\n"), Line("", "\n"), Line("", "\n"), Line("", "\n")],
            whitespace_format2.normalize_end_of_line_markers(
                [Line("", "\n"), Line("", "\n"), Line("", "\r"), Line("", "\r")], "\n"
            ),
        )
        self.assertListEqual(
            [Line("hello", "\n"), Line("world", "\n")],
            whitespace_format2.normalize_end_of_line_markers(
                [Line("hello", "\n"), Line("world", "\r")], "\n"
            ),
        )
        self.assertListEqual(
            [
                Line("", "\n"),
                Line("", "\n"),
                Line("", "\n"),
                Line("", "\n"),
                Line("", "\n"),
                Line("", "\n"),
            ],
            whitespace_format2.normalize_end_of_line_markers(
                [
                    Line("", "\r"),
                    Line("", "\r"),
                    Line("", "\r\n"),
                    Line("", "\r\n"),
                    Line("", "\n"),
                    Line("", "\n"),
                ],
                "\n",
            ),
        )

        self.assertListEqual([], whitespace_format2.normalize_end_of_line_markers([], "\r"))
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.normalize_end_of_line_markers([Line("  ", "")], "\r"),
        )
        self.assertListEqual(
            [Line("", "\r"), Line("", "\r"), Line("", "\r"), Line("", "\r")],
            whitespace_format2.normalize_end_of_line_markers(
                [Line("", "\n"), Line("", "\n"), Line("", "\r"), Line("", "\r")], "\r"
            ),
        )
        self.assertListEqual(
            [Line("hello", "\r"), Line("world", "\r")],
            whitespace_format2.normalize_end_of_line_markers(
                [Line("hello", "\n"), Line("world", "\r")], "\r"
            ),
        )
        self.assertListEqual(
            [
                Line("", "\r"),
                Line("", "\r"),
                Line("", "\r"),
                Line("", "\r"),
                Line("", "\r"),
                Line("", "\r"),
            ],
            whitespace_format2.normalize_end_of_line_markers(
                [
                    Line("", "\r"),
                    Line("", "\r"),
                    Line("", "\r\n"),
                    Line("", "\r\n"),
                    Line("", "\n"),
                    Line("", "\n"),
                ],
                "\r",
            ),
        )

        self.assertListEqual([], whitespace_format2.normalize_end_of_line_markers([], "\r\n"))
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.normalize_end_of_line_markers([Line("  ", "")], "\r\n"),
        )
        self.assertListEqual(
            [Line("", "\r\n"), Line("", "\r\n"), Line("", "\r\n"), Line("", "\r\n")],
            whitespace_format2.normalize_end_of_line_markers(
                [Line("", "\n"), Line("", "\n"), Line("", "\r"), Line("", "\r")], "\r\n"
            ),
        )
        self.assertListEqual(
            [Line("hello", "\r\n"), Line("world", "\r\n")],
            whitespace_format2.normalize_end_of_line_markers(
                [Line("hello", "\n"), Line("world", "\r")], "\r\n"
            ),
        )
        self.assertListEqual(
            [
                Line("", "\r\n"),
                Line("", "\r\n"),
                Line("", "\r\n"),
                Line("", "\r\n"),
                Line("", "\r\n"),
                Line("", "\r\n"),
            ],
            whitespace_format2.normalize_end_of_line_markers(
                [
                    Line("", "\r"),
                    Line("", "\r"),
                    Line("", "\r\n"),
                    Line("", "\r\n"),
                    Line("", "\n"),
                    Line("", "\n"),
                ],
                "\r\n",
            ),
        )

    def test_normalize_non_standard_whitespace(self):
        """Tests remove_non_standard_whitespace() function."""
        self.assertListEqual([], whitespace_format2.normalize_non_standard_whitespace([], "ignore"))
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.normalize_non_standard_whitespace([Line("  ", "")], "ignore"),
        )
        self.assertListEqual(
            [Line("hello", "")],
            whitespace_format2.normalize_non_standard_whitespace([Line("hello", "")], "ignore"),
        )
        self.assertListEqual(
            [Line("\v\f\t  ", "\n")],
            whitespace_format2.normalize_non_standard_whitespace(
                [Line("\v\f\t  ", "\n")], "ignore"
            ),
        )

        self.assertListEqual([], whitespace_format2.normalize_non_standard_whitespace([], "remove"))
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.normalize_non_standard_whitespace([Line("  ", "")], "remove"),
        )
        self.assertListEqual(
            [Line("hello", "")],
            whitespace_format2.normalize_non_standard_whitespace([Line("hello", "")], "remove"),
        )
        self.assertListEqual(
            [Line("\t  ", "\n")],
            whitespace_format2.normalize_non_standard_whitespace(
                [Line("\v\f\t  ", "\n")], "remove"
            ),
        )

        self.assertListEqual(
            [], whitespace_format2.normalize_non_standard_whitespace([], "replace")
        )
        self.assertListEqual(
            [Line("  ", "")],
            whitespace_format2.normalize_non_standard_whitespace([Line("  ", "")], "replace"),
        )
        self.assertListEqual(
            [Line("hello", "")],
            whitespace_format2.normalize_non_standard_whitespace([Line("hello", "")], "replace"),
        )
        self.assertListEqual(
            [Line("  \t  ", "\n")],
            whitespace_format2.normalize_non_standard_whitespace(
                [Line("\v\f\t  ", "\n")], "replace"
            ),
        )

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

    def test_format_file_content_1(self):
        """Tests format_file_content() function."""
        file_content_tracker = whitespace_format2.FileContentTracker([])
        whitespace_format2.format_file_content(
            file_content_tracker,
            argparse.Namespace(
                new_line_marker="auto",
                normalize_empty_files="ignore",
            ),
        )
        self.assertListEqual([], file_content_tracker.lines)

    def test_format_file_content_2(self):
        """Tests format_file_content() function."""
        file_content_tracker = whitespace_format2.FileContentTracker(
            [
                Line(" ", "\n"),
                Line(" ", "\n"),
                Line(" ", "\r"),
                Line(" ", "\r\n"),
                Line(" ", "\r\n"),
                Line(" \t \v \f ", ""),
            ]
        )
        whitespace_format2.format_file_content(
            file_content_tracker,
            argparse.Namespace(
                new_line_marker="auto",
                normalize_empty_files="ignore",
                normalize_whitespace_only_files="empty",
            ),
        )
        self.assertListEqual([], file_content_tracker.lines)

    def test_format_file_content_3(self):
        """Tests format_file_content() function."""
        file_content_tracker = whitespace_format2.FileContentTracker(
            [Line("hello", "\r\n"), Line("world   ", "")]
        )
        whitespace_format2.format_file_content(
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
        self.assertListEqual([Line("hello", "\n"), Line("world", "\n")], file_content_tracker.lines)


if __name__ == "__main__":
    unittest.main()
