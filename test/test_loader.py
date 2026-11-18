import shutil
from pathlib import Path

import pytest

from fordoctest import FordDocumentationTester, ProjectLoadError, load_project
from fordoctest.loader import (
    load_fpm_project,
    load_project_file,
    read_fpm_config,
)

FPM_FIXTURE = Path(__file__).parent / "fpm_project"
FIXTURES = Path(__file__).parent / "fixtures"


def test_load_project_file(make_project):
    project_file = make_project("documented_module.f90")

    project = load_project_file(project_file)

    assert len(project.files) == 1
    assert project.name == "test_project"


def test_load_project_missing_file(tmp_path):
    with pytest.raises(ProjectLoadError, match="not found"):
        load_project_file(tmp_path / "missing.md")


def test_load_project_directory_without_fpm(tmp_path):
    with pytest.raises(ProjectLoadError, match="is a directory"):
        load_project_file(tmp_path)


def test_project_without_source_files(tmp_path):
    project_file = tmp_path / "doc.md"
    project_file.write_text(
        "project: empty\nsrc_dir: missing\npreprocess: false\n",
        encoding="utf-8",
    )

    with pytest.raises(ProjectLoadError, match="No Fortran source files"):
        load_project_file(project_file)


def test_load_fpm_directory(make_project, tmp_path):
    make_project("documented_module.f90")
    (tmp_path / "fpm.toml").write_text(
        'name = "fpm_project"\nversion = "0.1.0"\n', encoding="utf-8"
    )

    project = load_project(tmp_path)

    assert project.name == "fpm_project"
    assert project.settings.version == "0.1.0"
    assert len(project.files) == 1


def test_load_fpm_file(make_project, tmp_path):
    make_project("documented_module.f90")
    fpm_file = tmp_path / "fpm.toml"
    fpm_file.write_text('name = "fpm_project"\n', encoding="utf-8")

    project = load_fpm_project(fpm_file)

    assert project.name == "fpm_project"


def test_load_fpm_with_extra_ford(make_project, tmp_path):
    make_project("documented_module.f90")
    fpm_file = tmp_path / "fpm.toml"
    fpm_file.write_text(
        """\
name = "fpm_project"

[extra.ford]
project = "extra project"
src_dir = ["src"]
preprocess = false
""",
        encoding="utf-8",
    )

    project = load_fpm_project(fpm_file)

    assert project.name == "extra project"


def test_fpm_missing_file(tmp_path):
    with pytest.raises(ProjectLoadError, match="fpm.toml not found"):
        load_fpm_project(tmp_path / "fpm.toml")


def test_fpm_without_sources(tmp_path):
    fpm_file = tmp_path / "fpm.toml"
    fpm_file.write_text('name = "empty"\n', encoding="utf-8")

    with pytest.raises(ProjectLoadError, match="No fpm source directories"):
        load_fpm_project(fpm_file)


def test_fpm_source_directory_without_files(tmp_path):
    (tmp_path / "src").mkdir()
    fpm_file = tmp_path / "fpm.toml"
    fpm_file.write_text('name = "empty"\n', encoding="utf-8")

    with pytest.raises(ProjectLoadError, match="No Fortran source files"):
        load_fpm_project(fpm_file)


def test_load_project_forces_fpm(tmp_path):
    fpm_file = tmp_path / "fpm.toml"
    fpm_file.write_text('name = "forced"\n', encoding="utf-8")
    (tmp_path / "src").mkdir()
    shutil.copyfile(
        FIXTURES / "documented_module.f90",
        tmp_path / "src" / "a.f90",
    )

    project = load_project(fpm_file, fpm=True)

    assert project.name == "forced"


def test_fpm_fixture_issues():
    tester = FordDocumentationTester.from_fpm(FPM_FIXTURE)
    issues = tester.find_issues()

    assert len(issues) == 4
    assert {issue.kind for issue in issues} == {
        "Module",
        "Procedure",
        "Program",
    }


def test_from_project_file_factory(make_project):
    tester = FordDocumentationTester.from_project_file(
        make_project("documented_module.f90")
    )

    assert tester.find_issues() == []


def _fpm_project(tmp_path, extra: str = "") -> Path:
    (tmp_path / "src").mkdir(exist_ok=True)
    shutil.copyfile(
        FIXTURES / "documented_module.f90",
        tmp_path / "src" / "a.f90",
    )
    fpm_file = tmp_path / "fpm.toml"
    fpm_file.write_text(f'name = "configured"\n{extra}', encoding="utf-8")
    return fpm_file


def test_read_fpm_config_defaults(tmp_path):
    config = read_fpm_config(_fpm_project(tmp_path))

    assert config.max_modules == 1
    assert config.check_imperative is False
    assert config.color == "auto"


def test_read_fpm_config_values(tmp_path):
    extra = (
        "\n[extra.fordoxtest]\n"
        "max_modules = 3\n"
        "check_imperative = true\n"
        'color = "never"\n'
    )
    config = read_fpm_config(_fpm_project(tmp_path, extra))

    assert config.max_modules == 3
    assert config.check_imperative is True
    assert config.color == "never"


def test_read_fpm_config_rejects_unknown_keys(tmp_path):
    fpm_file = _fpm_project(tmp_path, "\n[extra.fordoxtest]\nmax_module = 2\n")

    with pytest.raises(ProjectLoadError, match="Unknown key"):
        read_fpm_config(fpm_file)


@pytest.mark.parametrize("value", ['"two"', "-1", "true"])
def test_read_fpm_config_rejects_bad_max_modules(tmp_path, value):
    fpm_file = _fpm_project(
        tmp_path, f"\n[extra.fordoxtest]\nmax_modules = {value}\n"
    )

    with pytest.raises(ProjectLoadError, match="max_modules"):
        read_fpm_config(fpm_file)


def test_read_fpm_config_rejects_bad_check_imperative(tmp_path):
    fpm_file = _fpm_project(
        tmp_path, '\n[extra.fordoxtest]\ncheck_imperative = "yes"\n'
    )

    with pytest.raises(ProjectLoadError, match="check_imperative"):
        read_fpm_config(fpm_file)


def test_read_fpm_config_rejects_bad_color(tmp_path):
    fpm_file = _fpm_project(
        tmp_path, '\n[extra.fordoxtest]\ncolor = "rainbow"\n'
    )

    with pytest.raises(ProjectLoadError, match="color"):
        read_fpm_config(fpm_file)


def test_read_fpm_config_accepts_canonical_table(tmp_path):
    fpm_file = _fpm_project(
        tmp_path, "\n[extra.fordoctest]\nmax_modules = 4\n"
    )

    assert read_fpm_config(fpm_file).max_modules == 4


def test_read_fpm_config_rejects_both_tables(tmp_path):
    fpm_file = _fpm_project(
        tmp_path,
        "\n[extra.fordoxtest]\nmax_modules = 2\n"
        "\n[extra.fordoctest]\nmax_modules = 3\n",
    )

    with pytest.raises(ProjectLoadError, match="Use only one"):
        read_fpm_config(fpm_file)


def test_read_fpm_config_requires_table(tmp_path):
    fpm_file = _fpm_project(tmp_path, '\n[extra]\nfordoctest = "nope"\n')

    with pytest.raises(ProjectLoadError, match="must be a table"):
        read_fpm_config(fpm_file)


def test_from_fpm_uses_config(tmp_path):
    (tmp_path / "src").mkdir()
    shutil.copyfile(
        FIXTURES / "multiple_modules.f90",
        tmp_path / "src" / "many.f90",
    )
    (tmp_path / "fpm.toml").write_text(
        'name = "configured"\n\n[extra.fordoxtest]\nmax_modules = 2\n',
        encoding="utf-8",
    )

    tester = FordDocumentationTester.from_fpm(tmp_path)
    assert tester.find_issues() == []

    explicit = FordDocumentationTester.from_fpm(
        tmp_path, max_modules_per_file=1
    )
    assert [issue.kind for issue in explicit.find_issues()] == ["Module count"]


def test_from_fpm_uses_imperative_config(tmp_path):
    (tmp_path / "src").mkdir()
    shutil.copyfile(
        FIXTURES / "non_imperative.f90",
        tmp_path / "src" / "style.f90",
    )
    (tmp_path / "fpm.toml").write_text(
        'name = "configured"\n\n'
        "[extra.fordoxtest]\ncheck_imperative = true\n",
        encoding="utf-8",
    )

    tester = FordDocumentationTester.from_fpm(tmp_path)
    assert [issue.kind for issue in tester.find_issues()] == [
        "Documentation style"
    ]
