# whitespace-format

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/DavidPal/whitespace-format/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/DavidPal/whitespace-format/tree/main)

[![Build, lint and test](https://github.com/DavidPal/whitespace-format/actions/workflows/build.yaml/badge.svg)](https://github.com/DavidPal/whitespace-format/actions/workflows/build.yaml)

Linter and formatter for source code files and text files.

The purpose of this tool is to normalize source code files (e.g., Python, Java,
C/C++, Ruby, Go, JavaScript, etc.) and text files (HTML, JSON, YAML, CSV,
MarkDown, LaTeX) before checking them into a version control system.

The features include:

* Auto-detection of new line markers (Linux `\n`, Windows `\r\n`, Mac `\r`).
* Add a new line marker at the end of the file if it is missing.
* Make new line markers consistent.
* Remove empty lines at the end of the file.
* Remove whitespace at the end of each line.
* Replace tabs with spaces.
* Remove/replace non-standard whitespace characters.

The formatting changes are
[idempotent](https://en.wikipedia.org/wiki/Idempotence), i.e., running the tool
second time (with the same parameters) has no effect.

## Installation

```shell
pip install whitespace-format
```

Installation requires Python 3.8.0 or higher.

## Usage

A sample command that formats source code files:
```shell
whitespace-format \
    --exclude ".git/|.idea/|.pyc$" \
    --new-line-marker linux \
    --normalize-new-line-markers \
    foo.txt  my_project/
```
The command above formats `foo.txt` and all files contained in `my_project/`
directory and its subdirectories. Files that contain `.git/` or `.idea/` in
their (relative) path are excluded. For example, files in `my_project/.git/`
and files in `my_project/.idea/` are excluded. Likewise, files ending with
`*.pyc` are excluded.

If you want to know only if any changes **would be** made, add `--check-only`
option:
```shell
whitespace-format \
    --check-only \
    --exclude ".git/|.idea/|.pyc$" \
    --new-line-marker linux \
    --normalize-new-line-markers \
    foo.txt  my_project/
```
This command can be used as a validation step before checking the source files
into a version control system. The command outputs non-zero exit code if any
of the files would be formatted.

### Options

* `--check-only` -- Do not format files. Only report which files would be formatted.
* `--follow-symlinks` -- Follow symbolic links when searching for files.
* `--exclude=REGEX` -- Regular expression that specifies which files to exclude.
The regular expression is evaluated on the path of each file.
* `--verbose` -- Print more messages than normally.
* `--quiet` -- Do not print any messages, except for errors when reading or writing files.

### Formatting options

* `--add-new-line-marker-at-end-of-file` -- Add missing new line marker at the end of each file.
* `--remove-new-line-marker-from-end-of-file` -- Remove all new line marker(s) from the end of each file.
This option cannot be used in combination with `--add-new-line-marker-at-end-of-file`.
Empty lines at the end of the file are removed, i.e., this option implies `--remove-trailing-empty-lines`
option.
* `--normalize-new-line-markers` -- Make new line markers consistent in each file
by replacing `\r\n`, `\n`, and `\r` with a consistent new line marker.
* `--remove-trailing-whitespace` -- Remove whitespace at the end of each line.
* `--remove-leading-empty-lines` -- Remove empty lines at the beginning of each file.
* `--remove-trailing-empty-lines` -- Remove empty lines at the end of each file.
* `--new-line-marker=MARKER` -- This option specifies the new line marker to use when
adding or replacing existing new line markers. `MARKER` must be one of the following:
  * `auto` -- Use new line marker that is the most common in each individual file.
  If no new line marker is present in the file, Linux `\n` is used.
  This is the default option.
  * `linux` -- Use Linux new line marker `\n`.
  * `mac` -- Use Mac new line marker `\r`.
  * `windows` -- Use Windows new line marker `\r\n`.
* `--encoding` -- Text encoding for both reading and writing files. Default encoding is `utf-8`.
The list of supported encodings can be found at
https://docs.python.org/3/library/codecs.html#standard-encodings

Note that input files can contain an arbitrary mix of new line markers `\n`,
`\r`, `\r\n` even within the same file. The option `--new-line-marker`
specifies the character that should be in the formatted file.

An opinionated combination of options is:
```shell
whitespace-format \
    --new-line-marker=linux \
    --add-new-line-marker-at-end-of-file \
    --normalize-new-line-markers \
    --remove-trailing-whitespace \
    --remove-leading-empty-lines \
    --remove-trailing-empty-lines \
    foo.txt  my_project/
```
This should work well for common programming languages (e.g., Python, Java,
C/C++, JavaScript) and common text file formats (e.g., CSV, LaTeX, JSON, YAML,
HTML, MarkDown, Makefile, TSV).

### Empty files

There are separate options for handling empty files and files consisting of
whitespace characters only:

* `--normalize-empty-files=MODE`
* `--normalize-whitespace-only-files=MODE`

where `MODE` is one of the following:

* `ignore` -- Leave the file as is. This is the default option.
* `empty` -- Replace the file with an empty file.
* `one-line` -- Replace each file with a file consisting of a single new line marker.

Depending on the mode, an empty file or a whitespace-only file will be either
ignored, replaced by a zero-byte file, or replaced by a file consisting of
the single new line marker.

If `--normalize-whitespace-only-files` is set to `empty`,
`--normalize-empty-files setting` set to `empty` as well. In other words,
combination `--normalize-whitespace-only-files=empty` and
`--normalize-empty-files=one-line` is not allowed, since it would lead to
behavior that is not idempotent.

### Special characters

* `--replace-tabs-with-spaces=N` -- Replace tabs with spaces.
Where is `N` is the number of spaces. If `N` is zero, tabs are removed.
If `N` is negative, tabs are not replaced. Default value is `-1`.

* `--normalize-non-standard-whitespace=MODE` -- Replace or remove
non-standard whitespace characters (`\v` and `\f`). `MODE` must be one of the following:
  * `ignore` -- Leave `\v` and `\f` as is. This is the default option.
  * `replace` -- Replace any occurrence of `\v` or `\f` with a single space.
  * `remove` -- Remove all occurrences of `\v` and `\f`

## License

MIT
