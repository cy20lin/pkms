# Development Environment Setup

## Python packages setup

```sh
pip install beautifulsoup4
pip install lxml
pip install html5lib
pip install pathspec
# for html indexer
pip install inscripts
# For testing & coverage
pip install pytest
pip install pytest-cov
```

## How to test

```bash
# In project root
# -v for verbose, for detailed debug print
pytest -v test/pkg/test
```

## How to get test coverage

```bash
# pytest \
# --cov=<source_directory_or_module1> \
# --cov=<source_directory_or_module2> \
# <test_directory_or_file>
pytest --cov=pkg/pkms --cov=test/pkg/testing test/pkg/test
```