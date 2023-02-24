#!/usr/bin/env python

"""Unit tests for whitespace_format module."""

import unittest

import whitespace_format


class TestWhitespaceFormat(unittest.TestCase):
    """Unit tests for whitespace_format module."""

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


if __name__ == "__main__":
    unittest.main()
