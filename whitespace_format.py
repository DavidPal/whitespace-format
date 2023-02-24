#!/usr/bin/env python

"""Formatter of white space in text files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2023

Usage:

   whitespace_format.py some_file.txt
"""

import argparse


def main():
    """Reads the input files and outputs their properly formatted versions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=False, action="store_true", default=False)
    parser.add_argument("--diff", required=False, action="store_true", default=False)
    parser.add_argument("input_files", help="List of input files", nargs="+", default=[], type=str)
    parsed_arguments = parser.parse_args()

    print(parsed_arguments.check)

    for file_name in parsed_arguments.input_files:
        print(file_name)


if __name__ == "__main__":
    main()
