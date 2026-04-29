from __future__ import annotations

from io import StringIO
import re
import token
import tokenize

from .lowering import lower_module
from .parser import UnsupportedPytonySyntaxError, parse_module

KEYWORD_ALIASES = {
    "mica_vero": "False",
    "solo_una_macchia": "None",
    "lapalissiano": "True",
    "e_poi": "and",
    "come_monet": "as",
    "te_l_ho_detto": "assert",
    "fuori_piove": "async",
    "aspetta_amore": "await",
    "fine_del_mondo": "break",
    "uomo_cannone": "class",
    "anche_stasera": "continue",
    "e_se_invece": "elif",
    "senno": "else",
    "ma_ehi": "except",
    "a_dopo_amore": "finally",
    "gira_il_circo": "for",
    "dal_divano": "from",
    "su_tutta_la_terra": "global",
    "e_se": "if",
    "you_might_also_like": "import",
    "nell_alta_marea": "in",
    "sei_proprio": "is",
    "colpo_di_scena": "lambda",
    "vicoli_stretti": "nonlocal",
    "mica": "not",
    "oppure": "or",
    "fai_finta": "pass",
    "mentre_riposi": "while",
    "strofa": "def",
    "mi_strappo": "del",
    "interludio": "match",
    "bridge": "case",
    "oh_oh": "_",
    "scoppia": "raise",
    "restero": "return",
    "sperimentiamo": "try",
    "con_la_coperta": "with",
    "sfiora_le_stelle": "yield",
}

BUILTIN_ALIASES = {
    "spara_minchiate": "print",
    "pronto_amore": "input",
    "fai_la_pesata": "len",
    "viaggio_lontano": "range",
    "apri_il_portafoglio": "open",
    "schizzo_monet": "str",
    "duecento_euro": "int",
    "alta_marea": "float",
    "lapalissiano_o_mica": "bool",
    "popcorn": "list",
    "portafoglio": "dict",
    "mostri": "set",
    "coperta_calda": "tuple",
    "chi_siamo": "type",
    "lavarei_piatti": "sum",
    "meno_rossi": "min",
    "uomo_migliore": "max",
    "contale_tutte": "enumerate",
    "dammi_il_cuore": "zip",
    "di_lato": "reversed",
    "in_fusoliera": "sorted",
    "tutti_i_mostri": "all",
    "pure_uno": "any",
    "senza_arrossire": "abs",
    "a_crepapelle": "round",
}

ALIASES = KEYWORD_ALIASES | BUILTIN_ALIASES
PYTHON_TO_PYTONY = {python_name: pytony_name for pytony_name, python_name in ALIASES.items()}

FSTRING_PREFIX_RE = re.compile(r"(?i)^([rubf]*)(\"\"\"|'''|\"|')")
RITORNELLO_HEADER_RE = re.compile(
    r"^(?P<indent>[ \t]*)ritornello\s+(?P<count>.+?)\s*:(?P<comment>\s*#.*)?(?P<newline>\n?)$"
)
DUETTO_HEADER_RE = re.compile(
    r"^(?P<indent>[ \t]*)duetto\s+(?P<targets>.+?)\s+con\s+(?P<iterables>.+?)\s*:(?P<comment>\s*#.*)?(?P<newline>\n?)$"
)
ANCORA_UNA_VOLTA_HEADER_RE = re.compile(
    r"^(?P<indent>[ \t]*)ancora_una_volta\s+(?P<condition>.+?)\s*:(?P<comment>\s*#.*)?(?P<newline>\n?)$"
)


class PytonySyntaxError(SyntaxError):
    """Raised when a .pytony file uses Python vocabulary that Pytony reserves."""


def _build_forbidden_name_error(
    python_name: str,
    pytony_name: str,
    current: tokenize.TokenInfo,
) -> PytonySyntaxError:
    line_number = current.start[0]
    column = current.start[1] + 1
    message = (
        f"Nei file .pytony non puoi usare `{python_name}`: "
        f"qui devi scrivere `{pytony_name}`."
    )
    return PytonySyntaxError(f"{message} (riga {line_number}, colonna {column})")


def _transpile_expression(fragment: str, *, strict: bool = False) -> str:
    return transpile_source(fragment, strict=strict).rstrip("\n")


def _indent_width(indent: str) -> int:
    return len(indent.expandtabs(8))


def _leading_indent(line: str) -> str:
    return line[:len(line) - len(line.lstrip(" \t"))]


def _normalize_comma_spacing(fragment: str) -> str:
    return re.sub(r"\s*,\s*", ", ", fragment.strip())


def _build_first_tokens_by_line(source: str) -> dict[int, tokenize.TokenInfo]:
    first_tokens: dict[int, tokenize.TokenInfo] = {}
    ignored_types = {
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENDMARKER,
    }
    for current in tokenize.generate_tokens(StringIO(source).readline):
        if current.type in ignored_types:
            continue
        first_tokens.setdefault(current.start[0], current)
    return first_tokens


def _find_block_child_indent(
    lines: list[str],
    first_tokens: dict[int, tokenize.TokenInfo],
    header_index: int,
    header_indent_width: int,
) -> str | None:
    for line_index in range(header_index + 1, len(lines)):
        token_info = first_tokens.get(line_index + 1)
        if token_info is None:
            continue
        indent = _leading_indent(lines[line_index])
        if _indent_width(indent) <= header_indent_width:
            return None
        return indent
    return None


def _find_block_end(
    lines: list[str],
    first_tokens: dict[int, tokenize.TokenInfo],
    body_start: int,
    header_indent_width: int,
) -> int:
    for line_index in range(body_start, len(lines)):
        token_info = first_tokens.get(line_index + 1)
        if token_info is None:
            continue
        indent = _leading_indent(lines[line_index])
        if _indent_width(indent) <= header_indent_width:
            return line_index
    return len(lines)


def _rewrite_exclusive_constructs(source: str) -> str:
    lines = source.splitlines(keepends=True)
    if not lines:
        return source

    first_tokens = _build_first_tokens_by_line(source)
    ritornello_counter = 0

    def process_range(start: int, stop: int) -> list[str]:
        nonlocal ritornello_counter
        rewritten: list[str] = []
        line_index = start

        while line_index < stop:
            current_line = lines[line_index]
            token_info = first_tokens.get(line_index + 1)
            if token_info is None or token_info.type != token.NAME:
                rewritten.append(current_line)
                line_index += 1
                continue

            if token_info.string == "ritornello":
                match = RITORNELLO_HEADER_RE.match(current_line)
                if match:
                    ritornello_counter += 1
                    indent = match.group("indent")
                    comment = match.group("comment") or ""
                    newline = match.group("newline") or ""
                    count = match.group("count")
                    loop_name = f"__pytony_ritornello_{ritornello_counter}"
                    rewritten.append(
                        f"{indent}gira_il_circo {loop_name} nell_alta_marea "
                        f"viaggio_lontano({count}):{comment}{newline}"
                    )
                    line_index += 1
                    continue

            if token_info.string == "duetto":
                match = DUETTO_HEADER_RE.match(current_line)
                if match:
                    indent = match.group("indent")
                    comment = match.group("comment") or ""
                    newline = match.group("newline") or ""
                    targets = _normalize_comma_spacing(match.group("targets"))
                    iterables = _normalize_comma_spacing(match.group("iterables"))
                    rewritten.append(
                        f"{indent}gira_il_circo {targets} nell_alta_marea "
                        f"dammi_il_cuore({iterables}):{comment}{newline}"
                    )
                    line_index += 1
                    continue

            if token_info.string == "ancora_una_volta":
                match = ANCORA_UNA_VOLTA_HEADER_RE.match(current_line)
                if match:
                    indent = match.group("indent")
                    indent_width = _indent_width(indent)
                    child_indent = _find_block_child_indent(
                        lines,
                        first_tokens,
                        line_index,
                        indent_width,
                    )
                    if child_indent is None:
                        rewritten.append(current_line)
                        line_index += 1
                        continue

                    comment = match.group("comment") or ""
                    newline = match.group("newline") or ""
                    condition = match.group("condition")
                    block_end = _find_block_end(
                        lines,
                        first_tokens,
                        line_index + 1,
                        indent_width,
                    )
                    indent_unit = child_indent[len(indent):] if child_indent.startswith(indent) else ""
                    if not indent_unit:
                        indent_unit = "    "
                    rewritten.append(
                        f"{indent}mentre_riposi lapalissiano:{comment}{newline}"
                    )
                    rewritten.extend(process_range(line_index + 1, block_end))
                    rewritten.append(f"{child_indent}e_se mica ({condition}):\n")
                    rewritten.append(f"{child_indent}{indent_unit}fine_del_mondo\n")
                    line_index = block_end
                    continue

            rewritten.append(current_line)
            line_index += 1

        return rewritten

    return "".join(process_range(0, len(lines)))


def _split_fstring_field(field: str) -> tuple[str, str]:
    depth = 0
    string_delim = ""
    string_triple = False
    index = 0

    while index < len(field):
        current = field[index]
        trio = field[index:index + 3]

        if string_delim:
            if current == "\\":
                index += 2
                continue
            if string_triple and trio == string_delim * 3:
                string_delim = ""
                string_triple = False
                index += 3
                continue
            if not string_triple and current == string_delim:
                string_delim = ""
                index += 1
                continue
            index += 1
            continue

        if trio in ('"""', "'''"):
            string_delim = trio[0]
            string_triple = True
            index += 3
            continue
        if current in ("'", '"'):
            string_delim = current
            index += 1
            continue

        if current in "([{":
            depth += 1
            index += 1
            continue
        if current in ")]}":
            if depth > 0:
                depth -= 1
            index += 1
            continue

        if depth == 0 and current in ("!", ":"):
            return field[:index], field[index:]

        index += 1

    return field, ""


def _transpile_fstring(text: str, *, strict: bool = False) -> str:
    match = FSTRING_PREFIX_RE.match(text)
    if not match:
        return text

    prefix, quote = match.groups()
    if "f" not in prefix.lower():
        return text

    body_start = len(prefix) + len(quote)
    body_end = len(text) - len(quote)
    body = text[body_start:body_end]

    pieces: list[str] = []
    index = 0

    while index < len(body):
        current = body[index]

        if current == "{":
            if body[index:index + 2] == "{{":
                pieces.append("{{")
                index += 2
                continue

            field_start = index + 1
            depth = 0
            string_delim = ""
            string_triple = False
            cursor = field_start

            while cursor < len(body):
                char = body[cursor]
                trio = body[cursor:cursor + 3]

                if string_delim:
                    if char == "\\":
                        cursor += 2
                        continue
                    if string_triple and trio == string_delim * 3:
                        string_delim = ""
                        string_triple = False
                        cursor += 3
                        continue
                    if not string_triple and char == string_delim:
                        string_delim = ""
                        cursor += 1
                        continue
                    cursor += 1
                    continue

                if trio in ('"""', "'''"):
                    string_delim = trio[0]
                    string_triple = True
                    cursor += 3
                    continue
                if char in ("'", '"'):
                    string_delim = char
                    cursor += 1
                    continue
                if char in "([{":
                    depth += 1
                    cursor += 1
                    continue
                if char in ")]}":
                    if char == "}" and depth == 0:
                        break
                    if depth > 0:
                        depth -= 1
                    cursor += 1
                    continue
                cursor += 1

            if cursor >= len(body):
                pieces.append(body[index:])
                break

            field = body[field_start:cursor]
            expression, suffix = _split_fstring_field(field)
            pieces.append("{")
            pieces.append(_transpile_expression(expression, strict=strict))
            pieces.append(suffix)
            pieces.append("}")
            index = cursor + 1
            continue

        if current == "}" and body[index:index + 2] == "}}":
            pieces.append("}}")
            index += 2
            continue

        pieces.append(current)
        index += 1

    return f"{prefix}{quote}{''.join(pieces)}{quote}"


def transpile_source(source: str, *, strict: bool = False) -> str:
    """Convert a Pytony source string into valid Python code."""
    source = _rewrite_exclusive_constructs(source)
    stream = StringIO(source).readline
    tokens: list[tokenize.TokenInfo] = []
    has_comments = False

    for current in tokenize.generate_tokens(stream):
        if current.type == tokenize.COMMENT:
            has_comments = True
        if strict and current.type == token.NAME and current.string in PYTHON_TO_PYTONY:
            raise _build_forbidden_name_error(
                python_name=current.string,
                pytony_name=PYTHON_TO_PYTONY[current.string],
                current=current,
            )

        if current.type == token.NAME and current.string in ALIASES:
            current = tokenize.TokenInfo(
                type=current.type,
                string=ALIASES[current.string],
                start=current.start,
                end=current.end,
                line=current.line,
            )
        elif current.type == token.STRING:
            updated = _transpile_fstring(current.string, strict=strict)
            if updated != current.string:
                current = tokenize.TokenInfo(
                    type=current.type,
                    string=updated,
                    start=current.start,
                    end=current.end,
                    line=current.line,
                )
        tokens.append(current)

    python_source = tokenize.untokenize(tokens)
    if has_comments:
        return python_source

    try:
        module = parse_module(python_source)
    except UnsupportedPytonySyntaxError as error:
        if strict:
            raise PytonySyntaxError(str(error)) from error
        return python_source

    return lower_module(module)
