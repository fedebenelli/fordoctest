"""ForDocTest.

Fortran documentation tester.
"""

import warnings

import ford

from ford.fortran_project import Project

from fordoctest.warns import (
    DocumentationWarning,
    ProcedureDocumentationWarning,
)

from abc import ABC, abstractmethod
import os


class DocumentationTester(ABC):

    @abstractmethod
    def analyze(self):
        raise NotImplementedError


class FordDocumentationTester(DocumentationTester):
    """Documentation tester object.

    Test that all the modules and procedures are fully documented.

    Once initialized uses `ford`'s argument parser
    """

    def __init__(
        self,
        max_modules_per_file=1,
    ):

        self.max_modules = max_modules_per_file

        proj_data, proj_docs = ford.initialize()
        self.project = ford.fortran_project.Project(proj_data)

    def analyze(self):
        """Search for undocumented modules and procedures."""

        for file in self.project.files:
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
                if not mod.doc_list:
                    warnings.warn("Undocumented module", DocumentationWarning)

                for procedure in [*mod.functions, *mod.subroutines]:
                    if not procedure.doc_list:
                        warnings.warn("", ProcedureDocumentationWarning)

                    for arg in procedure.args:
                        if not arg.doc_list:
                            warnings.warn(
                                (
                                    f"Undocumented variable {arg} "
                                    f"at {mod.name}::{procedure.name}"
                                ),
                                DocumentationWarning,
                            )
