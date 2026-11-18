"""Load FORD project models without parsing ``sys.argv``."""

from pathlib import Path
from typing import Optional, Union

import ford
from ford.fortran_project import Project
from ford.settings import ProjectSettings

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

FPM_SOURCE_DIRS = ("src", "app", "test", "example", "examples", "benchmark")


class ProjectLoadError(RuntimeError):
    """Raised when a project file cannot be loaded."""


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
    project_path = Path(path).expanduser()
    if project_path.is_dir():
        directory = project_path
        fpm_file = directory / "fpm.toml"
    else:
        fpm_file = project_path
        directory = fpm_file.parent

    if not fpm_file.is_file():
        raise ProjectLoadError(f"fpm.toml not found: {fpm_file}")

    settings: Optional[ProjectSettings] = ford.settings.load_toml_settings(
        directory
    )

    if settings is None:
        try:
            data = tomllib.loads(fpm_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise ProjectLoadError(
                f"Could not read {fpm_file}: {error}"
            ) from error

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
