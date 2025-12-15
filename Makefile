init:
	python -m pip install -r requirements.txt

test:
	python -m unittest discover -s test/pkg -p "test*.py"

clean:
	python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	test -f .coverage && rm .coverage || true
	test -d coverage && rm coverage -r || true

# .coverage: pkg
# 	coverage run --source=./pkg --data-file=.coverage -m unittest discover -s test/pkg -p "test*.py"

# coverage: .coverage
coverage:
	python -m coverage run --source=./pkg --data-file=.coverage -m unittest discover -s test/pkg -p "test*.py"
	python -m coverage lcov --data-file=.coverage -o coverage/lcov.info
	python -m coverage xml --data-file=.coverage -o coverage/coverage.xml
	python -m coverage report --data-file=.coverage
	python -m coverage html --data-file=.coverage -d coverage/html

lcov:
	python -m coverage run --source=./pkg --data-file=.coverage -m unittest discover -s test/pkg -p "test*.py"
	python -m coverage lcov --data-file=.coverage -o coverage/lcov.info
	python -m coverage report --data-file=.coverage

dos2unix:
	dos2unix *.md || true
	dos2unix doc/**/*.md || true
	dos2unix pkg/**/*.py || true
	dos2unix test/pkg/**/*.py || true
	dos2unix test/expect/*.jsonc || true

.PHONY: init test clean coverage lcov dos2unix