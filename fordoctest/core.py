"""ForDocTest.

Fortran documentation tester.
"""

import warnings

import ford

from fordoctest.warns import (
    DocumentationWarning,
    warn_module,
    warn_procedure,
    warn_arg
)

from abc import ABC, abstractmethod


class DocumentationTester(ABC):

    @abstractmethod
    def analyze(self):
        raise NotImplementedError


class FordDocumentationTester(DocumentationTester):
    """Documentation tester object.

    Test that all the modules and procedures are fully documented.

    Upon initializatoin it uses `ford`'s argument parser to obtain
    all the relevant information.
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

            self.analyize_procedures(
                file, procedures=[*file.functions, *file.subroutines], mod=None
            )

            # Limit the ammount of modules per file
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
                    warn_module(file, mod)

                self.analyize_procedures(
                    file, [*mod.functions, *mod.subroutines], mod
                )

    def analyize_procedures(self, file, procedures, mod=None):
        """Test procedures documentation."""

        for procedure in procedures:
            if not procedure.doc_list:
                warn_procedure(file, mod, procedure)

            for arg in procedure.args:
                if not arg.doc_list:
                    warn_arg(file, mod, procedure, arg)
