# UV Python Package Workshop

## Objective

Create a Python package using `uv`, add a custom `strings` module, test it with `pytest`, check it with `ruff`, and build an installable package.

## 1. Create a UV Package Project

Use `--package` so that `uv` creates a proper Python package layout:

```bash
uv init --package myproject
cd myproject
```

Initial structure:

```text
myproject/
├── pyproject.toml
├── README.md
├── .python-version
└── src/
    └── myproject/
        └── __init__.py
```

> **Important:** Use `uv init --package`, not just `uv init`, when the goal is to create an installable Python package.

## 2. Add `strings.py`

Create:

```text
src/
└── myproject/
    ├── __init__.py
    └── strings.py
```

Add five custom string functions:

```python
# src/myproject/strings.py

import random
import string


def jumble(text):
    """Randomly rearrange characters."""
    chars = list(text)
    random.shuffle(chars)
    return "".join(chars)


def remove_punct(text):
    """Remove punctuation characters."""
    return "".join(c for c in text if c not in string.punctuation)


def compress(text):
    """Remove consecutive duplicate characters."""
    if not text:
        return text

    result = text[0]

    for char in text[1:]:
        if char != result[-1]:
            result += char

    return result


def word_count(text):
    """Count words in a string."""
    return len(text.split())


def mirror(text):
    """Return the string in reverse order."""
    return text[::-1]
```

The package can now be imported as:

```python
from myproject.strings import jumble
```

## 3. Add Pytest and Ruff

Install both as development dependencies:

```bash
uv add --dev pytest ruff
```

## 4. Create Tests

Create:

```text
tests/
└── test_strings.py
```

Add:

```python
# tests/test_strings.py

from myproject.strings import (
    compress,
    jumble,
    mirror,
    remove_punct,
    word_count,
)


def test_jumble():
    result = jumble("python")
    assert len(result) == 6
    assert sorted(result) == sorted("python")


def test_remove_punct():
    assert remove_punct("Hello, World!") == "Hello World"


def test_compress():
    assert compress("aaabbccaaa") == "abca"


def test_word_count():
    assert word_count("Python is easy") == 3


def test_mirror():
    assert mirror("hello") == "olleh"
```

Run the tests:

```bash
uv run pytest
```

Expected result:

```text
5 passed
```

## 5. Run Ruff

Check the project:

```bash
uv run ruff check .
```

Automatically fix issues where possible:

```bash
uv run ruff check . --fix
```

## 6. Build the Package

Build the distributable package:

```bash
uv build
```

This creates:

```text
dist/
├── myproject-0.1.0-py3-none-any.whl
└── myproject-0.1.0.tar.gz
```

The `.whl` file is the wheel distribution and the `.tar.gz` file is the source distribution.

## 7. Final Project Structure

After completing all tasks:

```text
myproject/
├── pyproject.toml
├── README.md
├── .python-version
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── strings.py
├── tests/
│   └── test_strings.py
└── dist/
    ├── myproject-0.1.0-py3-none-any.whl
    └── myproject-0.1.0.tar.gz
```

## 8. Complete Command Sequence

For a fresh project, the essential commands are:

```bash
uv init --package myproject
cd myproject

uv add --dev pytest ruff

uv run ruff check .
uv run pytest

uv build
```

## 9. Common Import Errors

### `ModuleNotFoundError`

If you see:

```text
ModuleNotFoundError: No module named 'myproject'
```

Make sure the project was created with:

```bash
uv init --package myproject
```

and that the source is under:

```text
src/myproject/
```

Then run:

```bash
uv sync
uv run pytest
```

### Circular Import Error

If you see:

```text
ImportError: cannot import name ... from partially initialized module
```

check `strings.py`.

**Do not put this in `strings.py`:**

```python
from myproject.strings import (
    compress,
    jumble,
    mirror,
    remove_punct,
    word_count,
)
```

That import belongs in:

```text
tests/test_strings.py
```

`strings.py` should contain the function implementations, while `test_strings.py` imports those functions for testing.

## Key Learning Points

1. `uv init --package` creates a package-oriented project.
2. `src/myproject/` contains the actual Python package.
3. `tests/` contains the test code.
4. `uv add --dev` adds development dependencies.
5. `uv run` executes commands in the project's environment.
6. `pytest` runs automated tests.
7. `ruff` checks code quality.
8. `uv build` creates installable package distributions.
9. The package is imported as `myproject`, not `src.myproject`.
