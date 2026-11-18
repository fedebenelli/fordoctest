from pathlib import Path

import pytest

from fordoctest.command_line import main

FPM_FIXTURE = Path(__file__).parent / "fpm_project"


def test_cli_success(make_project, capsys):
    project_file = make_project("documented_module.f90")

    assert main([str(project_file)]) == 0
    captured = capsys.readouterr()
    assert "No documentation issues found." in captured.out


def test_cli_issues(make_project, capsys):
    project_file = make_project("undocumented_for_cli.f90")

    assert main([str(project_file)]) == 1
    captured = capsys.readouterr()
    assert "Undocumented Module" in captured.err
    assert "documentation issue(s) found" in captured.err


def test_cli_quiet(make_project, capsys):
    project_file = make_project("undocumented_for_cli.f90")

    assert main(["--quiet", str(project_file)]) == 1
    captured = capsys.readouterr()
    assert "Undocumented Module" in captured.err
    assert "documentation issue(s) found" not in captured.err


def test_cli_quiet_success(make_project, capsys):
    project_file = make_project("documented_module.f90")

    assert main(["-q", str(project_file)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cli_max_modules_equals(make_project, capsys):
    project_file = make_project("multiple_modules.f90")

    assert main(["--max-modules=2", str(project_file)]) == 0

    assert main(["--max-modules", "1", str(project_file)]) == 1


def test_cli_max_modules_requires_value(capsys):
    assert main(["--max-modules"]) == 2
    captured = capsys.readouterr()
    assert "requires a value" in captured.err


def test_cli_invalid_max_modules(make_project, capsys):
    project_file = make_project("documented_module.f90")

    assert main(["--max-modules", "many", str(project_file)]) == 2
    captured = capsys.readouterr()
    assert "requires an integer" in captured.err


def test_cli_negative_max_modules(make_project, capsys):
    project_file = make_project("documented_module.f90")

    assert main(["--max-modules", "-1", str(project_file)]) == 2
    captured = capsys.readouterr()
    assert "zero or greater" in captured.err


def test_cli_requires_project(capsys):
    assert main([]) == 2
    captured = capsys.readouterr()
    assert "is required" in captured.err


def test_cli_help():
    with pytest.raises(SystemExit) as error:
        main(["--help"])

    assert error.value.code == 0


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--version"])

    assert error.value.code == 0
    assert "fordoctest" in capsys.readouterr().out


def test_cli_fpm_directory(capsys):
    assert main([str(FPM_FIXTURE)]) == 1
    captured = capsys.readouterr()
    assert "Undocumented Program" in captured.err


def test_cli_fpm_explicit(capsys):
    assert main(["--fpm", str(FPM_FIXTURE)]) == 1
    captured = capsys.readouterr()
    assert "Undocumented Program" in captured.err


def test_cli_fpm_toml_path(capsys):
    assert main([str(FPM_FIXTURE / "fpm.toml")]) == 1
    captured = capsys.readouterr()
    assert "Undocumented Program" in captured.err


def test_cli_imperative_check(make_project, capsys):
    project_file = make_project("non_imperative.f90")

    assert main(["--check-imperative", str(project_file)]) == 1
    captured = capsys.readouterr()
    assert "imperative verb" in captured.err


def test_cli_fpm_rejects_ford_options():
    assert main(["--fpm", str(FPM_FIXTURE), "-d", "src"]) == 2


def test_cli_forwards_ford_options(make_project):
    header = """\
project: test_project
src_dir: missing
preprocess: false
docmark: !
predocmark: >
"""
    project_file = make_project("documented_module.f90", header=header)

    assert main(["-q", str(project_file), "-d", "src"]) == 0


def test_cli_unknown_ford_option(make_project):
    project_file = make_project("documented_module.f90")

    assert main([str(project_file), "--badflag"]) == 2


def test_cli_missing_sources(make_project, capsys):
    header = """\
project: test_project
src_dir: missing
preprocess: false
"""
    project_file = make_project("documented_module.f90", header=header)

    assert main([str(project_file)]) == 2
    captured = capsys.readouterr()
    assert "No Fortran source files" in captured.err


def test_cli_double_dash(make_project):
    project_file = make_project("documented_module.f90")

    assert main(["--", str(project_file)]) == 0
