from __future__ import annotations

from dataclasses import dataclass
from .compiler import transpile_source
from .formatter import format_source


@dataclass(frozen=True, order=True)
class LintIssue:
    code: str
    message: str
    line: int
    column: int


def lint_source(source: str, *, strict: bool = False) -> list[LintIssue]:
    transpiled_source = transpile_source(source, strict=strict)
    compile(transpiled_source, "<pytony-lint>", "exec")

    issues: list[LintIssue] = []
    lines = source.splitlines(keepends=True)
    blank_run = 0

    for line_number, raw_line in enumerate(lines, start=1):
        line_without_newline = raw_line.rstrip("\r\n")
        indent = line_without_newline[:len(line_without_newline) - len(line_without_newline.lstrip(" \t"))]

        tab_index = indent.find("\t")
        if tab_index >= 0:
            issues.append(
                LintIssue(
                    "PYL001",
                    "Indentazione con tab: usa 4 spazi nello stile canonico di Pytony.",
                    line_number,
                    tab_index + 1,
                )
            )

        stripped_right = line_without_newline.rstrip(" \t")
        if stripped_right != line_without_newline:
            issues.append(
                LintIssue(
                    "PYL002",
                    "Spazi o tab finali non necessari.",
                    line_number,
                    len(stripped_right) + 1,
                )
            )

        if line_without_newline.strip() == "":
            blank_run += 1
            if blank_run > 1:
                issues.append(
                    LintIssue(
                        "PYL003",
                        "Troppi separatori verticali consecutivi: lascia al massimo una riga vuota.",
                        line_number,
                        1,
                    )
                )
        else:
            blank_run = 0

    if source and not source.endswith("\n"):
        issues.append(
            LintIssue(
                "PYL004",
                "Il file dovrebbe terminare con una newline finale.",
                len(lines),
                len(lines[-1].rstrip("\r\n")) + 1,
            )
        )

    if format_source(source) != source:
        issues.append(
            LintIssue(
                "PYL005",
                "Il file non segue il formato canonico: esegui `pytony fmt`.",
                1,
                1,
            )
        )

    return sorted(issues)


def format_lint_issue(path: str, issue: LintIssue) -> str:
    return f"{path}:{issue.line}:{issue.column}: [{issue.code}] {issue.message}"
