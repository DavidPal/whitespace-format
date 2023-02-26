# whitespace-format

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/DavidPal/whitespace-format/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/DavidPal/whitespace-format/tree/main)

Beautifier of source code files and text files. Its main features are:

* Add a new line marker at the end of the file if it is missing.
* Make new line markers consistent (Linux `\n`, Windows `\r\n`, Mac `\r`).
* Remove empty lines at the end of the file.
* Remove whitespace at the end of each line.
* Replace tabs with spaces.
* Remove/replace non-standard whitespace characters.
* Auto-detection of line endings.

The motivation for this tool is to normalize source code files and text files
before checking them into a version control system.

Technically, the tool supports only UTF-8 encoding. However, many encodings are
valid UTF-8 sequences and the tool processes only ` `, `\n`, `\f`, `\v`, `\t`
characters. As a result, the tool should work for many other encodings (e.g.
ASCII, ISO-8859-1, CP1250).

## Usage

A sample command that formats source code files:
```shell
python whitespace_format.py \
       --exclude ".git/|.idea/|.pyc$" \
       --new-line-marker linux \
       --normalize-new-line-markers \
       foo.txt  my_project/
```
The command above formats `foo.txt` and all files contained `my_project/` and
its subdirectories. Files that contain `.git/` or `.idea/` in their (relative)
path are excluded. For example, files in `my_project/.git/` and files in
`my_project/.idea/` are excluded. Likewise, files ending with `*.pyc` are
excluded.

If you want only know if any changes **would be** made, add `--check-only` option:
```shell
python whitespace_format.py \
       --exclude ".git/|.idea/|.pyc$" \
       --check-only \
       --new-line-marker linux \
       --normalize-new-line-markers \
       foo.txt  my_project/
```
This command can be used as a validation step before checking the source files
into a version control system. The command outputs non-zero exit code if any
of the files would be formatted.

### Basic formatting options

* `--add-new-line-marker-at-end-of-file` -- Add missing new line marker at end of each file.
* `--remove-new-line-marker-from-end-of-file` -- Remove all new line marker(s) from the end of each file.
This option is ignored when `--add-new-line-marker-at-end-of-file` is used.
Empty lines at the end of the file are removed. 
* `--normalize-new-line-markers` -- Make new line markers consistent in each file 
by replacing `\\r\\n`, `\\n`, and `\r` with a consistent new line marker. 
* `--remove-trailing-whitespace` -- Remove whitespace at the end of each line.
* `--remove-trailing-empty-lines` -- Remove empty lines at the end of each file.
* `--new-line-marker=MARKER` -- This option specifies what new line marker to use.
`MARKER` must be one of the following:
  * `auto` -- Use new line marker that is the most common in each individual file.
  If no new line marker is present in the file, Linux `\n` is used.
  This is the default option.
  * `linux` -- Use Linux new line marker `\\n`.
  * `mac` -- Use Mac new line marker `\\r`.
  * `windows` -- Use Windows new line marker `\\r\\n`.

Note that input files can contain an arbitrary mix of new line markers `\n`,
`\r`, `\r\n` even within the same file. The option `--new-line-marker`
specifies the character that should be in the formatted file. 

An opinionated combination of options is:
```shell
python whitespace_format.py \
       --new-line-marker=linux \
       --add-new-line-marker-at-end-of-file \
       --normalize-new-line-markers \
       --remove-trailing-whitespace \
       --remove-trailing-empty-lines \
       foo.txt  my_project/
```
This should work well for common programming languages (e.g. Python, Java, C/C++, JavaScript)
and common text file formats (CSV, LaTeX, JSON, YAML, HTML, MarkDown).

### Common

* `--check-only` -- Do not format files. Only report which files would be formatted.
* `--follow-symlinks` -- Follow symbolic links when searching for files.
* `--exclude=REGEX` -- Regular expression that specifies which files should be excluded.
* `--verbose` -- Print more messages than normally.
* `--quiet` -- Do not print any messages, except for errors when reading or writing files.

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
single end of line marker.

If `--normalize-whitespace-only-files` is set to value other than `ignore`, it
overrides `--normalize-empty-files setting`. This behavior exists so that
formatting is [idempotent](https://en.wikipedia.org/wiki/Idempotence). That is,
running the program multiple times does not change the result. (Otherwise, 
consecutive runs with the combination 
`--normalize-whitespace-only-files=empty` and `--normalize-empty-files=one-line`
would keep switching content of empty files back and forth.)

### Special characters

* `--replace-tabs-with-spaces=N` -- Replace tabs with spaces.
Where is `N` is the number of spaces. If `N` is negative, tabs are not replaced.
Default value is `-1`.

* `--normalize-non-standard-whitespace=MODE` -- Replace or remove 
non-standard whitespace characters (`\v` and `\f`). `MODE` must be one of the following:
  * `ignore` -- Leave `\v` and `f` as is. This is the default option.
  * `replace` -- Replace any occurrence of `\v` or `\f` with a single space.
  * `remove` -- Remove all occurrences of `\v` and `\f`


## MacOS development setup

1) Make sure you have [brew](https://brew.sh/) package manager installed.

2) Install [pyenv](https://github.com/pyenv/pyenv), [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
   and [poetry](https://python-poetry.org/):
    ```shell
    brew install pyenv
    brew install pyenv-virtualenv
    brew install poetry
    ```

3) Create Python virtual environment with the correct Python version:
   ```shell
   make install-python
   make create-environment
   ```

4) Add the following lines to `.zshrc` or `.bash_profile` and restart the terminal:
   ```shell
   # Pyenv settings
   export PYENV_ROOT="$HOME/.pyenv"
   export PATH="$PYENV_ROOT/bin:$PATH"
   eval "$(pyenv init --path)"
   eval "$(pyenv virtualenv-init -)"
   ```

5) Install all dependencies
    ```shell
    make install-dependecies
    ```

If you need to delete the Python virtual environment, you can do so with the
command `make delete-environment`.

## Running unit tests and code checks

If you make code change, run unit tests and code checks with the command:
```shell
make clean isort-check black-check flake8 pylint mypy test coverage
```

Each make target runs different checks:
- `clean` deletes temporary files
- `isort-check` runs [isort](https://pycqa.github.io/isort/) checker of imports in `*.py` files
- `black-check` runs [black](https://github.com/psf/black/) code format checker on `*.py` files
- `flake8` runs [flake8](https://flake8.pycqa.org/) code style checker on `*.py` files
- `pylint` runs [pylint](https://pylint.org/) code checker on `*.py` files
- `mypy` runs [mypy](http://mypy-lang.org/) type checker on `*.py` files
- `test` runs unit tests
- `coverage` generates code coverage report

You can automatically format code with the command:
```shell
make isort-format black-format
```

## Modifying dependencies

The list of Python packages that this project depends on is specified in
`pyproject.toml` and in `poetry.lock` files. The file `pyproject.toml` can be
edited by humans. The file `poetry.lock` is automatically generated by `poetry`.

Install a development dependency with the command:
```shell
poetry add --dev <some_new_python_tool>
```

Install a new production dependency with the command:
```shell
poetry add <some_python_library>
```

### Manual modification of `pyproject.toml`

Instead of using `poetry add` command, you can edit `pyproject.toml` file. Then,
regenerate `poetry.lock` file with the command:
```shell
poetry lock
```
or the command:
```shell
poetry lock --no-update
```
The latter command does not update already locked packages.

### Fixing broken Python environment

If your Python virtual environment becomes broken or polluted with unnecessary
packages, delete it, recreate it from scratch and install dependencies a fresh
with the following commands:
```shell
make delete-environment
make create-environment
make install-dependencies
```
