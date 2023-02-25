# whitespace-format

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/DavidPal/whitespace-format/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/DavidPal/whitespace-format/tree/main)

Beautifier of source code files and text files. Its main features are:

* Add new line marker at the file if it is missing. 
* Make new line markers consistent (Linux `\n`, Windows `\r\n`, Mac `\r`).
* Remove empty lines at the end of the file.
* Remove whitespace at the end of each line.
* Replace tabs with spaces.
* Remove/replace non-standard whitespace characters.
* Auto-detection of line endings.

The motivation for this tool is to normalize source code files and text files before checking them into a version control system.  

Currently, the tool supports only UTF-8 encoding (which includes ASCII).

## Usage

### Basic usage

A sample command that formats source code files: 
```
python whitespace_format.py \
       --normalize-new-line-markers auto \
       --normalize-new-line-marker-at-end-of-file auto \
       --remove-trailing-empty-lines \
       --remove-trailing-whitespace \
       *.py *.c *.h *.java *.go *.md *.json *.tex *.csv
```

If you want only know if any changes **would be** made, add `--check-only` option:
```
python whitespace_format.py \
       --check-only \
       --normalize-new-line-markers auto \
       --normalize-new-line-marker-at-end-of-file auto \
       --remove-trailing-empty-lines \
       --remove-trailing-whitespace \
       *.py *.c *.h *.java *.go *.md *.json *.tex *.csv
```
This is a command could be used as validation step before checking the source files into a version control system.
The command outputs non-zero exit code if any of the files would be formatted. 

### Handling empty files

There are separate options for handling empty files and files consisting of whitespace characters only.

* `--normalize-empty-files MODE`
* `--normalize-whitespace-only-files MODE`

These files can be replaced by zero-byte files, or files consisting of single end of line marker, depending on
the `MODE`:
* `ignore` -- Leave the file as is.
* `empty` -- Replace the file with an empty file.
* `one-line-linux` -- Replace each file with a file consisting of single byte `\\n`.
* `one-line-mac` -- Replace each file with a file consisting of single byte `\\r`.
* `one-line-windows` -- Replace each file with a file consisting of two bytes `\\r\\n`.

If `--normalize-whitespace-only-files` is set to value other than `ignore`, 
it overrides `--normalize-empty-files setting` so that formatting is idempotent, i.e., 
running the same settings multiple times does not change the result.


### Handling special characters

Tabs can be replaced with spaces by passing the options `--replace-tabs-with-spaces N` 
where is `N` is the number of spaces. If `N` is negative, tabs are not replaced.

Non-standard whitespace characters (`\v` and `\f`) can be replaced by spaces or removed with the option
`--normalize-non-standard-whitespace MODE` where `MODE` either `replace`, `remove`, or `ignore`. 


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
