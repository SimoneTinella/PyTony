from __future__ import annotations

from pathlib import Path
import sys

from .compiler import transpile_source


def load_source(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def transpile_path(path: str | Path) -> str:
    return transpile_source(load_source(path))


def run_path(path: str | Path, argv: list[str] | None = None) -> None:
    source_path = Path(path)
    python_source = transpile_path(source_path)
    code = compile(python_source, str(source_path), "exec")

    globals_dict = {
        "__name__": "__main__",
        "__file__": str(source_path),
        "__package__": None,
        "__cached__": None,
    }

    previous_argv = sys.argv[:]
    sys.argv = [str(source_path), *(argv or [])]
    try:
        exec(code, globals_dict)
    finally:
        sys.argv = previous_argv
