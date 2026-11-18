from fordoctest import (
    DocumentationError,
    DocumentationIssue,
    FordDocumentationTester,
)
from fordoctest.core import _first_documentation_word


def analyzer(make_project, source_file, **kwargs):
    project_file = make_project(source_file)
    return FordDocumentationTester.from_project_file(project_file, **kwargs)


def kinds(issues):
    return [issue.kind for issue in issues]


def test_fully_documented_project_has_no_issues(make_project):
    tester = analyzer(make_project, "documented_project.f90")

    assert tester.find_issues() == []
    tester.analyze()


def test_documented_module_has_no_issues(make_project):
    tester = analyzer(make_project, "documented_module.f90")

    assert tester.find_issues() == []


def test_undocumented_module(make_project):
    issues = analyzer(make_project, "undocumented_module.f90").find_issues()

    assert kinds(issues) == ["Module"]
    assert "m" in issues[0].message


def test_undocumented_program(make_project):
    issues = analyzer(make_project, "undocumented_program.f90").find_issues()

    assert kinds(issues) == ["Program"]


def test_undocumented_isolated_procedure_and_argument(make_project):
    issues = analyzer(
        make_project, "undocumented_isolated_procedure.f90"
    ).find_issues()

    assert kinds(issues) == ["Procedure", "Argument"]


def test_undocumented_module_procedure_and_argument(make_project):
    issues = analyzer(
        make_project, "undocumented_module_procedure.f90"
    ).find_issues()

    assert kinds(issues) == ["Procedure", "Argument"]


def test_undocumented_derived_type(make_project):
    issues = analyzer(
        make_project, "undocumented_derived_type.f90"
    ).find_issues()

    assert kinds(issues) == [
        "Derived type",
        "Type component",
        "Type-bound procedure",
    ]


def test_undocumented_type_component_only(make_project):
    issues = analyzer(
        make_project, "undocumented_type_component.f90"
    ).find_issues()

    assert kinds(issues) == ["Type component"]


def test_undocumented_interface(make_project):
    issues = analyzer(make_project, "undocumented_interface.f90").find_issues()

    assert kinds(issues) == ["Interface"]


def test_undocumented_interface_argument(make_project):
    issues = analyzer(
        make_project, "undocumented_interface_argument.f90"
    ).find_issues()

    assert kinds(issues) == ["Argument"]


def test_undocumented_submodule(make_project):
    issues = analyzer(make_project, "undocumented_submodule.f90").find_issues()

    assert kinds(issues) == ["Submodule", "Procedure"]


def test_module_count_limit(make_project):
    tester = analyzer(make_project, "multiple_modules.f90")
    issues = tester.find_issues()

    assert kinds(issues) == ["Module count"]
    assert "2 modules" in issues[0].message

    relaxed = analyzer(
        make_project, "multiple_modules.f90", max_modules_per_file=2
    )
    assert relaxed.find_issues() == []


def test_module_count_can_be_disabled(make_project):
    tester = analyzer(
        make_project,
        "multiple_modules.f90",
        max_modules_per_file=None,
    )

    assert tester.find_issues() == []


def test_analyze_aggregates_all_issues(make_project):
    tester = analyzer(make_project, "undocumented_procedures.f90")

    try:
        tester.analyze()
    except DocumentationError as error:
        assert len(error.issues) == 2
        assert "a" in str(error)
        assert "b" in str(error)
    else:  # pragma: no cover - makes the test failure obvious
        raise AssertionError("DocumentationError was not raised")


def test_imperative_check_flags_third_person(make_project):
    tester = analyzer(
        make_project,
        "non_imperative.f90",
        check_imperative=True,
    )
    issues = tester.find_issues()

    assert kinds(issues) == ["Documentation style"]
    assert "computes" in issues[0].message


def test_imperative_check_accepts_imperative(make_project):
    tester = analyzer(
        make_project,
        "imperative.f90",
        check_imperative=True,
    )

    assert tester.find_issues() == []


def test_imperative_check_is_opt_in(make_project):
    tester = analyzer(make_project, "non_imperative.f90")

    assert tester.find_issues() == []


def test_first_documentation_word_handles_empty_and_markup():
    assert _first_documentation_word([]) == ""
    assert _first_documentation_word([""]) == ""
    assert _first_documentation_word(["## 123"]) == ""
    assert _first_documentation_word(["## `Compute` now"]) == "compute"


def test_doxygen_style_documentation(make_project):
    tester = analyzer(make_project, "doxygen_documented.f90")

    assert tester.find_issues() == []


def test_doxygen_brief_metadata_counts_as_documentation(make_project):
    tester = analyzer(make_project, "doxygen_brief.f90")

    assert tester.find_issues() == []


def test_doxygen_param_is_required_for_arguments(make_project):
    issues = analyzer(make_project, "doxygen_missing_param.f90").find_issues()

    assert kinds(issues) == ["Argument"]
    assert "'x'" in issues[0].message


def test_multiple_fixture_files_are_all_analyzed(make_project):
    tester = analyzer(
        make_project,
        ["documented_module.f90", "undocumented_program.f90"],
    )

    issues = tester.find_issues()
    assert kinds(issues) == ["Program"]
    assert "::main" in issues[0].message


def test_documentation_error_accepts_strings_and_issues():
    string_error = DocumentationError("plain message")
    assert string_error.issues == ["plain message"]
    assert str(string_error) == "plain message"

    issue = DocumentationIssue(
        kind="Module",
        location="a.f90::m",
        message="Undocumented Module a.f90::m",
    )
    issue_error = DocumentationError([issue])
    assert str(issue_error) == "Undocumented Module a.f90::m"
