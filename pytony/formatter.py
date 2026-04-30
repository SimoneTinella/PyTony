from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
import token
import tokenize


INDENT = "    "
OPENERS = {"(", "[", "{"}
CLOSERS = {")", "]", "}"}
BINARY_OPERATORS = {
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "//=",
    "**=",
    "&=",
    "|=",
    "^=",
    ">>=",
    "<<=",
    ":=",
    "==",
    "!=",
    "<=",
    ">=",
    "<",
    ">",
    "+",
    "-",
    "*",
    "/",
    "%",
    "//",
    "**",
    "&",
    "|",
    "^",
    ">>",
    "<<",
    "->",
}
KEYWORDS_WITH_SPACE_BEFORE_PAREN = {
    "e_se",
    "e_se_invece",
    "mentre_riposi",
    "gira_il_circo",
    "interludio",
    "bridge",
    "ma_ehi",
}
PREFIX_OPERATOR_CONTEXT = {
    "(",
    "[",
    "{",
    ",",
    ":",
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "->",
}
PREFIX_OPERATOR_KEYWORDS = {
    "restero",
    "scoppia",
    "te_l_ho_detto",
    "gira_il_circo",
    "nell_alta_marea",
    "e_se",
    "e_se_invece",
    "mentre_riposi",
    "come_monet",
    "colpo_di_scena",
}


@dataclass
class _LogicalLine:
    start_line: int
    end_line: int
    indent_level: int
    code_tokens: list[tokenize.TokenInfo]
    comment: str | None = None
    comment_only: bool = False


def format_source(source: str) -> str:
    lines = source.splitlines()
    logical_lines = _collect_logical_lines(source)
    if not logical_lines:
        return ""

    rendered: list[str] = []
    previous_end = 0

    for line in logical_lines:
        for original_index in range(previous_end + 1, line.start_line):
            if lines[original_index - 1].strip() == "":
                rendered.append("")
        rendered.append(_render_logical_line(line))
        previous_end = line.end_line

    if source.endswith("\n"):
        return "\n".join(rendered) + "\n"
    return "\n".join(rendered)


def _collect_logical_lines(source: str) -> list[_LogicalLine]:
    tokens = tokenize.generate_tokens(StringIO(source).readline)
    logical_lines: list[_LogicalLine] = []

    indent_level = 0
    bracket_depth = 0
    current_tokens: list[tokenize.TokenInfo] = []
    current_comment: str | None = None
    current_comment_only = False
    current_start_line: int | None = None
    current_end_line: int | None = None
    current_indent_level = 0

    def finalize() -> None:
        nonlocal current_tokens
        nonlocal current_comment
        nonlocal current_comment_only
        nonlocal current_start_line
        nonlocal current_end_line
        nonlocal current_indent_level
        if current_start_line is None:
            return
        logical_lines.append(
            _LogicalLine(
                start_line=current_start_line,
                end_line=current_end_line or current_start_line,
                indent_level=current_indent_level,
                code_tokens=current_tokens,
                comment=current_comment,
                comment_only=current_comment_only,
            )
        )
        current_tokens = []
        current_comment = None
        current_comment_only = False
        current_start_line = None
        current_end_line = None
        current_indent_level = indent_level

    for current in tokens:
        if current.type == tokenize.INDENT:
            indent_level += 1
            continue
        if current.type == tokenize.DEDENT:
            indent_level = max(indent_level - 1, 0)
            continue
        if current.type == tokenize.ENDMARKER:
            finalize()
            break
        if current.type == tokenize.NL:
            if bracket_depth == 0 and (current_tokens or current_comment is not None):
                finalize()
            continue
        if current.type == tokenize.NEWLINE:
            finalize()
            continue
        if current.type == tokenize.COMMENT:
            if current_start_line is None:
                current_start_line = current.start[0]
                current_indent_level = current.start[1] // len(INDENT)
                current_comment_only = True
            current_end_line = current.end[0]
            current_comment = current.string.rstrip()
            continue

        if current_start_line is None:
            current_start_line = current.start[0]
            current_indent_level = indent_level
        current_end_line = current.end[0]
        current_comment_only = False
        current_tokens.append(current)

        if current.type == token.OP:
            if current.string in OPENERS:
                bracket_depth += 1
            elif current.string in CLOSERS:
                bracket_depth = max(bracket_depth - 1, 0)

    return logical_lines


def _render_logical_line(line: _LogicalLine) -> str:
    indent = INDENT * line.indent_level
    if line.comment_only:
        comment = (line.comment or "").lstrip()
        return f"{indent}{comment}".rstrip()

    rendered = _render_code_tokens(line.code_tokens)
    if line.comment:
        return f"{indent}{rendered}  {line.comment.lstrip()}".rstrip()
    return f"{indent}{rendered}".rstrip()


def _render_code_tokens(tokens: list[tokenize.TokenInfo]) -> str:
    pieces: list[str] = []
    before_previous: tokenize.TokenInfo | None = None
    previous: tokenize.TokenInfo | None = None
    nesting: list[str] = []

    for current in tokens:
        if pieces and _needs_space(before_previous, previous, current, tuple(nesting)):
            pieces.append(" ")
        pieces.append(current.string)
        if current.type == token.OP:
            if current.string in OPENERS:
                nesting.append(current.string)
            elif current.string in CLOSERS and nesting:
                nesting.pop()
        before_previous = previous
        previous = current

    return "".join(pieces)


def _needs_space(
    before_previous: tokenize.TokenInfo | None,
    previous: tokenize.TokenInfo | None,
    current: tokenize.TokenInfo,
    nesting: tuple[str, ...],
) -> bool:
    if previous is None:
        return False

    if current.string in CLOSERS | {",", ":", ";", "."}:
        return False
    if previous.string in OPENERS | {"."}:
        return False
    if previous.string == ",":
        return current.string not in CLOSERS
    if current.string == "(":
        if previous.type in {token.NAME, token.NUMBER, token.STRING} and previous.string not in KEYWORDS_WITH_SPACE_BEFORE_PAREN:
            return False
        if previous.string in CLOSERS:
            return False
        return True
    if current.string == "[":
        if previous.type in {token.NAME, token.NUMBER, token.STRING} or previous.string in CLOSERS:
            return False
        return previous.string not in OPENERS | {"."}
    if current.string == "{":
        return previous.string not in OPENERS | {"."}
    if previous.string == ":":
        return current.string not in CLOSERS | {","}
    if current.string == "=" and nesting and nesting[-1] == "(" and previous.type == token.NAME:
        return False
    if previous.string == "=" and nesting and nesting[-1] == "(" and before_previous and before_previous.type == token.NAME:
        return False

    if current.type == token.OP and current.string in BINARY_OPERATORS:
        if _is_prefix_operator(before_previous, current):
            return False
        return True
    if previous.type == token.OP and previous.string in BINARY_OPERATORS:
        if _is_prefix_operator(before_previous, previous):
            return False
        return True

    if previous.type == token.NAME and current.type == token.NAME:
        return True
    if previous.type in {token.NAME, token.NUMBER, token.STRING} and current.type in {token.NAME, token.NUMBER, token.STRING}:
        return True

    return False


def _is_prefix_operator(
    context: tokenize.TokenInfo | None,
    operator: tokenize.TokenInfo,
) -> bool:
    if operator.string not in {"+", "-", "*", "**"}:
        return False
    if context is None:
        return True
    if context.type == token.OP and context.string in PREFIX_OPERATOR_CONTEXT:
        return True
    if context.type == token.NAME and context.string in PREFIX_OPERATOR_KEYWORDS:
        return True
    return False
