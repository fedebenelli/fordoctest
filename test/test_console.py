import io

from fordoctest import console


class Stream(io.StringIO):
    def __init__(self, tty: bool) -> None:
        super().__init__()
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


def test_color_modes_override_terminal_detection():
    assert console.color_enabled("always", Stream(False))
    assert not console.color_enabled("never", Stream(True))


def test_color_auto_uses_isatty():
    assert console.color_enabled("auto", Stream(True))
    assert not console.color_enabled("auto", Stream(False))


def test_color_auto_respects_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    assert not console.color_enabled("auto", Stream(True))


def test_color_auto_respects_dumb_terminal(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "dumb")

    assert not console.color_enabled("auto", Stream(True))


def test_console_styles_output():
    styled = console.Console(True)

    assert styled.error("bad").startswith("\033[31m")
    assert styled.heading("summary").startswith("\033[1m\033[33m")
    assert styled.success("good").startswith("\033[32m")
    assert styled.error("bad").endswith("\033[0m")


def test_console_without_color_is_plain():
    plain = console.Console(False)

    assert plain.error("bad") == "bad"
    assert plain.heading("summary") == "summary"
    assert plain.success("good") == "good"
