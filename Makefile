init:
	python -m pip install -r requirements.txt

test:
# 	python -m unittest discover -s test/pkg -p "test*.py"
	pytest -v test/pkg/test

clean:
	python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	test -f .coverage && rm .coverage || true
	test -d coverage && rm coverage -r || true

# .coverage: pkg
# 	coverage run --source=./pkg --data-file=.coverage -m unittest discover -s test/pkg -p "test*.py"

# coverage: .coverage
# coverage:
# 	python -m coverage run --source=./pkg --data-file=.coverage -m unittest discover -s test/pkg -p "test*.py"
# 	python -m coverage lcov --data-file=.coverage -o coverage/lcov.info
# 	python -m coverage xml --data-file=.coverage -o coverage/coverage.xml
# 	python -m coverage report --data-file=.coverage
# 	python -m coverage html --data-file=.coverage -d coverage/html

# lcov:
# 	python -m coverage run --source=./pkg --data-file=.coverage -m unittest discover -s test/pkg -p "test*.py"
# 	python -m coverage lcov --data-file=.coverage -o coverage/lcov.info
# 	python -m coverage report --data-file=.coverage

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

# Update ADR markdown document filenames
adr:
	python ./script/normalize_adr_filenames.py doc/adr

# Dry run of updating ADR markdown document filenames
adr_dry:
	python ./script/normalize_adr_filenames.py doc/adr --dry_run

tree:
	tree --gitignore

.PHONY: init test clean coverage coverage_html coverage_lcov dos2unix adr adr_dry tree