from __future__ import annotations

from pathlib import Path
import sys

from .compiler import transpile_source
from .formatter import format_source
from .importer import install_import_hook


def load_source(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def transpile_path(path: str | Path) -> str:
    source_path = Path(path)
    strict = source_path.suffix == ".pytony"
    return transpile_source(load_source(source_path), strict=strict)


def check_path(path: str | Path) -> str:
    source_path = Path(path)
    python_source = transpile_path(source_path)
    compile(python_source, str(source_path), "exec")
    return python_source


def format_path(path: str | Path, *, write: bool = False) -> tuple[str, bool]:
    source_path = Path(path)
    original_source = load_source(source_path)
    formatted_source = format_source(original_source)
    changed = formatted_source != original_source
    if write and changed:
        source_path.write_text(formatted_source, encoding="utf-8")
    return formatted_source, changed


def run_path(path: str | Path, argv: list[str] | None = None) -> None:
    source_path = Path(path)
    python_source = transpile_path(source_path)
    code = compile(python_source, str(source_path), "exec")
    install_import_hook()

    globals_dict = {
        "__name__": "__main__",
        "__file__": str(source_path),
        "__package__": None,
        "__cached__": None,
    }

    previous_argv = sys.argv[:]
    previous_sys_path = sys.path[:]
    sys.argv = [str(source_path), *(argv or [])]
    module_dir = str(source_path.resolve().parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    try:
        exec(code, globals_dict)
    finally:
        sys.argv = previous_argv
        sys.path[:] = previous_sys_path
