PYTHON_ENVIRONMENT = "whitespace_format"
PYTHON_VERSION = "3.8.0"
SOURCE_FILES = *.py

TEMPORARY_FILES = pytest_results/ .coverage *.egg-info/ dist/ .ruff_cache/ .mypy_cache/ .pytest_cache/
NON_TEXT_FILES_REGEX = "\.pyc$$|^\.git/|^\.idea/|^\.ruff_cache/|^.mypy_cache/|^.coverage$$|^pytest_results/|^.pytest_cache/|^test_data/"

.PHONY: \
	whitespace-format-check \
	whitespace-format \
	init-file-checker \
	init-file-checker-add-missing \
	isort-check \
	isort-format \
	black-check \
	black-format \
	ruff ruff-fix \
	flake8 \
	pylint \
	mypy \
	lint \
	fix \
	test \
	coverage \
	clean \
	install-python \
	create-environment \
	delete-environment \
	install-dependencies \
	poetry-check-lock \
	build-package \
	publish-to-pypi \
	publish-to-test-pypi \

whitespace-format-check:
	# Check whitespace formatting.
	whitespace-format --check-only --color --verbose \
			--new-line-marker linux \
			--normalize-new-line-markers \
			--add-new-line-marker-at-end-of-file \
			--remove-trailing-whitespace \
			--remove-trailing-empty-lines \
			--normalize-non-standard-whitespace replace \
			--normalize-whitespace-only-files empty \
			--exclude $(NON_TEXT_FILES_REGEX)  .

whitespace-format:
	# Reformat code.
	whitespace-format --color --verbose \
			--new-line-marker linux \
			--normalize-new-line-markers \
			--add-new-line-marker-at-end-of-file \
			--remove-trailing-whitespace \
			--remove-trailing-empty-lines \
			--normalize-non-standard-whitespace replace \
			--normalize-whitespace-only-files empty \
			--exclude $(NON_TEXT_FILES_REGEX)  .

init-file-checker:
	# Checks if __init__.py files are not missing.
	init-file-checker `ls -d */`

init-file-checker-add-missing:
	# Adds missing __init__.py files.
	init-file-checker --add-missing `ls -d */`

isort-check:
	# Check imports.
	isort --check-only --diff --color --skip-glob="*_pb2.py" --skip-glob="*_rpc.py" --skip-glob="*_twirp.py" $(SOURCE_FILES)

isort-format:
	# Format imports.
	isort --color --skip-glob="*_pb2.py" --skip-glob="*_rpc.py" --skip-glob="*_twirp.py" $(SOURCE_FILES)

black-check:
	# Check code formatting.
	black --diff --check --color --exclude "_pb2.py|_rpc.py|_twirp.py" $(SOURCE_FILES)

black-format:
	# Reformat code.
	black --exclude "_pb2.py|_rpc.py|_twirp.py" $(SOURCE_FILES)

ruff:
	# Check code style with ruff.
	ruff check ./

ruff-fix:
	# Fix code style with ruff
	ruff check --fix ./

flake8:
	# Check PEP8 code style.
	flake8 --color=always --exclude="*_pb2.py,*_rpc.py,*_twirp.py" $(SOURCE_FILES)

pylint:
	# Static code analysis.
	pylint --output-format=colorized --ignore-patterns="_pb2.py,_rpc.py,_twirp.py" --rcfile=pylintrc $(SOURCE_FILES)

mypy:
	# Check type hints.
	mypy --exclude ".*_pb2.py$$|.*_rpc.py$$|.*_twirp.py$$" $(SOURCE_FILES)

# Run all linters
lint: whitespace-format-check black-check isort-check ruff flake8 pylint mypy

# Fix code formatting.
fix: whitespace-format black-format isort-format ruff-fix

test:
	# Run unit tests.
	pytest --verbose ./

coverage:
	# Compute unit test code coverage.
	coverage run -m pytest --verbose --junit-xml=pytest_results/pytest.xml  ./
	coverage report --show-missing
	coverage xml

clean:
	# Remove temporary files.
	rm -rf $(TEMPORARY_FILES)
	find . -name "__pycache__" -prune -exec rm -rf {} \;

install-python:
	# Install the correct version of python.
	pyenv install $(PYTHON_VERSION)

create-environment:
	# Create virtual environment.
	pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_ENVIRONMENT)
	pyenv local $(PYTHON_ENVIRONMENT)
	pip install --upgrade pip

delete-environment:
	# Delete virtual environment.
	pyenv virtualenv-delete $(PYTHON_ENVIRONMENT)
	pyenv local --unset
	rm -rf .python-version

install-dependencies:
	# Install all dependencies.
	poetry install --verbose
	pyenv rehash

poetry-check-lock:
	# Check that poetry.lock is consistent with pyproject.toml
	poetry check --lock

build-package:
	# Build a wheel package.
	poetry build

publish-to-pypi:
	# Publish package to PyPI.
	poetry publish

publish-to-test-pypi:
	# Publish package to Test-PyPI.
	poetry publish -r test-pypi
