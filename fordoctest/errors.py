"""Custom Error messages.
"""


class DocumentationError(ValueError):
    """DocumentationError object."""


def raise_module(file, module):
    """raise about an undocumented module."""
    raise DocumentationError(
        f"Undocumented Module {file.name}::{module.name}",
    )


def raise_iso_procedure(file, procedure):
    """ """
    raise DocumentationError(
        f"Undocumented Procedure {file.name}::{procedure.name}",
    )


def raise_mod_procedure(file, module, procedure):
    """ """
    raise DocumentationError(
        f"Undocumented Procedure {file.name}::{module.name}::{procedure.name}",
    )


def raise_iso_arg(file, procedure, arg):
    """ """
    raise DocumentationError(
        (
            f"Undocumented argument {arg.name}"
            f"@{file.name}::{procedure.name}"
        ),
    )


def raise_mod_arg(file, module, procedure, arg):
    """ """
    raise DocumentationError(
        (
            f"Undocumented argument {arg.name}"
            f"@{file.name}::{module.name}::{procedure.name}"
        ),
    )


def raise_prog(file, program):
    """ """
    raise DocumentationError(
        (
            f"Undocumented program {program.name}"
            f"@{file.name}::{program.name}"
        ),
    )
