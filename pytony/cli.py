from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tokenize

from .compiler import PytonySyntaxError
from .runtime import check_path, format_path, run_path, transpile_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pytony",
        description="Esegui o transpila file Pytony compatibili con Python.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Esegui un file .pytony")
    run_parser.add_argument("path", help="Percorso del file Pytony")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Argomenti per lo script")

    transpile_parser = subparsers.add_parser(
        "transpile",
        help="Mostra il Python generato da un file .pytony",
    )
    transpile_parser.add_argument("path", help="Percorso del file Pytony")

    check_parser = subparsers.add_parser(
        "check",
        help="Valida un file Pytony senza eseguirlo",
    )
    check_parser.add_argument("path", help="Percorso del file Pytony o Python")

    fmt_parser = subparsers.add_parser(
        "fmt",
        help="Formatta un file Pytony o Python nello stile canonico di Pytony",
    )
    fmt_parser.add_argument("path", help="Percorso del file Pytony o Python")
    fmt_parser.add_argument(
        "--check",
        action="store_true",
        help="Verifica se il file e gia formattato senza modificarlo",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_path(Path(args.path), args.args)
        return 0

    if args.command == "transpile":
        sys.stdout.write(transpile_path(Path(args.path)))
        return 0

    if args.command == "check":
        try:
            check_path(Path(args.path))
        except (PytonySyntaxError, SyntaxError) as error:
            sys.stderr.write(f"{error}\n")
            return 1
        sys.stdout.write(f"OK: {args.path}\n")
        return 0

    if args.command == "fmt":
        try:
            _, changed = format_path(Path(args.path), write=not args.check)
        except (PytonySyntaxError, SyntaxError, tokenize.TokenError) as error:
            sys.stderr.write(f"{error}\n")
            return 1
        if args.check:
            if changed:
                sys.stderr.write(f"Needs formatting: {args.path}\n")
                return 1
            sys.stdout.write(f"Already formatted: {args.path}\n")
            return 0
        if changed:
            sys.stdout.write(f"Formatted: {args.path}\n")
        else:
            sys.stdout.write(f"Already formatted: {args.path}\n")
        return 0

    parser.error(f"Comando non supportato: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
