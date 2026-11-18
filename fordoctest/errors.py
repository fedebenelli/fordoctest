"""Documentation issues and the public exception type."""

from dataclasses import dataclass
from typing import Iterable, Sequence, Union


@dataclass(frozen=True)
class DocumentationIssue:
    """A single missing or malformed piece of documentation."""

    kind: str
    location: str
    message: str

    def __str__(self) -> str:
        return self.message


class DocumentationError(ValueError):
    """Raised when a project contains documentation issues."""

    def __init__(
        self, issues: Union[str, Sequence[DocumentationIssue]]
    ) -> None:
        if isinstance(issues, str):
            issues = [issues]
        self.issues = list(issues)
        super().__init__("\n".join(str(issue) for issue in self.issues))


def undocumented(
    kind: str,
    file,
    entity: str,
    parents: Iterable[str] = (),
) -> DocumentationIssue:
    """Build an issue for an undocumented entity."""
    location = "::".join([file.name, *parents, entity])
    return DocumentationIssue(
        kind=kind,
        location=location,
        message=f"Undocumented {kind} {location}",
    )


def undocumented_argument(
    file,
    argument: str,
    parents: Iterable[str] = (),
) -> DocumentationIssue:
    """Build an issue for an undocumented procedure argument."""
    location = "::".join([file.name, *parents])
    return DocumentationIssue(
        kind="Argument",
        location=location,
        message=f"Undocumented argument '{argument}' in {location}",
    )


def non_imperative(
    file,
    procedure: str,
    word: str,
    parents: Iterable[str] = (),
) -> DocumentationIssue:
    """Build an issue for documentation that is not imperative."""
    location = "::".join([file.name, *parents, procedure])
    return DocumentationIssue(
        kind="Documentation style",
        location=location,
        message=(
            f"Procedure {location} should start with an imperative verb; "
            f"found '{word}'"
        ),
    )
