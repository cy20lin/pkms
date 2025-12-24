# Project Directory Tree Structure

```text
pkms
├─.vscode
├─doc
│  ├─adr
│  └─design
├─pkg
│  └─pkms
│      ├─globber
│      ├─indexer
│      ├─model
│      └─__pycache__
├─script
└─test
   ├─expect
   ├─pkg
   │  ├─test
   │  │  ├─pkms
   │  │  │  └─__pycache__
   │  │  ├─testing
   │  │  │  └─__pycache__
   │  │  └─__pycache__
   │  └─testing
   │      └─__pycache__
   └─webpage
```

## How to print project tree

One could print project with following command

```bash
tree --gitignore
```

## Structure Elaboration

- doc: for markdown documents
- Makefile: command for developments commands like 
  - test: test this project
  - clean: clean python cached files
  - coverage: generate test coverage report
  - dos2unix: project files CRLF to LF conversion
  - adr: do ADR document rename and normalize
  - adr_dry: dry run for ADR document rename and normalize
- pkg:  the folder to be included in PYTHON_PATH for using this pkms project
- test: for test suites and test utilities
  - pkg: the folder to be included in PYTHON_PATH for testing
    - testing: utility module for testing
    - test: test-suites for pkms, testing module
  - expect: folder for test suites expectation data
  - webpage: folder for webpage test data
- script: folder for utility scripts 