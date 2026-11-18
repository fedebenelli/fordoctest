# AGENTS.md

Small Python CLI that checks whether Fortran projects are documented using
FORD's parser (`ford >= 7.0.5, < 8`). Python `>= 3.10`.

## Setup and commands

- Always work in a virtualenv. Never install packages system-wide. Use
  `uv venv --python 3.11 .venv && source .venv/bin/activate`, or
  virtualenvwrapper (`mkvirtualenv fordoctest`). `.venv` is gitignored.
- Install: `pip install -r requirements_dev.txt` (editable install plus dev
  tools).
- Tests: `python -m pytest -q` (testpaths is `test`). No Fortran compiler is
  needed; test projects set `preprocess: false`.
- Single test: `python -m pytest test/test_analyze.py::test_undocumented_module -q`
- Coverage: `pytest --cov=fordoctest --cov-report=term-missing` (gate is 90%).
- Format: `black .` using the repo config (79 columns, py310). There is no
  linter or typechecker.
- CLI: `fordoctest <project.md>` or `fordoctest fpm.toml`. Exit codes: 0
  clean, 1 issues, 2 bad input. `python -m fordoctest` also works.

## Architecture

- `fordoctest/loader.py` wraps FORD: `load_project_file` uses
  `ford.load_settings` + `ford.parse_arguments`; `load_fpm_project` uses
  `[extra.ford]` when present, otherwise builds `ProjectSettings` from the
  standard fpm directories. Keep FORD API calls here.
- `fordoctest/core.py` — `FordDocumentationTester` takes an already-parsed
  `Project`; use `from_project_file()` or `from_fpm()`.
  - `find_issues()` returns every `DocumentationIssue`; `analyze()` raises one
    `DocumentationError` containing all of them.
  - Checks live in `_check_unit`, `_check_types`, `_check_interfaces`,
    `_check_procedures`; deduplicate by object id because FORD can expose the
    same submodule procedure twice.
  - Do not call `Project.correlate()`: it injects inherited/generated docs.
- `fordoctest/errors.py` — `DocumentationIssue`, `DocumentationError`, and
  message constructors.
- `fordoctest/command_line.py` — splits fordoctest options manually and lets
  FORD parse the remaining arguments so FORD flags keep working. In FPM mode,
  FORD flags are rejected.
- `fordoctest/__main__.py` is a thin `SystemExit(main())` wrapper.

## Testing and fixtures

- Fortran sources analyzed by tests live in `test/fixtures/*.f90`, never as
  strings inside Python. Add a `.f90` file and pass its name to `make_project`.
- `test/conftest.py` provides `make_project`, which writes a temporary
  `doc.md` + `src/` tree and copies the requested fixture files. Prefer this
  over `sys.argv` patching.
- `test/fpm_project/` is a real fpm fixture used by loader/CLI tests; its
  undocumented entities are asserted.
- `test/case1/` and `test/fully_documented/` are legacy FORD fixtures.
- CLI tests call `main([...])` directly and use `capsys`; FORD progress output
  goes to stdout unless `-q/--quiet` is used.
- The imperative-verb check is opt-in (`--check-imperative`) and deliberately
  conservative; do not turn it into an NLP heuristic.

## Packaging and release

- Version lives only in `fordoctest/__init__.py`; setuptools reads it
  dynamically.
- CI: `.github/workflows/ci.yml` runs black and tests on Python 3.10/3.11.
- Release: push a `v*` tag. PyPI publishing uses trusted publishing and
  requires the `pypi` environment/trusted publisher to be configured in the
  PyPI project settings. PyPI name: `fordoctest`; git remote:
  `fedebenelli/fordoctester`.
- README and `[project.urls]` should match the actual repository/name.

## Do not edit

- `build/` and `fordoctest.egg-info/` are stale, gitignored artifacts (the
  build copy still contains the removed `warns.py`/`main.py` API). Edit
  `fordoctest/` only.
