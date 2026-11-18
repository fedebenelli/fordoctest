import shutil
from pathlib import Path

import pytest

PROJECT_HEADER = """\
project: test_project
src_dir: src
preprocess: false
docmark: !
predocmark: >
"""

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def make_project(tmp_path):
    """Copy Fortran sources into a tiny FORD project."""

    def _make(
        source_files,
        header: str = PROJECT_HEADER,
        source_dir: str = "src",
    ) -> Path:
        if isinstance(source_files, (str, Path)):
            source_files = [source_files]

        directory = tmp_path / source_dir
        directory.mkdir(parents=True, exist_ok=True)
        for source_file in source_files:
            source_path = Path(source_file)
            if not source_path.is_absolute():
                source_path = FIXTURES / source_path
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
            shutil.copyfile(source_path, directory / source_path.name)

        project_file = tmp_path / "doc.md"
        project_file.write_text(header, encoding="utf-8")
        return project_file

    return _make
