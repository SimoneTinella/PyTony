from __future__ import annotations

from io import StringIO
import re
import token
import tokenize

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

FSTRING_PREFIX_RE = re.compile(r"(?i)^([rubf]*)(\"\"\"|'''|\"|')")


def _transpile_expression(fragment: str) -> str:
    return transpile_source(fragment)


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


def _transpile_fstring(text: str) -> str:
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
            pieces.append(_transpile_expression(expression))
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


def transpile_source(source: str) -> str:
    """Convert a Pytony source string into valid Python code."""
    stream = StringIO(source).readline
    tokens: list[tokenize.TokenInfo] = []

    for current in tokenize.generate_tokens(stream):
        if current.type == token.NAME and current.string in ALIASES:
            current = tokenize.TokenInfo(
                type=current.type,
                string=ALIASES[current.string],
                start=current.start,
                end=current.end,
                line=current.line,
            )
        elif current.type == token.STRING:
            updated = _transpile_fstring(current.string)
            if updated != current.string:
                current = tokenize.TokenInfo(
                    type=current.type,
                    string=updated,
                    start=current.start,
                    end=current.end,
                    line=current.line,
                )
        tokens.append(current)

    return tokenize.untokenize(tokens)
