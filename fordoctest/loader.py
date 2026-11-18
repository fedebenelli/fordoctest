"""Load FORD project models without parsing ``sys.argv``."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import ford
from ford.fortran_project import Project
from ford.settings import ProjectSettings

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

FPM_SOURCE_DIRS = ("src", "app", "test", "example", "examples", "benchmark")
# ``fordoxtest`` was used in the original issue; keep it as an alias.
TOOL_TABLES = ("fordoctest", "fordoxtest")
COLOR_MODES = ("auto", "always", "never")
CONFIG_KEYS = frozenset({"max_modules", "check_imperative", "color"})


class ProjectLoadError(RuntimeError):
    """Raised when a project file cannot be loaded."""


@dataclass(frozen=True)
class ToolConfig:
    """Settings read from ``[extra.fordoctest]`` in an fpm manifest."""

    max_modules: int = 1
    check_imperative: bool = False
    color: str = "auto"


class _ProjectFileRef:
    """Minimal stand-in for FORD's argparse file object."""

    def __init__(self, name: str) -> None:
        self.name = name


def _project_from_settings(
    settings: ProjectSettings, directory: Path
) -> Project:
    settings, _ = ford.parse_arguments(
        {"project_file": _ProjectFileRef(str(directory))},
        "",
        settings,
        directory,
    )
    project = Project(settings)
    if not project.files:
        raise ProjectLoadError(f"No Fortran source files found in {directory}")
    return project


def _read_toml(fpm_file: Path) -> Dict[str, Any]:
    try:
        return tomllib.loads(fpm_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ProjectLoadError(
            f"Could not read {fpm_file}: {error}"
        ) from error


def _locate_fpm(path: Union[str, Path]) -> Tuple[Path, Path]:
    project_path = Path(path).expanduser()
    if project_path.is_dir():
        directory = project_path
        fpm_file = directory / "fpm.toml"
    else:
        fpm_file = project_path
        directory = fpm_file.parent

    if not fpm_file.is_file():
        raise ProjectLoadError(f"fpm.toml not found: {fpm_file}")
    return fpm_file, directory


def _validate_config(
    section: Dict[str, Any], fpm_file: Path, table: str
) -> ToolConfig:
    unknown = set(section) - CONFIG_KEYS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ProjectLoadError(
            f"Unknown key(s) in [extra.{table}] in {fpm_file}: {names}"
        )

    max_modules = section.get("max_modules", 1)
    if not isinstance(max_modules, int) or isinstance(max_modules, bool):
        raise ProjectLoadError(
            f"'max_modules' in [extra.{table}] must be an integer"
        )
    if max_modules < 0:
        raise ProjectLoadError(
            f"'max_modules' in [extra.{table}] must be zero or greater"
        )

    check_imperative = section.get("check_imperative", False)
    if not isinstance(check_imperative, bool):
        raise ProjectLoadError(
            f"'check_imperative' in [extra.{table}] must be a boolean"
        )

    color = section.get("color", "auto")
    if color not in COLOR_MODES:
        modes = ", ".join(COLOR_MODES)
        raise ProjectLoadError(
            f"'color' in [extra.{table}] must be one of: {modes}"
        )

    return ToolConfig(
        max_modules=max_modules,
        check_imperative=check_imperative,
        color=color,
    )


def _config_table(extra: Dict[str, Any], fpm_file: Path):
    present = [name for name in TOOL_TABLES if name in extra]
    if len(present) > 1:
        names = " and ".join(f"[extra.{name}]" for name in present)
        raise ProjectLoadError(f"Use only one of {names} in {fpm_file}")
    if not present:
        return {}, TOOL_TABLES[0]

    table = present[0]
    section = extra[table]
    if not isinstance(section, dict):
        raise ProjectLoadError(
            f"'extra.{table}' in {fpm_file} must be a table"
        )
    return section, table


def read_fpm_config(path: Union[str, Path]) -> ToolConfig:
    """Read fordoctest settings from ``[extra.fordoctest]``.

    ``[extra.fordoxtest]`` (the spelling used when the issue was opened) is
    accepted as an alias. Missing tables and keys fall back to the defaults;
    unknown keys are rejected so typos do not silently disable checks.
    """
    fpm_file, _ = _locate_fpm(path)
    data = _read_toml(fpm_file)
    extra = data.get("extra", {})
    if not isinstance(extra, dict):
        raise ProjectLoadError(f"'extra' in {fpm_file} must be a table")
    section, table = _config_table(extra, fpm_file)
    return _validate_config(section, fpm_file, table)


def load_project_file(path: Union[str, Path]) -> Project:
    """Load a FORD markdown project file."""
    project_file = Path(path).expanduser()
    if project_file.is_dir():
        raise ProjectLoadError(
            f"{project_file} is a directory; pass a FORD project file or "
            "an fpm.toml"
        )
    if not project_file.is_file():
        raise ProjectLoadError(f"Project file not found: {project_file}")

    try:
        text = project_file.read_text(encoding="utf-8")
    except OSError as error:
        raise ProjectLoadError(
            f"Could not read {project_file}: {error}"
        ) from error

    directory = project_file.parent
    proj_docs, settings = ford.load_settings(
        text, directory, project_file.name
    )
    settings, _ = ford.parse_arguments(
        {"project_file": _ProjectFileRef(str(project_file))},
        proj_docs,
        settings,
        directory,
    )
    project = Project(settings)
    if not project.files:
        raise ProjectLoadError(
            f"No Fortran source files found for {project_file}. "
            "Check 'src_dir' in the project file."
        )
    return project


def load_fpm_project(path: Union[str, Path]) -> Project:
    """Load an fpm project, using ``[extra.ford]`` when present.

    FORD itself only understands settings in ``[extra.ford]``. If that table
    is absent, build defaults from the standard fpm source directories so a
    normal ``fpm.toml`` can be checked directly.
    """
    fpm_file, directory = _locate_fpm(path)

    settings: Optional[ProjectSettings] = ford.settings.load_toml_settings(
        directory
    )

    if settings is None:
        data = _read_toml(fpm_file)

        source_dirs = [
            name for name in FPM_SOURCE_DIRS if (directory / name).is_dir()
        ]
        if not source_dirs:
            raise ProjectLoadError(
                f"No fpm source directories found in {directory}"
            )

        settings = ProjectSettings(
            project=data.get("name", "Fortran Project"),
            version=data.get("version"),
            src_dir=source_dirs,
            preprocess=False,
        )

    return _project_from_settings(settings, directory)


def load_project(path: Union[str, Path], fpm: bool = False) -> Project:
    """Load either an fpm project or a FORD project file."""
    project_path = Path(path).expanduser()

    if fpm or project_path.name == "fpm.toml":
        return load_fpm_project(project_path)

    if project_path.is_dir() and (project_path / "fpm.toml").is_file():
        return load_fpm_project(project_path)

    return load_project_file(project_path)
