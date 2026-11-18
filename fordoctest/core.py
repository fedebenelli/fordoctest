"""ForDocTest.

Fortran documentation tester.
"""

import re
from abc import ABC, abstractmethod
from typing import Iterable, List, Optional

from fordoctest.errors import (
    DocumentationError,
    DocumentationIssue,
    non_imperative,
    undocumented,
    undocumented_argument,
)
from fordoctest.loader import load_project, read_fpm_config

# Conservative heuristic: only flag first words that are clearly not
# imperative. Anything else is left alone to avoid false positives.
NON_IMPERATIVE_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "this",
        "that",
        "these",
        "those",
        "it",
        "we",
        "you",
        "they",
        "he",
        "she",
        "is",
        "are",
        "was",
        "were",
        "will",
        "would",
        "can",
        "could",
        "should",
        "may",
        "might",
        "must",
        "has",
        "have",
        "had",
        "does",
        "computes",
        "calculates",
        "performs",
        "returns",
        "gives",
        "gets",
        "sets",
        "creates",
        "checks",
        "tests",
        "defines",
        "describes",
        "provides",
        "contains",
        "uses",
    }
)


class DocumentationTester(ABC):
    """Base class for documentation testers."""

    @abstractmethod
    def find_issues(self) -> List[DocumentationIssue]:
        """Return every documentation issue found in the project."""
        raise NotImplementedError

    def analyze(self) -> None:
        """Raise if the project contains any documentation issue."""
        issues = self.find_issues()
        if issues:
            raise DocumentationError(issues)


class FordDocumentationTester(DocumentationTester):
    """Documentation tester backed by a parsed FORD project.

    Use :meth:`from_project_file` or :meth:`from_fpm` to build an instance.
    """

    def __init__(
        self,
        project,
        max_modules_per_file: int = 1,
        check_imperative: bool = False,
    ) -> None:
        self.project = project
        self.max_modules = max_modules_per_file
        self.check_imperative = check_imperative

    @classmethod
    def from_project_file(
        cls,
        path,
        max_modules_per_file: int = 1,
        check_imperative: bool = False,
    ) -> "FordDocumentationTester":
        """Build a tester from a FORD markdown project file."""
        return cls(
            load_project(path),
            max_modules_per_file=max_modules_per_file,
            check_imperative=check_imperative,
        )

    @classmethod
    def from_fpm(
        cls,
        path,
        max_modules_per_file: Optional[int] = None,
        check_imperative: Optional[bool] = None,
    ) -> "FordDocumentationTester":
        """Build a tester from an ``fpm.toml`` file or directory.

        Explicit arguments win; anything left as ``None`` falls back to
        ``[extra.fordoctest]`` in the fpm manifest and then to the defaults.
        """
        config = read_fpm_config(path)
        if max_modules_per_file is None:
            max_modules_per_file = config.max_modules
        if check_imperative is None:
            check_imperative = config.check_imperative
        return cls(
            load_project(path, fpm=True),
            max_modules_per_file=max_modules_per_file,
            check_imperative=check_imperative,
        )

    def find_issues(self) -> List[DocumentationIssue]:
        """Search for undocumented entities and style problems."""
        issues: List[DocumentationIssue] = []
        seen = set()

        for file in self.project.files:
            self._check_module_count(file, issues, seen)

            for module in file.modules:
                self._check_unit(
                    file,
                    module,
                    "Module",
                    (),
                    issues,
                    seen,
                )

            for submodule in file.submodules:
                self._check_unit(
                    file,
                    submodule,
                    "Submodule",
                    (),
                    issues,
                    seen,
                )

            for program in file.programs:
                self._check_unit(
                    file,
                    program,
                    "Program",
                    (),
                    issues,
                    seen,
                )

            self._check_procedures(
                file,
                [*file.functions, *file.subroutines],
                (),
                issues,
                seen,
            )

        return issues

    def _check_module_count(self, file, issues, seen) -> None:
        if self.max_modules is None:
            return
        if len(file.modules) <= self.max_modules:
            return

        issue = DocumentationIssue(
            kind="Module count",
            location=file.name,
            message=(
                f"{file.name} defines {len(file.modules)} modules; "
                f"at most {self.max_modules} allowed"
            ),
        )
        self._add(issues, seen, issue, ("module-count", file.path))

    def _check_unit(
        self,
        file,
        unit,
        kind: str,
        parents: Iterable[str],
        issues,
        seen,
    ) -> None:
        key = ("unit", id(unit))
        if key in seen:
            return
        seen.add(key)

        parents = tuple(parents)
        if not _is_documented(unit):
            self._add(
                issues,
                seen,
                undocumented(kind, file, unit.name, parents),
                ("undocumented", key),
            )

        unit_parents = (*parents, unit.name)
        self._check_types(file, unit, unit_parents, issues, seen)
        self._check_interfaces(file, unit, unit_parents, issues, seen)
        self._check_procedures(
            file,
            [*unit.functions, *unit.subroutines],
            unit_parents,
            issues,
            seen,
        )

        for procedure in getattr(unit, "modprocedures", []):
            self._check_procedures(
                file,
                [procedure],
                unit_parents,
                issues,
                seen,
            )

    def _check_types(
        self,
        file,
        container,
        parents,
        issues,
        seen,
    ) -> None:
        for derived_type in getattr(container, "types", []):
            key = ("type", id(derived_type))
            if key in seen:
                continue
            seen.add(key)

            if not _is_documented(derived_type):
                self._add(
                    issues,
                    seen,
                    undocumented(
                        "Derived type", file, derived_type.name, parents
                    ),
                    ("undocumented", key),
                )

            type_parents = (*parents, derived_type.name)
            for component in derived_type.variables:
                if _is_documented(component):
                    continue
                self._add(
                    issues,
                    seen,
                    undocumented(
                        "Type component", file, component.name, type_parents
                    ),
                    ("undocumented", "component", id(component)),
                )

            for procedure in derived_type.boundprocs:
                if _is_documented(procedure):
                    continue
                self._add(
                    issues,
                    seen,
                    undocumented(
                        "Type-bound procedure",
                        file,
                        procedure.name,
                        type_parents,
                    ),
                    ("undocumented", "boundproc", id(procedure)),
                )

    def _check_interfaces(
        self,
        file,
        container,
        parents,
        issues,
        seen,
    ) -> None:
        interfaces = [
            *getattr(container, "interfaces", []),
            *getattr(container, "absinterfaces", []),
        ]
        for interface in interfaces:
            key = ("interface", id(interface))
            if key in seen:
                continue
            seen.add(key)

            name = interface.name or "<anonymous>"
            if not _is_documented(interface):
                self._add(
                    issues,
                    seen,
                    undocumented("Interface", file, name, parents),
                    ("undocumented", key),
                )

            procedures = []
            procedure = getattr(interface, "procedure", None)
            if procedure is not None:
                procedures.append(procedure)
            procedures.extend(getattr(interface, "functions", []) or [])
            procedures.extend(getattr(interface, "subroutines", []) or [])

            for procedure in procedures:
                procedure_parents = (*parents, name)
                for argument in getattr(procedure, "args", []):
                    if _is_documented(argument):
                        continue
                    self._add(
                        issues,
                        seen,
                        undocumented_argument(
                            file,
                            argument.name,
                            procedure_parents,
                        ),
                        ("undocumented", "argument", id(argument)),
                    )

    def _check_procedures(
        self,
        file,
        procedures,
        parents,
        issues,
        seen,
    ) -> None:
        for procedure in procedures:
            key = ("procedure", id(procedure))
            if key in seen:
                continue
            seen.add(key)

            if not _is_documented(procedure):
                self._add(
                    issues,
                    seen,
                    undocumented("Procedure", file, procedure.name, parents),
                    ("undocumented", key),
                )
            elif self.check_imperative:
                word = _first_documentation_word(procedure.doc_list)
                if word in NON_IMPERATIVE_WORDS:
                    self._add(
                        issues,
                        seen,
                        non_imperative(
                            file,
                            procedure.name,
                            word,
                            parents,
                        ),
                        ("style", key),
                    )

            procedure_parents = (*parents, procedure.name)
            for argument in getattr(procedure, "args", []):
                if _is_documented(argument):
                    continue
                self._add(
                    issues,
                    seen,
                    undocumented_argument(
                        file,
                        argument.name,
                        procedure_parents,
                    ),
                    ("undocumented", "argument", id(argument)),
                )

    @staticmethod
    def _add(issues, seen, issue, key) -> None:
        if key in seen:
            return
        seen.add(key)
        issues.append(issue)


def _is_documented(entity) -> bool:
    """Return whether an entity carries documentation.

    Doxygen ``@brief`` metadata is moved into ``meta.summary`` by FORD,
    leaving ``doc_list`` empty, so both places must be considered.
    """
    if entity.doc_list:
        return True
    return bool(getattr(getattr(entity, "meta", None), "summary", None))


def _first_documentation_word(doc_list) -> str:
    text = " ".join(doc_list).strip()
    if not text:
        return ""
    text = text.lstrip("#*-_` ")
    match = re.search(r"[A-Za-z][A-Za-z'-]*", text)
    if match is None:
        return ""
    return match.group(0).lower()
