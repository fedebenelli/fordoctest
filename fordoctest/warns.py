"""Custom warning classes
"""

from warnings import warn


class DocumentationWarning(Warning):
    """DocumentationWarning object."""


def warn_module(file, module):
    """Warn about an undocumented module."""
    warn(
        f"Undocumented Module {file.name}::{module.name}", DocumentationWarning
    )


def warn_procedure(file, module, procedure):
    """ """
    warn(
        f"Undocumented Procedure {file.name}::{module.name}::{procedure.name}",
        DocumentationWarning,
    )


def warn_arg(file, module, procedure, arg):
    """ """
    warn(
        (
            f"Undocumented argument {arg}"
            f"{file.name}::{module.name}::{procedure.name}"
        ),
        DocumentationWarning,
    )
