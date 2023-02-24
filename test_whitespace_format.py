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

    def test_remove_last_end_of_line(self):
        """Tests remove_last_end_of_line() function."""
        self.assertEqual("", whitespace_format.remove_last_end_of_line(""))
        self.assertEqual("hello", whitespace_format.remove_last_end_of_line("hello"))
        self.assertEqual("hello", whitespace_format.remove_last_end_of_line("hello\n"))
        self.assertEqual("hello", whitespace_format.remove_last_end_of_line("hello\r"))
        self.assertEqual("hello", whitespace_format.remove_last_end_of_line("hello\r\n"))
        self.assertEqual("hello\n", whitespace_format.remove_last_end_of_line("hello\n\r"))
        self.assertEqual(" ", whitespace_format.remove_last_end_of_line(" \n"))
        self.assertEqual(" ", whitespace_format.remove_last_end_of_line(" \r"))
        self.assertEqual(" ", whitespace_format.remove_last_end_of_line(" \r\n"))
        self.assertEqual(" \n", whitespace_format.remove_last_end_of_line(" \n\r"))

    def test_fix_empty_file(self):
        """Tests fix_empty_file() function."""
        self.assertEqual("", whitespace_format.fix_empty_file("", "ignore"))
        self.assertEqual("", whitespace_format.fix_empty_file("", "empty"))
        self.assertEqual("\n", whitespace_format.fix_empty_file("", "one-line-linux"))
        self.assertEqual("\r", whitespace_format.fix_empty_file("", "one-line-mac"))
        self.assertEqual("\r\n", whitespace_format.fix_empty_file("", "one-line-windows"))

        self.assertEqual(" \t ", whitespace_format.fix_empty_file(" \t ", "ignore"))
        self.assertEqual("", whitespace_format.fix_empty_file(" \t ", "empty"))
        self.assertEqual("\n", whitespace_format.fix_empty_file(" \t ", "one-line-linux"))
        self.assertEqual("\r", whitespace_format.fix_empty_file(" \t ", "one-line-mac"))
        self.assertEqual("\r\n", whitespace_format.fix_empty_file(" \t ", "one-line-windows"))

    def test_fix_end_of_file(self):
        """Tests fix_end_of_file() function."""
        self.assertEqual("", whitespace_format.fix_end_of_file("", "ignore", "\n"))
        self.assertEqual("  ", whitespace_format.fix_end_of_file("  ", "ignore", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello", "ignore", "\n"))
        self.assertEqual("  \n", whitespace_format.fix_end_of_file("  \n", "ignore", "\n"))
        self.assertEqual("  \r", whitespace_format.fix_end_of_file("  \r", "ignore", "\n"))
        self.assertEqual("  \r\n", whitespace_format.fix_end_of_file("  \r\n", "ignore", "\n"))

        self.assertEqual("", whitespace_format.fix_end_of_file("", "remove", "\n"))
        self.assertEqual("  ", whitespace_format.fix_end_of_file("  ", "remove", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello", "remove", "\n"))
        self.assertEqual("\n  ", whitespace_format.fix_end_of_file("\n  \n", "remove", "\n"))
        self.assertEqual("\n  ", whitespace_format.fix_end_of_file("\n  \r", "remove", "\n"))
        self.assertEqual("\n  ", whitespace_format.fix_end_of_file("\n  \r\n", "remove", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello\n\n\n", "remove", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello\r\r\r", "remove", "\n"))
        self.assertEqual(
            "hello", whitespace_format.fix_end_of_file("hello\r\n\r\n\r\n", "remove", "\n")
        )

        self.assertEqual("", whitespace_format.fix_end_of_file("", "remove", "\n"))
        self.assertEqual("  ", whitespace_format.fix_end_of_file("  ", "remove", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello", "remove", "\n"))
        self.assertEqual("\n  ", whitespace_format.fix_end_of_file("\n  \n", "remove", "\n"))
        self.assertEqual("\n  ", whitespace_format.fix_end_of_file("\n  \r", "remove", "\n"))
        self.assertEqual("\n  ", whitespace_format.fix_end_of_file("\n  \r\n", "remove", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello\n\n\n", "remove", "\n"))
        self.assertEqual("hello", whitespace_format.fix_end_of_file("hello\r\r\r", "remove", "\n"))
        self.assertEqual(
            "hello", whitespace_format.fix_end_of_file("hello\r\n\r\n\r\n", "remove", "\n")
        )


if __name__ == "__main__":
    unittest.main()
