"""Custom warning classes
"""

from warnings import warn


class DocumentationWarning(Warning):
    ...


class ProcedureDocumentationWarning(DocumentationWarning):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def warn_module(file, module):
    warn(f"Undocumented Module {file}::{module}")


def warn_procedure(file, module, procedure):
    warn(f"Undocumented Procedure {file}::{module}::{procedure}")
