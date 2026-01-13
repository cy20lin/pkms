init:
    python -m pip install -r requirements.txt

test:
    # python -m unittest discover -s test/pkg -p "test*.py"
    pytest -vv test/pkg/test

clean:
    python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
    python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
    test -f .coverage && rm .coverage || true
    test -d coverage && rm coverage -r || true

coverage:
    # pytest \
    # --cov=<source_directory_or_module1> \
    # --cov=<source_directory_or_module2> \
    # <test_directory_or_file>
    pytest --cov=pkg/pkms --cov=test/pkg/testing test/pkg/test

coverage_html:
    pytest --cov=pkg/pkms --cov=test/pkg/testing --cov-report=html test/pkg/test

coverage_lcov:
    pytest --cov=pkg/pkms --cov=test/pkg/testing --cov-report=lcov test/pkg/test

dos2unix:
    dos2unix *.md || true
    dos2unix doc/**/*.md || true
    dos2unix pkg/**/*.py || true
    dos2unix test/pkg/**/*.py || true
    dos2unix test/expect/*.jsonc || true

adr:
    python ./script/normalize_adr_filenames.py doc/adr

adr_dry:
    python ./script/normalize_adr_filenames.py doc/adr --dry_run

tree:
    tree --gitignore
