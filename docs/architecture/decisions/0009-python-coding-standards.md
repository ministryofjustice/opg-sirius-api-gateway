# 9. Python Best Practices

Date: 2020-02-03

## Status

Proposed

## Context

> Readbility counts -- [The Zen of Python](https://www.python.org/dev/peps/pep-0020/)


## Decision

#### Code Formatting

* Follow [PEP-8](https://www.python.org/dev/peps/pep-0008/) and the [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html) for code formatting
* Use static-typing as per [PEP-484](https://www.python.org/dev/peps/pep-0484/) wherever it is reasonable
* Use pre-commit hooks to enforce these standards where possible 


#### Code Style
* See the [Python Style Guide](../supporting-notes/python-style-guide.md)

#### Documentation

* Follow [PEP-257](https://www.python.org/dev/peps/pep-0257/) for docstring formatting using [reStructured Text](https://www.writethedocs.org/guide/writing/reStructuredText/)
* Generate documentation with Sphinx

#### Standard Tools
* Code Formatting: [Black](https://black.readthedocs.io/en/stable/)
* Linting/Complexity/Error Detection: [Flake8](https://flake8.pycqa.org/en/latest/)
* Type Checking: [MyPy](http://mypy-lang.org/)
* Unit Tests: [PyTest](https://docs.pytest.org/en/latest/)
* WSGI Server: [Gunicorn](https://gunicorn.org/)
* Package Management: [Pip](https://pypi.org/project/pip/)
* Emojis: [Emoji](https://pypi.org/project/emoji/)
* Dates: [????]




## Consequences

