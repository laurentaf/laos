"""Tests for lacouncil.__main__._ensure_utf8_stdout() (LACOUNCIL b43ca63d C-B2).

Validates that the reconfigure call:
- Forces UTF-8 on a cp1252 TextIOWrapper (the original bug).
- Is no-op on already-UTF-8 streams.
- Does not raise on streams without reconfigure() (colorama, IPython, frozen).
"""
from __future__ import annotations

import io
import sys

import pytest

from lacouncil.__main__ import _ensure_utf8_stdout


def test_reconfigure_guards_cp1252():
    """The original bug: stdout wrapped as cp1252 should be upgraded to UTF-8."""
    buf = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    original_encoding = buf.encoding
    assert original_encoding == "cp1252", "fixture should start as cp1252"

    real_stdout = sys.stdout
    sys.stdout = buf
    try:
        _ensure_utf8_stdout()
    finally:
        sys.stdout = real_stdout

    assert buf.encoding == "utf-8", (
        f"_ensure_utf8_stdout() should upgrade cp1252 to UTF-8, got {buf.encoding}"
    )


def test_reconfigure_is_noop_on_utf8():
    """On already-UTF-8 environments (Linux, macOS, modern Windows TTY), the call
    should be a no-op or at worst a safe re-encode."""
    buf = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")

    real_stdout = sys.stdout
    sys.stdout = buf
    try:
        _ensure_utf8_stdout()
    finally:
        sys.stdout = real_stdout

    assert buf.encoding == "utf-8"


def test_reconfigure_handles_missing_attribute(monkeypatch):
    """If sys.stdout lacks reconfigure (colorama wrap, IPython, frozen, etc.),
    the guard must swallow the AttributeError."""
    class FakeStreamNoReconfigure:
        encoding = "ascii"

    monkeypatch.setattr(sys, "stdout", FakeStreamNoReconfigure())
    _ensure_utf8_stdout()  # must not raise AttributeError


def test_reconfigure_handles_value_error_on_closed_stream(monkeypatch):
    """If sys.stdout is a closed stream, reconfigure raises ValueError.
    Guard must swallow it."""
    class FakeClosedStream:
        encoding = "utf-8"
        def reconfigure(self, **kwargs):
            raise ValueError("I/O operation on closed file")

    monkeypatch.setattr(sys, "stdout", FakeClosedStream())
    _ensure_utf8_stdout()  # must not raise


def test_module_import_is_safe():
    """Importing lacouncil.__main__ must not crash, even on weird stdout.

    This was the original symptom: `uv run lacouncil --help` or any
    lacouncil command crashed at import time with UnicodeEncodeError or
    AttributeError on Windows console.
    """
    import lacouncil.__main__  # noqa: F401
    assert hasattr(lacouncil.__main__, "_ensure_utf8_stdout")
