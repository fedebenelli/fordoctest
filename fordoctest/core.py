"""ForDocTest.

Fortran documentation tester.
"""

import warnings

import ford

from fordoctest.warns import DocumentationWarning


settings, _ = ford.settings.load_markdown_settings(
    "doc", "ford-front-matter.md"
)
project = ford.fortran_project.Project(settings)

# project.files[0].source_file.path


class ForDocTester:
    """Documentation tester object."""

    def __init__(
        self,
        ford_project_file=None,
        ford_project=None,
        fpm_toml_file=None,
        max_modules_per_file=None,
    ):

        self.project = ford_project
        self.max_modules = max_modules_per_file

    def analyze(self):
        """ """
        for file in project.files:
            print("Analyizing...", file.source_file.path)

            if len(file.modules) > self.max_modules:
                warnings.warn(
                    (
                        "There should not be more than one "
                        "module defined in a file!"
                    ),
                    DocumentationWarning,
                )

            for mod in file.modules:
                for fun in [*mod.functions, *mod.subroutines]:
                    for arg in fun.args:
                        if not arg.doc_list:
                            warnings.warn(
                                (
                                    f"Undocumented variable {arg} "
                                    f"at {mod.name}::{fun.name}"
                                ),
                                DocumentationWarning,
                            )
