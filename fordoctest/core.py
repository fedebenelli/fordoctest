"""ForDocTest.

Fortran documentation tester.
"""

import ford

from fordoctest.errors import (
    DocumentationError,
    raise_module,
    raise_iso_procedure,
    raise_iso_arg,
    raise_mod_procedure,
    raise_mod_arg,
    raise_prog
)

from abc import ABC, abstractmethod


class DocumentationTester(ABC):

    @abstractmethod
    def analyze(self):
        raise NotImplementedError


class FordDocumentationTester(DocumentationTester):
    """Documentation tester object.

    Test that all the modules and procedures are fully documented.

    Upon initialization it uses `ford`'s argument parser to obtain
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
            print("Analyzing...", file.source_file.path)

            self.analyize_procedures(
                file, procedures=[*file.functions, *file.subroutines], mod=None
            )

            for prog in file.programs:
                if not prog.doc_list:
                    raise_prog(file, prog)
                
                self.analyize_procedures(
                    file, [*prog.functions, *prog.subroutines], mod=prog
                )

            # Limit the ammount of modules per file
            if len(file.modules) > self.max_modules:
                raise DocumentationError(
                    (
                        "There should not be more than one "
                        "module defined in a file!"
                    ),
                )

            for mod in file.modules:
                if not mod.doc_list:
                    raise_module(file, mod)

                self.analyize_procedures(
                    file, [*mod.functions, *mod.subroutines], mod
                )

    def analyize_procedures(self, file, procedures, mod=None):
        """Test procedures documentation."""

        for procedure in procedures:
            if not procedure.doc_list:
                if mod:
                    raise_mod_procedure(file, mod, procedure)
                else:
                    raise_iso_procedure(file, procedure)


            for arg in procedure.args:
                if not arg.doc_list:
                    if mod:
                        raise_mod_arg(file, mod, procedure, arg)
                    else:
                        raise_iso_arg(file, procedure, arg)
