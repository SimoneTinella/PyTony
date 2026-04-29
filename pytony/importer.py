from __future__ import annotations

from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
import sys
from types import ModuleType

from .compiler import transpile_source


class PytonyModuleFinder(MetaPathFinder, Loader):
    """Import hook that lets Python import .pytony modules."""

    def find_spec(self, fullname: str, path: list[str] | None, target: ModuleType | None = None) -> ModuleSpec | None:
        search_roots = [Path(entry) for entry in (path or sys.path)]
        module_parts = fullname.split(".")

        for root in search_roots:
            package_dir = root.joinpath(*module_parts)
            package_init = package_dir / "__init__.pytony"
            if package_init.is_file():
                return ModuleSpec(
                    fullname,
                    self,
                    origin=str(package_init),
                    is_package=True,
                )

            module_path = root.joinpath(*module_parts[:-1], f"{module_parts[-1]}.pytony")
            if module_path.is_file():
                return ModuleSpec(
                    fullname,
                    self,
                    origin=str(module_path),
                    is_package=False,
                )

        return None

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        return None

    def exec_module(self, module: ModuleType) -> None:
        if module.__spec__ is None or module.__spec__.origin is None:
            raise ImportError(f"Spec Pytony non valido per il modulo {module.__name__}.")

        source_path = Path(module.__spec__.origin)
        python_source = transpile_source(source_path.read_text(encoding="utf-8"), strict=True)
        code = compile(python_source, str(source_path), "exec")

        module.__file__ = str(source_path)
        if module.__spec__.submodule_search_locations is not None:
            module.__path__ = [str(source_path.parent)]
            module.__package__ = module.__name__
        else:
            module.__package__ = module.__name__.rpartition(".")[0]

        exec(code, module.__dict__)


_FINDER = PytonyModuleFinder()


def install_import_hook() -> None:
    if not any(finder is _FINDER for finder in sys.meta_path):
        sys.meta_path.insert(0, _FINDER)
