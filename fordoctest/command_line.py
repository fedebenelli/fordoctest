"""Command line interface for fordoctest."""

import argparse
import contextlib
import io
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import ford

from fordoctest import __version__
from fordoctest import console
from fordoctest.core import FordDocumentationTester
from fordoctest.loader import (
    COLOR_MODES,
    ProjectLoadError,
    load_project,
    read_fpm_config,
)

DEFAULT_MAX_MODULES = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fordoctest",
        description="Check that a Fortran project is documented.",
        epilog=(
            "FORD command line options (for example -d/--src_dir, -m and "
            "--config) are forwarded to FORD when a markdown project file "
            "is used."
        ),
    )
    parser.add_argument(
        "project_file",
        nargs="?",
        help="FORD project file or fpm.toml",
    )
    parser.add_argument(
        "--fpm",
        action="store_true",
        help="treat the input as an fpm project",
    )
    parser.add_argument(
        "--max-modules",
        type=int,
        default=None,
        metavar="N",
        help="maximum number of modules per source file (default: 1)",
    )
    parser.add_argument(
        "--check-imperative",
        action="store_true",
        default=None,
        help="warn when procedure docs do not start with an imperative verb",
    )
    parser.add_argument(
        "--color",
        choices=COLOR_MODES,
        default=None,
        help="colourise output: auto, always or never (default: auto)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress progress and success messages",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _parse_max_modules(value: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        raise ValueError("--max-modules requires an integer") from error


def _parse_color(value: str) -> str:
    if value not in COLOR_MODES:
        modes = ", ".join(COLOR_MODES)
        raise ValueError(f"--color must be one of: {modes}")
    return value


def _parse_arguments(
    argv: Sequence[str],
) -> Tuple[Dict[str, object], List[str]]:
    """Split fordoctest options from arguments passed through to FORD."""
    options: Dict[str, object] = {
        "max_modules": None,
        "check_imperative": None,
        "color": None,
        "fpm": False,
        "quiet": False,
    }
    rest: List[str] = []
    index = 0

    while index < len(argv):
        argument = argv[index]

        if argument == "--":
            rest.extend(argv[index + 1 :])
            break
        if argument == "--max-modules":
            if index + 1 >= len(argv):
                raise ValueError("--max-modules requires a value")
            options["max_modules"] = _parse_max_modules(argv[index + 1])
            index += 2
            continue
        if argument.startswith("--max-modules="):
            options["max_modules"] = _parse_max_modules(
                argument.split("=", 1)[1]
            )
            index += 1
            continue
        if argument == "--check-imperative":
            options["check_imperative"] = True
            index += 1
            continue
        if argument == "--color":
            if index + 1 >= len(argv):
                raise ValueError("--color requires a value")
            options["color"] = _parse_color(argv[index + 1])
            index += 2
            continue
        if argument.startswith("--color="):
            options["color"] = _parse_color(argument.split("=", 1)[1])
            index += 1
            continue
        if argument == "--fpm":
            options["fpm"] = True
            index += 1
            continue
        if argument in ("-q", "--quiet"):
            options["quiet"] = True
            index += 1
            continue
        if argument == "--version":
            print(f"fordoctest {__version__}")
            raise SystemExit(0)
        if argument in ("-h", "--help"):
            build_parser().print_help()
            raise SystemExit(0)

        rest.append(argument)
        index += 1

    return options, rest


def _load_with_ford_cli(arguments: Sequence[str], quiet: bool = False):
    """Let FORD parse its own options, preserving ``[ford_flags]``."""
    saved_argv = sys.argv
    ford_argv = [saved_argv[0], *arguments]
    if quiet:
        ford_argv.append("-q")
    sys.argv = ford_argv
    try:
        settings, _ = ford.initialize()
    finally:
        sys.argv = saved_argv

    project = ford.fortran_project.Project(settings)
    if not project.files:
        raise ProjectLoadError("No Fortran source files found")
    return project


def _is_fpm_input(path: str) -> bool:
    candidate = Path(path).expanduser()
    if candidate.name == "fpm.toml":
        return True
    return candidate.is_dir() and (candidate / "fpm.toml").is_file()


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)

    try:
        options, rest = _parse_arguments(arguments)
    except ValueError as error:
        print(f"fordoctest: error: {error}", file=sys.stderr)
        return 2

    if options["max_modules"] is not None and options["max_modules"] < 0:
        print(
            "fordoctest: error: --max-modules must be zero or greater",
            file=sys.stderr,
        )
        return 2

    uses_fpm = bool(options["fpm"])
    if not uses_fpm and len(rest) == 1 and _is_fpm_input(rest[0]):
        uses_fpm = True

    project = None
    config = None
    quiet_output = (
        contextlib.redirect_stdout(io.StringIO())
        if options["quiet"]
        else contextlib.nullcontext()
    )

    try:
        with quiet_output:
            if uses_fpm:
                if len(rest) != 1:
                    print(
                        "fordoctest: error: fpm mode expects exactly one "
                        "fpm.toml path (FORD options are not supported)",
                        file=sys.stderr,
                    )
                    return 2
                project = load_project(rest[0], fpm=True)
                config = read_fpm_config(rest[0])
            else:
                if not rest:
                    print(
                        "fordoctest: error: a FORD project file or "
                        "fpm.toml is required",
                        file=sys.stderr,
                    )
                    return 2
                project = _load_with_ford_cli(
                    rest, quiet=bool(options["quiet"])
                )
    except ProjectLoadError as error:
        print(f"fordoctest: error: {error}", file=sys.stderr)
        return 2
    except SystemExit as error:
        return int(error.code or 0)
    except (OSError, ValueError) as error:
        print(f"fordoctest: error: {error}", file=sys.stderr)
        return 2

    max_modules = options["max_modules"]
    if max_modules is None:
        max_modules = config.max_modules if config else DEFAULT_MAX_MODULES

    check_imperative = options["check_imperative"]
    if check_imperative is None:
        check_imperative = config.check_imperative if config else False

    color_mode = options["color"]
    if color_mode is None:
        color_mode = config.color if config else "auto"

    out = console.stdout(color_mode)
    err = console.stderr(color_mode)

    tester = FordDocumentationTester(
        project,
        max_modules_per_file=int(max_modules),
        check_imperative=bool(check_imperative),
    )
    issues = tester.find_issues()

    if issues:
        for issue in issues:
            print(err.error(issue.message), file=sys.stderr)
        if not options["quiet"]:
            print(
                "\n"
                + err.heading(f"{len(issues)} documentation issue(s) found."),
                file=sys.stderr,
            )
        return 1

    if not options["quiet"]:
        print(out.success("No documentation issues found."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
