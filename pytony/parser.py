from __future__ import annotations

import ast
from io import StringIO
import re
import token
import tokenize

from .ast_nodes import (
    AsMatchPattern,
    AssignStatement,
    AssertStatement,
    AttributeExpression,
    AugAssignStatement,
    BinaryExpression,
    BoolExpression,
    BreakStatement,
    CallExpression,
    CaptureMatchPattern,
    ClassMatchPattern,
    ClassDefStatement,
    ComprehensionClause,
    CompareExpression,
    ComparePart,
    DictComprehensionExpression,
    DictEntry,
    DictExpression,
    DoubleStarredExpression,
    ContinueStatement,
    ExceptHandler,
    ExprStatement,
    Expression,
    ForStatement,
    FunctionDefStatement,
    GeneratorExpression,
    GroupExpression,
    IndexExpression,
    ImportAlias,
    ImportFromStatement,
    ImportStatement,
    KeywordMatchPattern,
    KeywordArgument,
    LambdaExpression,
    LiteralExpression,
    IfStatement,
    LiteralMatchPattern,
    ListComprehensionExpression,
    ListExpression,
    MatchPattern,
    MatchCase,
    MatchStatement,
    Module,
    NameExpression,
    OrMatchPattern,
    Parameter,
    PassStatement,
    RawMatchPattern,
    RawExpression,
    RaiseStatement,
    ReturnStatement,
    SequenceMatchPattern,
    SetComprehensionExpression,
    SetExpression,
    SliceExpression,
    StarMatchPattern,
    StarredExpression,
    Statement,
    TryStatement,
    TupleExpression,
    UnaryExpression,
    ValueMatchPattern,
    WildcardMatchPattern,
    WithItem,
    WithStatement,
    WhileStatement,
)


class UnsupportedPytonySyntaxError(ValueError):
    """Raised when the first Pytony AST milestone cannot represent a node yet."""


class UnsupportedPytonyExpressionSyntaxError(UnsupportedPytonySyntaxError):
    """Raised when the expression milestone cannot represent a fragment yet."""


class UnsupportedPytonyPatternSyntaxError(UnsupportedPytonySyntaxError):
    """Raised when the pattern milestone cannot represent a fragment yet."""


_BINDING_COMMA_RE = re.compile(r"\s*,\s*")


class _StatementTokenStream:
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines() or [""]
        self.tokens = [
            current
            for current in tokenize.generate_tokens(StringIO(source).readline)
            if current.type not in {tokenize.NL}
        ]
        self.index = 0

    def peek(self, offset: int = 0) -> tokenize.TokenInfo | None:
        position = self.index + offset
        if position >= len(self.tokens):
            return None
        return self.tokens[position]

    def advance(self) -> tokenize.TokenInfo:
        current = self.peek()
        if current is None:
            raise UnsupportedPytonySyntaxError("Fine file inattesa.")
        self.index += 1
        return current

    def match_name(self, value: str) -> bool:
        current = self.peek()
        if current and current.type == token.NAME and current.string == value:
            self.index += 1
            return True
        return False

    def match_op(self, value: str) -> bool:
        current = self.peek()
        if current and current.type == token.OP and current.string == value:
            self.index += 1
            return True
        return False

    def match_type(self, token_type: int) -> bool:
        current = self.peek()
        if current and current.type == token_type:
            self.index += 1
            return True
        return False

    def at_end(self) -> bool:
        current = self.peek()
        return current is None or current.type == tokenize.ENDMARKER

    def error(
        self,
        message: str,
        *,
        current: tokenize.TokenInfo | None = None,
    ) -> UnsupportedPytonySyntaxError:
        token_info = current or self.peek()
        if token_info is None:
            token_info = self.tokens[-1]
        return UnsupportedPytonySyntaxError(
            _format_native_syntax_error(message, token_info, self.lines)
        )

    def fail(
        self,
        message: str,
        *,
        current: tokenize.TokenInfo | None = None,
    ) -> None:
        raise self.error(message, current=current)


class _ExpressionTokenStream:
    def __init__(self, source: str):
        self.source = source
        self.tokens = [
            current
            for current in tokenize.generate_tokens(StringIO(source).readline)
            if current.type not in {tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER}
        ]
        self.index = 0

    def peek(self, offset: int = 0) -> tokenize.TokenInfo | None:
        position = self.index + offset
        if position >= len(self.tokens):
            return None
        return self.tokens[position]

    def advance(self) -> tokenize.TokenInfo:
        current = self.peek()
        if current is None:
            raise UnsupportedPytonyExpressionSyntaxError("Fine espressione inattesa.")
        self.index += 1
        return current

    def match_name(self, value: str) -> bool:
        current = self.peek()
        if current and current.type == token.NAME and current.string == value:
            self.index += 1
            return True
        return False

    def match_op(self, value: str) -> bool:
        current = self.peek()
        if current and current.type == token.OP and current.string == value:
            self.index += 1
            return True
        return False

    def at_end(self) -> bool:
        return self.index >= len(self.tokens)


class _PatternTokenStream:
    def __init__(self, source: str):
        self.source = source
        self.tokens = [
            current
            for current in tokenize.generate_tokens(StringIO(source).readline)
            if current.type not in {tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER}
        ]
        self.index = 0

    def peek(self, offset: int = 0) -> tokenize.TokenInfo | None:
        position = self.index + offset
        if position >= len(self.tokens):
            return None
        return self.tokens[position]

    def advance(self) -> tokenize.TokenInfo:
        current = self.peek()
        if current is None:
            raise UnsupportedPytonyPatternSyntaxError("Fine pattern inattesa.")
        self.index += 1
        return current

    def match_name(self, value: str) -> bool:
        current = self.peek()
        if current and current.type == token.NAME and current.string == value:
            self.index += 1
            return True
        return False

    def match_op(self, value: str) -> bool:
        current = self.peek()
        if current and current.type == token.OP and current.string == value:
            self.index += 1
            return True
        return False

    def at_end(self) -> bool:
        return self.index >= len(self.tokens)


def parse_module(source: str) -> Module:
    native_error: UnsupportedPytonySyntaxError | None = None
    try:
        return _parse_module_native(source)
    except UnsupportedPytonySyntaxError as error:
        native_error = error

    try:
        python_tree = ast.parse(source)
    except SyntaxError as error:
        if native_error is not None:
            raise native_error from error
        raise UnsupportedPytonySyntaxError(_format_python_syntax_error(error)) from error
    return Module(body=[_convert_statement(node, source) for node in python_tree.body])


def _parse_module_native(source: str) -> Module:
    stream = _StatementTokenStream(source)
    body = _parse_statement_block(stream, stop_types={tokenize.ENDMARKER})
    if not stream.at_end():
        current = stream.peek()
        raise UnsupportedPytonySyntaxError(
            f"Token inatteso `{current.string}` alla fine del modulo."
        )
    return Module(body=body)


def _parse_statement_block(
    stream: _StatementTokenStream,
    *,
    stop_types: set[int],
) -> list[Statement]:
    body: list[Statement] = []
    while True:
        current = stream.peek()
        if current is None or current.type in stop_types:
            return body
        if current.type == tokenize.NEWLINE:
            stream.advance()
            continue
        body.append(_parse_statement(stream))


def _parse_statement(stream: _StatementTokenStream) -> Statement:
    current = stream.peek()
    if current is None:
        stream.fail("Fine file inattesa dentro uno statement.")

    if current.type == token.NAME:
        if current.string == "import":
            return _parse_import_statement(stream)
        if current.string == "from":
            return _parse_import_from_statement(stream)
        if current.string == "return":
            return _parse_return_statement(stream)
        if current.string == "raise":
            return _parse_raise_statement(stream)
        if current.string == "assert":
            return _parse_assert_statement(stream)
        if current.string == "pass":
            return _parse_pass_statement(stream)
        if current.string == "break":
            return _parse_break_statement(stream)
        if current.string == "continue":
            return _parse_continue_statement(stream)
        if current.string in {"if", "elif"}:
            return _parse_if_statement(stream)
        if current.string == "while":
            return _parse_while_statement(stream)
        if current.string == "for":
            return _parse_for_statement(stream)
        if current.string == "def":
            return _parse_function_def_statement(stream)
        if current.string == "class":
            return _parse_class_def_statement(stream)
        if current.string == "with":
            return _parse_with_statement(stream)
        if current.string == "try":
            return _parse_try_statement(stream)
        if current.string == "match":
            return _parse_match_statement(stream)

    return _parse_assignment_or_expr_statement(stream)


def _parse_import_statement(stream: _StatementTokenStream) -> ImportStatement:
    if not stream.match_name("import"):
        stream.fail("Statement import non valido.")
    aliases = _parse_import_aliases(stream)
    _expect_newline(stream)
    return ImportStatement(aliases=aliases)


def _parse_import_from_statement(stream: _StatementTokenStream) -> ImportFromStatement:
    if not stream.match_name("from"):
        stream.fail("Statement from import non valido.")

    level = 0
    while True:
        current = stream.peek()
        if current and current.type == token.OP and current.string in {".", "..."}:
            level += len(current.string)
            stream.advance()
            continue
        break

    module_parts: list[str] = []
    while True:
        current = stream.peek()
        if current is None or current.type != token.NAME:
            break
        module_parts.append(stream.advance().string)
        if not stream.match_op("."):
            break
        module_parts.append(".")

    module_name = "".join(module_parts) or None
    if not stream.match_name("import"):
        stream.fail("Statement from import senza `import`.")

    if stream.match_op("*"):
        aliases = [ImportAlias(name="*")]
    else:
        aliases = _parse_import_aliases(stream)

    _expect_newline(stream)
    return ImportFromStatement(module=module_name, aliases=aliases, level=level)


def _parse_return_statement(stream: _StatementTokenStream) -> ReturnStatement:
    if not stream.match_name("return"):
        stream.fail("Statement return non valido.")

    value_tokens = _collect_until_newline(stream)
    if not value_tokens:
        return ReturnStatement()
    return ReturnStatement(value=_build_expression_from_tokens(value_tokens))


def _parse_raise_statement(stream: _StatementTokenStream) -> RaiseStatement:
    if not stream.match_name("raise"):
        stream.fail("Statement raise non valido.")

    value_tokens = _collect_until_newline(stream)
    if not value_tokens:
        return RaiseStatement()

    exception_tokens, cause_tokens = _split_tokens_on_top_level_name_once(value_tokens, "from")
    if cause_tokens is None:
        return RaiseStatement(exception=_build_expression_from_tokens(value_tokens))

    if not exception_tokens or not cause_tokens:
        stream.fail("Statement raise con `from` non valido.")

    return RaiseStatement(
        exception=_build_expression_from_tokens(exception_tokens),
        cause=_build_expression_from_tokens(cause_tokens),
    )


def _parse_assert_statement(stream: _StatementTokenStream) -> AssertStatement:
    if not stream.match_name("assert"):
        stream.fail("Statement assert non valido.")

    value_tokens = _collect_until_newline(stream)
    if not value_tokens:
        stream.fail("Statement assert senza condizione.")

    test_tokens, message_tokens = _split_tokens_on_top_level_op_once(value_tokens, ",")
    if not test_tokens:
        stream.fail("Statement assert senza condizione valida.")

    message = None
    if message_tokens is not None:
        if not message_tokens:
            stream.fail("Statement assert con messaggio vuoto.")
        message = _build_expression_from_tokens(message_tokens)

    return AssertStatement(test=_build_expression_from_tokens(test_tokens), message=message)


def _parse_pass_statement(stream: _StatementTokenStream) -> PassStatement:
    if not stream.match_name("pass"):
        stream.fail("Statement pass non valido.")
    _expect_statement_end(stream)
    return PassStatement()


def _parse_break_statement(stream: _StatementTokenStream) -> BreakStatement:
    if not stream.match_name("break"):
        stream.fail("Statement break non valido.")
    _expect_statement_end(stream)
    return BreakStatement()


def _parse_continue_statement(stream: _StatementTokenStream) -> ContinueStatement:
    if not stream.match_name("continue"):
        stream.fail("Statement continue non valido.")
    _expect_statement_end(stream)
    return ContinueStatement()


def _parse_if_statement(stream: _StatementTokenStream) -> IfStatement:
    keyword_name = stream.peek()
    if keyword_name is None or keyword_name.type != token.NAME or keyword_name.string not in {"if", "elif"}:
        stream.fail("Statement if/elif non valido.")
    stream.advance()

    test_tokens = _collect_until_colon(stream)
    if not test_tokens:
        stream.fail("Condition vuota in uno statement if.")
    body = _parse_suite(stream)

    orelse: list[Statement] = []
    current = stream.peek()
    if current and current.type == token.NAME and current.string == "elif":
        orelse = [_parse_if_statement(stream)]
    elif current and current.type == token.NAME and current.string == "else":
        stream.advance()
        orelse = _parse_suite(stream)

    return IfStatement(
        test=_build_expression_from_tokens(test_tokens),
        body=body,
        orelse=orelse,
    )


def _parse_while_statement(stream: _StatementTokenStream) -> WhileStatement:
    if not stream.match_name("while"):
        stream.fail("Statement while non valido.")

    test_tokens = _collect_until_colon(stream)
    if not test_tokens:
        stream.fail("Condition vuota in uno statement while.")
    body = _parse_suite(stream)

    orelse: list[Statement] = []
    current = stream.peek()
    if current and current.type == token.NAME and current.string == "else":
        stream.advance()
        orelse = _parse_suite(stream)

    return WhileStatement(
        test=_build_expression_from_tokens(test_tokens),
        body=body,
        orelse=orelse,
    )


def _parse_for_statement(stream: _StatementTokenStream) -> ForStatement:
    if not stream.match_name("for"):
        stream.fail("Statement for non valido.")

    header_tokens = _collect_until_colon(stream)
    target_tokens, iterator_tokens = _split_tokens_on_top_level_name_once(header_tokens, "in")
    if not target_tokens or not iterator_tokens:
        stream.fail("Statement for senza `in` valido.")
    body = _parse_suite(stream)

    orelse: list[Statement] = []
    current = stream.peek()
    if current and current.type == token.NAME and current.string == "else":
        stream.advance()
        orelse = _parse_suite(stream)

    return ForStatement(
        target=_normalize_binding_target(_untokenize_tokens(target_tokens)),
        iterator=_build_expression_from_tokens(iterator_tokens),
        body=body,
        orelse=orelse,
    )


def _parse_function_def_statement(stream: _StatementTokenStream) -> FunctionDefStatement:
    if not stream.match_name("def"):
        stream.fail("Statement def non valido.")

    name_token = stream.advance()
    if name_token.type != token.NAME:
        stream.fail("Nome funzione non valido.", current=name_token)
    if not stream.match_op("("):
        stream.fail("Definizione funzione senza `(`.")

    parameter_tokens = _collect_parenthesized_content(stream)
    return_annotation = None
    if stream.match_op("->"):
        annotation_tokens = _collect_until_colon(stream)
        return_annotation = _untokenize_tokens(annotation_tokens).strip() or None

    body = _parse_suite(stream)
    return FunctionDefStatement(
        name=name_token.string,
        parameters=_parse_parameter_list(parameter_tokens),
        body=body,
        return_annotation=return_annotation,
    )


def _parse_class_def_statement(stream: _StatementTokenStream) -> ClassDefStatement:
    if not stream.match_name("class"):
        stream.fail("Statement class non valido.")

    name_token = stream.advance()
    if name_token.type != token.NAME:
        stream.fail("Nome classe non valido.", current=name_token)

    bases: list[Expression] = []
    if stream.match_op("("):
        base_tokens = _collect_parenthesized_content(stream)
        bases = _parse_expression_list(base_tokens)

    body = _parse_suite(stream)
    return ClassDefStatement(name=name_token.string, bases=bases, body=body)


def _parse_with_statement(stream: _StatementTokenStream) -> WithStatement:
    if not stream.match_name("with"):
        stream.fail("Statement with non valido.")

    header_tokens = _collect_until_colon(stream)
    items = _parse_with_items(header_tokens)
    if not items:
        stream.fail("Statement with senza contesto.")
    body = _parse_suite(stream)
    return WithStatement(items=items, body=body)


def _parse_try_statement(stream: _StatementTokenStream) -> TryStatement:
    if not stream.match_name("try"):
        stream.fail("Statement try non valido.")

    body = _parse_suite(stream)
    handlers: list[ExceptHandler] = []
    orelse: list[Statement] = []
    finalbody: list[Statement] = []

    while True:
        current = stream.peek()
        if current is None or current.type != token.NAME:
            break
        if current.string == "except":
            handlers.append(_parse_except_handler(stream))
            continue
        if current.string == "else":
            if orelse:
                stream.fail("Blocco try con piu `else`.", current=current)
            stream.advance()
            orelse = _parse_suite(stream)
            continue
        if current.string == "finally":
            if finalbody:
                stream.fail("Blocco try con piu `finally`.", current=current)
            stream.advance()
            finalbody = _parse_suite(stream)
            continue
        break

    if not handlers and not finalbody:
        stream.fail("Blocco try senza `except` o `finally`.")

    return TryStatement(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)


def _parse_match_statement(stream: _StatementTokenStream) -> MatchStatement:
    if not stream.match_name("match"):
        stream.fail("Statement match non valido.")

    subject_tokens = _collect_until_colon(stream)
    if not subject_tokens:
        stream.fail("Statement match senza soggetto.")
    if not stream.match_op(":"):
        stream.fail("Statement match senza `:`.")

    _expect_indented_block_start(stream)
    cases: list[MatchCase] = []

    while True:
        current = stream.peek()
        if current is None:
            stream.fail("Blocco match non chiuso correttamente.")
        if current.type == tokenize.DEDENT:
            stream.advance()
            break
        if current.type == tokenize.NEWLINE:
            stream.advance()
            continue
        if current.type != token.NAME or current.string != "case":
            stream.fail("Dentro `match` ogni blocco deve iniziare con `case`.", current=current)
        cases.append(_parse_match_case(stream))

    if not cases:
        stream.fail("Statement match senza case.")

    return MatchStatement(subject=_build_expression_from_tokens(subject_tokens), cases=cases)


def _parse_match_case(stream: _StatementTokenStream) -> MatchCase:
    if not stream.match_name("case"):
        stream.fail("Blocco case non valido.")

    header_tokens = _collect_until_colon(stream)
    if not header_tokens:
        stream.fail("Blocco case senza pattern.")

    pattern_tokens, guard_tokens = _split_tokens_on_top_level_name_once(header_tokens, "if")
    if guard_tokens is None:
        pattern_source = _untokenize_tokens(header_tokens).strip()
        guard = None
    else:
        if not pattern_tokens or not guard_tokens:
            stream.fail("Blocco case con guard non valido.")
        pattern_source = _untokenize_tokens(pattern_tokens).strip()
        guard = _build_expression_from_tokens(guard_tokens)

    if not pattern_source:
        stream.fail("Blocco case senza pattern valido.")
    if not stream.match_op(":"):
        stream.fail("Blocco case senza `:`.")

    body = _parse_indented_block(stream)
    return MatchCase(
        pattern=_build_match_pattern(pattern_source),
        pattern_source=pattern_source,
        guard=guard,
        body=body,
    )


def _parse_assignment_or_expr_statement(stream: _StatementTokenStream) -> Statement:
    tokens = _collect_until_newline(stream)
    if not tokens:
        stream.fail("Statement vuoto non valido.")

    target_tokens, operator, value_tokens = _split_tokens_on_top_level_augassign_once(tokens)
    if operator is not None:
        if not target_tokens or not value_tokens:
            stream.fail("Assegnazione aumentata non valida.")
        return AugAssignStatement(
            target=_untokenize_tokens(target_tokens).strip(),
            operator=operator,
            value=_build_expression_from_tokens(value_tokens),
        )

    segments = _split_tokens_on_top_level_op(tokens, "=")
    if len(segments) > 1:
        targets = [_untokenize_tokens(segment).strip() for segment in segments[:-1]]
        if any(not target for target in targets):
            stream.fail("Assegnazione con target vuoto.")
        return AssignStatement(targets=targets, value=_build_expression_from_tokens(segments[-1]))

    return ExprStatement(expression=_build_expression_from_tokens(tokens))


def _parse_suite(stream: _StatementTokenStream) -> list[Statement]:
    if not stream.match_op(":"):
        stream.fail("Blocco senza `:`.")
    return _parse_indented_block(stream)


def _parse_indented_block(stream: _StatementTokenStream) -> list[Statement]:
    _expect_indented_block_start(stream)
    body = _parse_statement_block(stream, stop_types={tokenize.DEDENT})
    if not stream.match_type(tokenize.DEDENT):
        stream.fail("Blocco non chiuso correttamente.")
    return body


def _segment(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return ast.unparse(node)
    return segment


def _convert_expression(node: ast.AST, source: str) -> Expression:
    expression_source = _segment(source, node)
    try:
        return parse_expression(expression_source)
    except UnsupportedPytonyExpressionSyntaxError:
        return RawExpression(source=expression_source)


def _convert_parameters(node: ast.arguments, source: str) -> list[Parameter]:
    if node.posonlyargs or node.vararg or node.kwonlyargs or node.kwarg or node.defaults or node.kw_defaults:
        raise UnsupportedPytonySyntaxError(
            "Il primo milestone AST di Pytony supporta solo parametri semplici senza default."
        )

    parameters: list[Parameter] = []
    for argument in node.args:
        annotation = _segment(source, argument.annotation) if argument.annotation else None
        parameters.append(Parameter(name=argument.arg, annotation=annotation))
    return parameters


def _convert_statement(node: ast.stmt, source: str) -> Statement:
    if isinstance(node, ast.Import):
        return ImportStatement(
            aliases=[ImportAlias(name=alias.name, asname=alias.asname) for alias in node.names]
        )

    if isinstance(node, ast.ImportFrom):
        return ImportFromStatement(
            module=node.module,
            aliases=[ImportAlias(name=alias.name, asname=alias.asname) for alias in node.names],
            level=node.level,
        )

    if isinstance(node, ast.Expr):
        return ExprStatement(expression=_convert_expression(node.value, source))

    if isinstance(node, ast.Assign):
        return AssignStatement(
            targets=[_segment(source, target) for target in node.targets],
            value=_convert_expression(node.value, source),
        )

    if isinstance(node, ast.AugAssign):
        return AugAssignStatement(
            target=_segment(source, node.target),
            operator=_convert_augassign_operator(node.op),
            value=_convert_expression(node.value, source),
        )

    if isinstance(node, ast.Pass):
        return PassStatement()

    if isinstance(node, ast.Break):
        return BreakStatement()

    if isinstance(node, ast.Continue):
        return ContinueStatement()

    if isinstance(node, ast.Return):
        value = _convert_expression(node.value, source) if node.value else None
        return ReturnStatement(value=value)

    if isinstance(node, ast.Raise):
        return RaiseStatement(
            exception=_convert_expression(node.exc, source) if node.exc else None,
            cause=_convert_expression(node.cause, source) if node.cause else None,
        )

    if isinstance(node, ast.Assert):
        return AssertStatement(
            test=_convert_expression(node.test, source),
            message=_convert_expression(node.msg, source) if node.msg else None,
        )

    if isinstance(node, ast.If):
        return IfStatement(
            test=_convert_expression(node.test, source),
            body=[_convert_statement(child, source) for child in node.body],
            orelse=[_convert_statement(child, source) for child in node.orelse],
        )

    if isinstance(node, ast.While):
        return WhileStatement(
            test=_convert_expression(node.test, source),
            body=[_convert_statement(child, source) for child in node.body],
            orelse=[_convert_statement(child, source) for child in node.orelse],
        )

    if isinstance(node, ast.For):
        return ForStatement(
            target=_segment(source, node.target),
            iterator=_convert_expression(node.iter, source),
            body=[_convert_statement(child, source) for child in node.body],
            orelse=[_convert_statement(child, source) for child in node.orelse],
        )

    if isinstance(node, ast.FunctionDef):
        if node.decorator_list:
            raise UnsupportedPytonySyntaxError(
                "Il primo milestone AST di Pytony non supporta ancora i decorator."
            )
        return FunctionDefStatement(
            name=node.name,
            parameters=_convert_parameters(node.args, source),
            body=[_convert_statement(child, source) for child in node.body],
            return_annotation=_segment(source, node.returns) if node.returns else None,
        )

    if isinstance(node, ast.ClassDef):
        if node.decorator_list or node.keywords:
            raise UnsupportedPytonySyntaxError(
                "Il parser Pytony non supporta ancora decorator o keyword nelle classi."
            )
        return ClassDefStatement(
            name=node.name,
            bases=[_convert_expression(base, source) for base in node.bases],
            body=[_convert_statement(child, source) for child in node.body],
        )

    if isinstance(node, ast.With):
        items = [
            WithItem(
                context=_convert_expression(item.context_expr, source),
                target=_segment(source, item.optional_vars) if item.optional_vars else None,
            )
            for item in node.items
        ]
        return WithStatement(
            items=items,
            body=[_convert_statement(child, source) for child in node.body],
        )

    if isinstance(node, ast.Try):
        handlers = [
            ExceptHandler(
                exception=_convert_expression(handler.type, source) if handler.type else None,
                target=handler.name,
                body=[_convert_statement(child, source) for child in handler.body],
            )
            for handler in node.handlers
        ]
        return TryStatement(
            body=[_convert_statement(child, source) for child in node.body],
            handlers=handlers,
            orelse=[_convert_statement(child, source) for child in node.orelse],
            finalbody=[_convert_statement(child, source) for child in node.finalbody],
        )

    if isinstance(node, ast.Match):
        cases = [
            MatchCase(
                pattern=_build_match_pattern(_segment(source, case.pattern)),
                pattern_source=_segment(source, case.pattern),
                guard=_convert_expression(case.guard, source) if case.guard else None,
                body=[_convert_statement(child, source) for child in case.body],
            )
            for case in node.cases
        ]
        return MatchStatement(
            subject=_convert_expression(node.subject, source),
            cases=cases,
        )

    raise UnsupportedPytonySyntaxError(
        f"Il primo milestone AST di Pytony non supporta ancora `{type(node).__name__}`."
    )


def _parse_import_aliases(stream: _StatementTokenStream) -> list[ImportAlias]:
    aliases: list[ImportAlias] = []
    while True:
        name_parts: list[str] = []
        current = stream.peek()
        if current is None or current.type != token.NAME:
            raise UnsupportedPytonySyntaxError("Import senza nome valido.")

        while True:
            name_token = stream.advance()
            if name_token.type != token.NAME:
                raise UnsupportedPytonySyntaxError("Import con nome non valido.")
            name_parts.append(name_token.string)
            if not stream.match_op("."):
                break
            name_parts.append(".")

        asname = None
        if stream.match_name("as"):
            alias_token = stream.advance()
            if alias_token.type != token.NAME:
                raise UnsupportedPytonySyntaxError("Alias import non valido.")
            asname = alias_token.string

        aliases.append(ImportAlias(name="".join(name_parts), asname=asname))
        if not stream.match_op(","):
            return aliases


def _parse_parameter_list(tokens: list[tokenize.TokenInfo]) -> list[Parameter]:
    if not tokens:
        return []

    parameters: list[Parameter] = []
    for segment in _split_tokens_on_top_level_op(tokens, ","):
        parameter_source = _untokenize_tokens(segment).strip()
        if not parameter_source:
            continue
        if any(current.string in {"=", "/", "*", "**"} for current in segment):
            raise UnsupportedPytonySyntaxError(
                "Il parser nativo supporta solo parametri semplici senza default."
            )

        name_tokens, annotation_tokens = _split_tokens_on_top_level_op_once(segment, ":")
        if not name_tokens:
            raise UnsupportedPytonySyntaxError("Parametro funzione non valido.")
        name = _untokenize_tokens(name_tokens).strip()
        if not name.isidentifier():
            raise UnsupportedPytonySyntaxError("Nome parametro non valido.")

        annotation = None
        if annotation_tokens is not None:
            annotation = _untokenize_tokens(annotation_tokens).strip() or None

        parameters.append(Parameter(name=name, annotation=annotation))

    return parameters


def _parse_expression_list(tokens: list[tokenize.TokenInfo]) -> list[Expression]:
    if not tokens:
        return []

    expressions: list[Expression] = []
    for segment in _split_tokens_on_top_level_op(tokens, ","):
        if not segment or not _untokenize_tokens(segment).strip():
            continue
        expressions.append(_build_expression_from_tokens(segment))
    return expressions


def _parse_with_items(tokens: list[tokenize.TokenInfo]) -> list[WithItem]:
    items: list[WithItem] = []
    for segment in _split_tokens_on_top_level_op(tokens, ","):
        if not segment or not _untokenize_tokens(segment).strip():
            continue
        context_tokens, target_tokens = _split_tokens_on_top_level_name_once(segment, "as")
        if target_tokens is None:
            items.append(WithItem(context=_build_expression_from_tokens(segment)))
            continue
        if not context_tokens or not target_tokens:
            raise UnsupportedPytonySyntaxError("Item `with` non valido.")
        target = _untokenize_tokens(target_tokens).strip()
        if not target:
            raise UnsupportedPytonySyntaxError("Alias `with` vuoto.")
        items.append(
            WithItem(
                context=_build_expression_from_tokens(context_tokens),
                target=target,
            )
        )
    return items


def _parse_except_handler(stream: _StatementTokenStream) -> ExceptHandler:
    if not stream.match_name("except"):
        raise UnsupportedPytonySyntaxError("Blocco except non valido.")

    header_tokens = _collect_until_colon(stream)
    exception = None
    target = None
    if header_tokens:
        exception_tokens, target_tokens = _split_tokens_on_top_level_name_once(header_tokens, "as")
        if target_tokens is None:
            exception = _build_expression_from_tokens(header_tokens)
        else:
            if not exception_tokens or not target_tokens:
                raise UnsupportedPytonySyntaxError("Blocco except con `as` non valido.")
            target = _untokenize_tokens(target_tokens).strip()
            if not target:
                raise UnsupportedPytonySyntaxError("Alias except vuoto.")
            exception = _build_expression_from_tokens(exception_tokens)

    body = _parse_suite(stream)
    return ExceptHandler(exception=exception, target=target, body=body)


def _build_expression_from_tokens(tokens: list[tokenize.TokenInfo]) -> Expression:
    source = _untokenize_tokens(tokens).strip()
    if not source:
        raise UnsupportedPytonySyntaxError("Espressione vuota.")

    try:
        return parse_expression(source)
    except UnsupportedPytonyExpressionSyntaxError as error:
        try:
            ast.parse(source, mode="eval")
        except SyntaxError as syntax_error:
            raise UnsupportedPytonySyntaxError(_format_python_syntax_error(syntax_error)) from syntax_error
        return RawExpression(source=source)


def _collect_until_newline(stream: _StatementTokenStream) -> list[tokenize.TokenInfo]:
    tokens: list[tokenize.TokenInfo] = []
    while True:
        current = stream.peek()
        if current is None or current.type in {tokenize.ENDMARKER, tokenize.DEDENT}:
            return tokens
        if current.type == tokenize.NEWLINE:
            stream.advance()
            return tokens
        tokens.append(stream.advance())


def _collect_until_colon(stream: _StatementTokenStream) -> list[tokenize.TokenInfo]:
    tokens: list[tokenize.TokenInfo] = []
    depth = 0

    while True:
        current = stream.peek()
        if current is None:
            stream.fail("Header incompleto: manca `:`.")
        if current.type == tokenize.NEWLINE:
            stream.fail("Header spezzato prima di `:`.", current=current)
        if depth == 0 and current.type == token.OP and current.string == ":":
            return tokens

        if current.type == token.OP:
            if current.string in {"(", "[", "{"}:
                depth += 1
            elif current.string in {")", "]", "}"}:
                depth -= 1

        tokens.append(stream.advance())


def _collect_parenthesized_content(stream: _StatementTokenStream) -> list[tokenize.TokenInfo]:
    tokens: list[tokenize.TokenInfo] = []
    depth = 1

    while True:
        current = stream.advance()
        if current.type == token.OP:
            if current.string in {"(", "[", "{"}:
                depth += 1
            elif current.string in {")", "]", "}"}:
                depth -= 1
                if depth == 0:
                    return tokens
        tokens.append(current)


def _split_tokens_on_top_level_name_once(
    tokens: list[tokenize.TokenInfo],
    name: str,
) -> tuple[list[tokenize.TokenInfo] | None, list[tokenize.TokenInfo] | None]:
    depth = 0
    for index, current in enumerate(tokens):
        if current.type == token.OP:
            if current.string in {"(", "[", "{"}:
                depth += 1
            elif current.string in {")", "]", "}"}:
                depth -= 1
        if depth == 0 and current.type == token.NAME and current.string == name:
            return tokens[:index], tokens[index + 1:]
    return None, None


def _split_tokens_on_top_level_augassign_once(
    tokens: list[tokenize.TokenInfo],
) -> tuple[list[tokenize.TokenInfo] | None, str | None, list[tokenize.TokenInfo] | None]:
    augmented_operators = {
        "+=": "+",
        "-=": "-",
        "*=": "*",
        "/=": "/",
        "%=": "%",
        "//=": "//",
        "@=": "@",
        "&=": "&",
        "|=": "|",
        "^=": "^",
        ">>=": ">>",
        "<<=": "<<",
        "**=": "**",
    }
    depth = 0
    for index, current in enumerate(tokens):
        if current.type == token.OP:
            if current.string in {"(", "[", "{"}:
                depth += 1
            elif current.string in {")", "]", "}"}:
                depth -= 1

        if depth == 0 and current.type == token.OP and current.string in augmented_operators:
            return tokens[:index], augmented_operators[current.string], tokens[index + 1:]

    return None, None, None


def _split_tokens_on_top_level_op(
    tokens: list[tokenize.TokenInfo],
    operator: str,
) -> list[list[tokenize.TokenInfo]]:
    parts: list[list[tokenize.TokenInfo]] = []
    current_part: list[tokenize.TokenInfo] = []
    depth = 0

    for current in tokens:
        if current.type == token.OP:
            if current.string in {"(", "[", "{"}:
                depth += 1
            elif current.string in {")", "]", "}"}:
                depth -= 1

        if depth == 0 and current.type == token.OP and current.string == operator:
            parts.append(current_part)
            current_part = []
            continue

        current_part.append(current)

    parts.append(current_part)
    return parts


def _split_tokens_on_top_level_op_once(
    tokens: list[tokenize.TokenInfo],
    operator: str,
) -> tuple[list[tokenize.TokenInfo] | None, list[tokenize.TokenInfo] | None]:
    depth = 0
    for index, current in enumerate(tokens):
        if current.type == token.OP:
            if current.string in {"(", "[", "{"}:
                depth += 1
            elif current.string in {")", "]", "}"}:
                depth -= 1

        if depth == 0 and current.type == token.OP and current.string == operator:
            return tokens[:index], tokens[index + 1:]

    return tokens, None


def _untokenize_tokens(tokens: list[tokenize.TokenInfo]) -> str:
    if not tokens:
        return ""
    return tokenize.untokenize((current.type, current.string) for current in tokens)


def _normalize_binding_target(source: str) -> str:
    return _BINDING_COMMA_RE.sub(", ", source.strip())


def _expect_newline(stream: _StatementTokenStream) -> None:
    current = stream.peek()
    if current is None or current.type == tokenize.ENDMARKER:
        return
    if not stream.match_type(tokenize.NEWLINE):
        stream.fail("Statement non terminato correttamente.", current=current)


def _expect_indented_block_start(stream: _StatementTokenStream) -> None:
    if not stream.match_type(tokenize.NEWLINE):
        stream.fail("Dopo `:` serve una nuova riga nel sottoinsieme nativo.")
    if not stream.match_type(tokenize.INDENT):
        stream.fail("Blocco indentato mancante.")


def _expect_statement_end(stream: _StatementTokenStream) -> None:
    current = stream.peek()
    if current is None or current.type in {tokenize.ENDMARKER, tokenize.DEDENT}:
        return
    if current.type != tokenize.NEWLINE:
        stream.fail("Statement non terminato correttamente.", current=current)
    stream.advance()


def _build_match_pattern(source: str) -> MatchPattern:
    if not source:
        raise UnsupportedPytonyPatternSyntaxError("Pattern Pytony vuoto.")

    try:
        return parse_pattern(source)
    except UnsupportedPytonyPatternSyntaxError as error:
        if _is_valid_python_pattern(source):
            return RawMatchPattern(source=source)
        raise error


def parse_pattern(source: str) -> MatchPattern:
    stream = _PatternTokenStream(source)
    pattern = _parse_as_match_pattern(stream)
    if not stream.at_end():
        current = stream.peek()
        raise UnsupportedPytonyPatternSyntaxError(
            f"Pattern non supportato vicino a `{current.string}`."
        )
    return pattern


def _parse_as_match_pattern(stream: _PatternTokenStream) -> MatchPattern:
    pattern = _parse_or_match_pattern(stream)
    if not stream.match_name("as"):
        return pattern

    alias = stream.advance()
    if alias.type != token.NAME or alias.string == "_":
        raise UnsupportedPytonyPatternSyntaxError("Alias pattern non valido dopo `as`.")
    return AsMatchPattern(pattern=pattern, name=alias.string)


def _parse_or_match_pattern(stream: _PatternTokenStream) -> MatchPattern:
    patterns = [_parse_closed_match_pattern(stream)]
    while stream.match_op("|"):
        patterns.append(_parse_closed_match_pattern(stream))

    if len(patterns) == 1:
        return patterns[0]
    return OrMatchPattern(patterns=patterns)


def _parse_closed_match_pattern(stream: _PatternTokenStream) -> MatchPattern:
    current = stream.peek()
    if current is None:
        raise UnsupportedPytonyPatternSyntaxError("Pattern Pytony incompleto.")

    if current.type == token.OP and current.string == "[":
        stream.advance()
        return _parse_list_match_pattern(stream)

    if current.type == token.OP and current.string == "(":
        stream.advance()
        return _parse_tuple_or_group_match_pattern(stream)

    if current.type == token.OP and current.string in {"+", "-"}:
        return _parse_signed_literal_match_pattern(stream)

    if current.type in {token.STRING, token.NUMBER}:
        stream.advance()
        return LiteralMatchPattern(value_source=current.string)

    if current.type == token.NAME:
        if current.string in {"True", "False", "None"}:
            stream.advance()
            return LiteralMatchPattern(value_source=current.string)
        if current.string == "_":
            stream.advance()
            return WildcardMatchPattern()

        value, dotted = _parse_pattern_name_or_attr(stream)
        if stream.match_op("("):
            return _parse_class_match_pattern(stream, value)
        if dotted:
            return ValueMatchPattern(value=value)
        if isinstance(value, NameExpression):
            return CaptureMatchPattern(name=value.identifier)

    raise UnsupportedPytonyPatternSyntaxError(
        f"Pattern Pytony non supportato vicino a `{current.string}`."
    )


def _parse_pattern_name_or_attr(
    stream: _PatternTokenStream,
) -> tuple[Expression, bool]:
    name = stream.advance()
    if name.type != token.NAME:
        raise UnsupportedPytonyPatternSyntaxError("Nome pattern non valido.")

    expression: Expression = NameExpression(source=name.string, identifier=name.string)
    dotted = False
    while stream.match_op("."):
        attribute = stream.advance()
        if attribute.type != token.NAME:
            raise UnsupportedPytonyPatternSyntaxError("Attributo pattern non valido.")
        expression = AttributeExpression(
            source=f"{expression.source}.{attribute.string}",
            value=expression,
            attribute=attribute.string,
        )
        dotted = True
    return expression, dotted


def _parse_signed_literal_match_pattern(stream: _PatternTokenStream) -> MatchPattern:
    operator = stream.advance()
    value = stream.advance()
    if value.type != token.NUMBER:
        raise UnsupportedPytonyPatternSyntaxError("Solo i numeri supportano segno esplicito nei pattern.")
    return LiteralMatchPattern(value_source=f"{operator.string}{value.string}")


def _parse_list_match_pattern(stream: _PatternTokenStream) -> MatchPattern:
    if stream.match_op("]"):
        return SequenceMatchPattern(kind="list", elements=[])

    elements = [_parse_sequence_match_element(stream)]
    while True:
        if stream.match_op("]"):
            return SequenceMatchPattern(kind="list", elements=elements)
        if not stream.match_op(","):
            raise UnsupportedPytonyPatternSyntaxError("Pattern lista non valido.")
        if stream.match_op("]"):
            return SequenceMatchPattern(kind="list", elements=elements)
        elements.append(_parse_sequence_match_element(stream))


def _parse_tuple_or_group_match_pattern(stream: _PatternTokenStream) -> MatchPattern:
    if stream.match_op(")"):
        return SequenceMatchPattern(kind="tuple", elements=[])

    first = _parse_sequence_match_element(stream)
    if stream.match_op(")"):
        return first
    if not stream.match_op(","):
        current = stream.peek()
        token_text = current.string if current else ")"
        raise UnsupportedPytonyPatternSyntaxError(
            f"Pattern tra parentesi non valido vicino a `{token_text}`."
        )

    elements = [first]
    while True:
        if stream.match_op(")"):
            return SequenceMatchPattern(kind="tuple", elements=elements)
        elements.append(_parse_sequence_match_element(stream))
        if stream.match_op(")"):
            return SequenceMatchPattern(kind="tuple", elements=elements)
        if not stream.match_op(","):
            raise UnsupportedPytonyPatternSyntaxError("Pattern tupla non valido.")


def _parse_sequence_match_element(stream: _PatternTokenStream) -> MatchPattern:
    if not stream.match_op("*"):
        return _parse_as_match_pattern(stream)

    current = stream.peek()
    if current and current.type == token.NAME and current.string == "_":
        stream.advance()
        return StarMatchPattern(name=None)
    if current and current.type == token.NAME:
        stream.advance()
        return StarMatchPattern(name=current.string)
    raise UnsupportedPytonyPatternSyntaxError("Star pattern non valido.")


def _parse_class_match_pattern(
    stream: _PatternTokenStream,
    class_name: Expression,
) -> MatchPattern:
    positional_patterns: list[MatchPattern] = []
    keyword_patterns: list[KeywordMatchPattern] = []
    seen_keyword = False

    if stream.match_op(")"):
        return ClassMatchPattern(
            class_name=class_name,
            patterns=positional_patterns,
            keyword_patterns=keyword_patterns,
        )

    while True:
        if _looks_like_pattern_keyword(stream):
            seen_keyword = True
            name = stream.advance().string
            stream.advance()
            keyword_patterns.append(
                KeywordMatchPattern(name=name, pattern=_parse_as_match_pattern(stream))
            )
        else:
            if seen_keyword:
                raise UnsupportedPytonyPatternSyntaxError(
                    "I pattern posizionali non possono arrivare dopo quelli nominati."
                )
            positional_patterns.append(_parse_as_match_pattern(stream))

        if stream.match_op(")"):
            return ClassMatchPattern(
                class_name=class_name,
                patterns=positional_patterns,
                keyword_patterns=keyword_patterns,
            )
        if not stream.match_op(","):
            raise UnsupportedPytonyPatternSyntaxError("Argomenti del class pattern non validi.")
        if stream.match_op(")"):
            return ClassMatchPattern(
                class_name=class_name,
                patterns=positional_patterns,
                keyword_patterns=keyword_patterns,
            )


def _looks_like_pattern_keyword(stream: _PatternTokenStream) -> bool:
    current = stream.peek()
    next_token = stream.peek(1)
    return (
        current is not None
        and next_token is not None
        and current.type == token.NAME
        and next_token.type == token.OP
        and next_token.string == "="
    )


def _is_valid_python_pattern(source: str) -> bool:
    try:
        ast.parse(f"match _:\n    case {source}:\n        pass\n")
    except SyntaxError:
        return False
    return True


def parse_expression(source: str) -> Expression:
    stream = _ExpressionTokenStream(source)
    expression = _parse_lambda_expression(stream, source)
    if not stream.at_end():
        raise UnsupportedPytonyExpressionSyntaxError(
            f"Espressione non supportata vicino a `{stream.peek().string}`."
        )
    return expression


def _parse_lambda_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    if not stream.match_name("lambda"):
        return _parse_or_expression(stream, source)

    parameters: list[str] = []
    if not stream.match_op(":"):
        while True:
            current = stream.advance()
            if current.type != token.NAME:
                raise UnsupportedPytonyExpressionSyntaxError("Parametro lambda non valido.")
            parameters.append(current.string)
            if stream.match_op(":"):
                break
            if not stream.match_op(","):
                raise UnsupportedPytonyExpressionSyntaxError("Parametri lambda non validi.")

    body = _parse_lambda_expression(stream, source)
    return LambdaExpression(source=source, parameters=parameters, body=body)


def _parse_or_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    values = [_parse_and_expression(stream, source)]
    while stream.match_name("or"):
        values.append(_parse_and_expression(stream, source))

    if len(values) == 1:
        return values[0]
    return BoolExpression(source=source, operator="or", values=values)


def _parse_and_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    values = [_parse_not_expression(stream, source)]
    while stream.match_name("and"):
        values.append(_parse_not_expression(stream, source))

    if len(values) == 1:
        return values[0]
    return BoolExpression(source=source, operator="and", values=values)


def _parse_not_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    if stream.match_name("not"):
        operand = _parse_not_expression(stream, source)
        return UnaryExpression(source=source, operator="not", operand=operand)
    return _parse_comparison_expression(stream, source)


def _parse_comparison_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    left = _parse_additive_expression(stream, source)
    comparisons: list[ComparePart] = []

    while True:
        operator = _consume_comparison_operator(stream)
        if operator is None:
            break
        right = _parse_additive_expression(stream, source)
        comparisons.append(ComparePart(operator=operator, right=right))

    if not comparisons:
        return left
    return CompareExpression(source=source, left=left, comparisons=comparisons)


def _consume_comparison_operator(stream: _ExpressionTokenStream) -> str | None:
    current = stream.peek()
    if current is None:
        return None

    if current.type == token.OP and current.string in {"==", "!=", "<", "<=", ">", ">="}:
        stream.advance()
        return current.string

    if current.type == token.NAME and current.string == "is":
        stream.advance()
        if stream.match_name("not"):
            return "is not"
        return "is"

    if current.type == token.NAME and current.string == "not":
        if stream.peek(1) and stream.peek(1).type == token.NAME and stream.peek(1).string == "in":
            stream.advance()
            stream.advance()
            return "not in"
        return None

    if current.type == token.NAME and current.string == "in":
        stream.advance()
        return "in"

    return None


def _parse_additive_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    expression = _parse_multiplicative_expression(stream, source)
    while True:
        current = stream.peek()
        if current and current.type == token.OP and current.string in {"+", "-"}:
            operator = current.string
            stream.advance()
            right = _parse_multiplicative_expression(stream, source)
            expression = BinaryExpression(
                source=source,
                left=expression,
                operator=operator,
                right=right,
            )
            continue
        return expression


def _parse_multiplicative_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    expression = _parse_unary_expression(stream, source)
    while True:
        current = stream.peek()
        if current and current.type == token.OP and current.string in {"*", "/", "%"}:
            operator = current.string
            stream.advance()
            right = _parse_unary_expression(stream, source)
            expression = BinaryExpression(
                source=source,
                left=expression,
                operator=operator,
                right=right,
            )
            continue
        return expression


def _parse_unary_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    current = stream.peek()
    if current and current.type == token.OP and current.string in {"+", "-"}:
        operator = current.string
        stream.advance()
        operand = _parse_unary_expression(stream, source)
        return UnaryExpression(source=source, operator=operator, operand=operand)
    return _parse_postfix_expression(stream, source)


def _parse_postfix_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    expression = _parse_primary_expression(stream, source)

    while True:
        if stream.match_op("("):
            arguments, starred_arguments, keyword_arguments, double_starred_arguments = _parse_argument_list(stream, source)
            expression = CallExpression(
                source=source,
                function=expression,
                arguments=arguments,
                starred_arguments=starred_arguments,
                keyword_arguments=keyword_arguments,
                double_starred_arguments=double_starred_arguments,
            )
            continue

        if stream.match_op("."):
            attribute = stream.advance()
            if attribute.type != token.NAME:
                raise UnsupportedPytonyExpressionSyntaxError("Attributo non valido dopo `.`.")
            expression = AttributeExpression(source=source, value=expression, attribute=attribute.string)
            continue

        if stream.match_op("["):
            expression = _parse_bracket_access(stream, source, expression)
            continue

        return expression


def _parse_argument_list(
    stream: _ExpressionTokenStream,
    source: str,
) -> tuple[list[Expression], list[Expression], list[KeywordArgument], list[Expression]]:
    arguments: list[Expression] = []
    starred_arguments: list[Expression] = []
    keyword_arguments: list[KeywordArgument] = []
    double_starred_arguments: list[Expression] = []
    if stream.match_op(")"):
        return arguments, starred_arguments, keyword_arguments, double_starred_arguments

    seen_keyword = False
    seen_double_star = False

    while True:
        if stream.match_op("**"):
            seen_keyword = True
            seen_double_star = True
            double_starred_arguments.append(DoubleStarredExpression(
                source=source,
                value=_parse_lambda_expression(stream, source),
            ))
        elif stream.match_op("*"):
            if seen_keyword:
                raise UnsupportedPytonyExpressionSyntaxError(
                    "Gli unpack `*` devono arrivare prima degli argomenti nominati."
                )
            starred_arguments.append(StarredExpression(
                source=source,
                value=_parse_lambda_expression(stream, source),
            ))
        elif _looks_like_keyword_argument(stream):
            seen_keyword = True
            name = stream.advance().string
            stream.advance()
            keyword_arguments.append(
                KeywordArgument(name=name, value=_parse_lambda_expression(stream, source))
            )
        else:
            if seen_keyword or seen_double_star:
                raise UnsupportedPytonyExpressionSyntaxError(
                    "Gli argomenti posizionali non possono venire dopo quelli nominati o `**`."
                )
            first = _parse_lambda_expression(stream, source)
            if (
                not arguments
                and not starred_arguments
                and not keyword_arguments
                and not double_starred_arguments
                and stream.peek()
                and stream.peek().type == token.NAME
                and stream.peek().string == "for"
            ):
                clauses = [_parse_comprehension_clause(stream, source)]
                while stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
                    clauses.append(_parse_comprehension_clause(stream, source))
                arguments.append(GeneratorExpression(source=source, element=first, clauses=clauses))
                if not stream.match_op(")"):
                    raise UnsupportedPytonyExpressionSyntaxError(
                        "Generator expression come argomento deve chiudersi subito."
                    )
                return arguments, starred_arguments, keyword_arguments, double_starred_arguments

            arguments.append(first)
        if stream.match_op(")"):
            return arguments, starred_arguments, keyword_arguments, double_starred_arguments
        if not stream.match_op(","):
            raise UnsupportedPytonyExpressionSyntaxError("Argomenti funzione non validi.")
        if stream.match_op(")"):
            return arguments, starred_arguments, keyword_arguments, double_starred_arguments


def _parse_primary_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    current = stream.peek()
    if current is None:
        raise UnsupportedPytonyExpressionSyntaxError("Espressione vuota.")

    if current.type == token.NAME:
        stream.advance()
        if current.string in {"True", "False", "None"}:
            return LiteralExpression(source=current.string, value_source=current.string)
        return NameExpression(source=current.string, identifier=current.string)

    if current.type in {token.NUMBER, token.STRING}:
        stream.advance()
        return LiteralExpression(source=current.string, value_source=current.string)

    if stream.match_op("["):
        return _parse_list_like_expression(stream, source)

    if stream.match_op("{"):
        return _parse_brace_expression(stream, source)

    if stream.match_op("("):
        return _parse_parenthesized_expression(stream, source)

    raise UnsupportedPytonyExpressionSyntaxError(
        f"Espressione primaria non supportata: `{current.string}`."
    )


def _parse_list_like_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    if stream.match_op("]"):
        return ListExpression(source=source, elements=[])

    first = _parse_starred_list_element(stream, source)
    if stream.match_name("for"):
        if isinstance(first, (StarredExpression, DoubleStarredExpression)):
            raise UnsupportedPytonyExpressionSyntaxError("Le comprehension non supportano unpack come elemento.")
        clauses = [_parse_comprehension_clause(stream, source, already_consumed_for=True)]
        while stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
            stream.advance()
            clauses.append(_parse_comprehension_clause(stream, source, already_consumed_for=True))
        if not stream.match_op("]"):
            raise UnsupportedPytonyExpressionSyntaxError("List comprehension non chiusa.")
        return ListComprehensionExpression(source=source, element=first, clauses=clauses)

    elements = [first]
    while True:
        if stream.match_op("]"):
            return ListExpression(source=source, elements=elements)
        if not stream.match_op(","):
            raise UnsupportedPytonyExpressionSyntaxError("Lista non valida.")
        if stream.match_op("]"):
            return ListExpression(source=source, elements=elements)
        elements.append(_parse_starred_list_element(stream, source))


def _parse_parenthesized_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    if stream.match_op(")"):
        return TupleExpression(source=source, elements=[])

    first = _parse_starred_list_element(stream, source)
    if stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
        if isinstance(first, (StarredExpression, DoubleStarredExpression)):
            raise UnsupportedPytonyExpressionSyntaxError("Le generator expression non supportano unpack come elemento.")
        clauses = [_parse_comprehension_clause(stream, source)]
        while stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
            clauses.append(_parse_comprehension_clause(stream, source))
        if not stream.match_op(")"):
            raise UnsupportedPytonyExpressionSyntaxError("Generator expression non chiusa.")
        return GeneratorExpression(source=source, element=first, clauses=clauses)

    if stream.match_op(")"):
        return GroupExpression(source=source, expression=first)

    if not stream.match_op(","):
        raise UnsupportedPytonyExpressionSyntaxError("Parentesi non chiusa.")

    elements = [first]
    while True:
        if stream.match_op(")"):
            return TupleExpression(source=source, elements=elements)
        elements.append(_parse_starred_list_element(stream, source))
        if stream.match_op(")"):
            return TupleExpression(source=source, elements=elements)
        if not stream.match_op(","):
            raise UnsupportedPytonyExpressionSyntaxError("Tupla non valida.")


def _parse_brace_expression(stream: _ExpressionTokenStream, source: str) -> Expression:
    if stream.match_op("}"):
        return DictExpression(source=source, entries=[])

    if stream.match_op("**"):
        entries = [DictEntry(key=None, value=_parse_lambda_expression(stream, source), is_unpack=True)]
        while True:
            if stream.match_op("}"):
                return DictExpression(source=source, entries=entries)
            if not stream.match_op(","):
                raise UnsupportedPytonyExpressionSyntaxError("Dizionario non valido.")
            if stream.match_op("}"):
                return DictExpression(source=source, entries=entries)
            if not stream.match_op("**"):
                raise UnsupportedPytonyExpressionSyntaxError(
                    "Dopo un unpack `**` in un dizionario serve un'altra entry valida."
                )
            entries.append(DictEntry(key=None, value=_parse_lambda_expression(stream, source), is_unpack=True))

    first = _parse_lambda_expression(stream, source)
    if stream.match_op(":"):
        first_value = _parse_lambda_expression(stream, source)
        if stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
            clauses = [_parse_comprehension_clause(stream, source)]
            while stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
                clauses.append(_parse_comprehension_clause(stream, source))
            if not stream.match_op("}"):
                raise UnsupportedPytonyExpressionSyntaxError("Dict comprehension non chiusa.")
            return DictComprehensionExpression(
                source=source,
                key=first,
                value=first_value,
                clauses=clauses,
            )

        entries = [DictEntry(key=first, value=first_value)]
        while True:
            if stream.match_op("}"):
                return DictExpression(source=source, entries=entries)
            if not stream.match_op(","):
                raise UnsupportedPytonyExpressionSyntaxError("Dizionario non valido.")
            if stream.match_op("}"):
                return DictExpression(source=source, entries=entries)
            if stream.match_op("**"):
                entries.append(DictEntry(key=None, value=_parse_lambda_expression(stream, source), is_unpack=True))
                continue
            key = _parse_lambda_expression(stream, source)
            if not stream.match_op(":"):
                raise UnsupportedPytonyExpressionSyntaxError("Entry dizionario non valida.")
            value = _parse_lambda_expression(stream, source)
            entries.append(DictEntry(key=key, value=value))

    if stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
        if isinstance(first, (StarredExpression, DoubleStarredExpression)):
            raise UnsupportedPytonyExpressionSyntaxError("Le set comprehension non supportano unpack come elemento.")
        clauses = [_parse_comprehension_clause(stream, source)]
        while stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "for":
            clauses.append(_parse_comprehension_clause(stream, source))
        if not stream.match_op("}"):
            raise UnsupportedPytonyExpressionSyntaxError("Set comprehension non chiuso.")
        return SetComprehensionExpression(source=source, element=first, clauses=clauses)

    elements = [first]
    while True:
        if stream.match_op("}"):
            return SetExpression(source=source, elements=elements)
        if not stream.match_op(","):
            raise UnsupportedPytonyExpressionSyntaxError("Set non valido.")
        if stream.match_op("}"):
            return SetExpression(source=source, elements=elements)
        elements.append(_parse_starred_list_element(stream, source))


def _parse_comprehension_clause(
    stream: _ExpressionTokenStream,
    source: str,
    *,
    already_consumed_for: bool = False,
) -> ComprehensionClause:
    if not already_consumed_for and not stream.match_name("for"):
        raise UnsupportedPytonyExpressionSyntaxError("Comprehension senza `for`.")

    target_tokens: list[str] = []
    while True:
        current = stream.peek()
        if current is None:
            raise UnsupportedPytonyExpressionSyntaxError("Comprehension incompleta.")
        if current.type == token.NAME and current.string == "in":
            break
        target_tokens.append(stream.advance().string)

    if not stream.match_name("in"):
        raise UnsupportedPytonyExpressionSyntaxError("Comprehension senza `in`.")

    target = _normalize_binding_target(" ".join(target_tokens))
    if not target:
        raise UnsupportedPytonyExpressionSyntaxError("Target comprehension vuoto.")

    iterator = _parse_lambda_expression(stream, source)
    conditions: list[Expression] = []
    while stream.peek() and stream.peek().type == token.NAME and stream.peek().string == "if":
        stream.advance()
        conditions.append(_parse_lambda_expression(stream, source))

    return ComprehensionClause(target=target, iterator=iterator, conditions=conditions)


def _parse_bracket_access(
    stream: _ExpressionTokenStream,
    source: str,
    value: Expression,
) -> Expression:
    if stream.match_op(":"):
        stop = None
        step = None
        if not _peek_closing_bracket(stream) and not _peek_colon(stream):
            stop = _parse_lambda_expression(stream, source)
        if stream.match_op(":"):
            if not _peek_closing_bracket(stream):
                step = _parse_lambda_expression(stream, source)
        if not stream.match_op("]"):
            raise UnsupportedPytonyExpressionSyntaxError("Slice non chiuso.")
        return SliceExpression(source=source, value=value, start=None, stop=stop, step=step)

    first = _parse_lambda_expression(stream, source)
    if stream.match_op(":"):
        stop = None
        step = None
        if not _peek_closing_bracket(stream) and not _peek_colon(stream):
            stop = _parse_lambda_expression(stream, source)
        if stream.match_op(":"):
            if not _peek_closing_bracket(stream):
                step = _parse_lambda_expression(stream, source)
        if not stream.match_op("]"):
            raise UnsupportedPytonyExpressionSyntaxError("Slice non chiuso.")
        return SliceExpression(source=source, value=value, start=first, stop=stop, step=step)

    if not stream.match_op("]"):
        raise UnsupportedPytonyExpressionSyntaxError("Indicizzazione non chiusa.")
    return IndexExpression(source=source, value=value, index=first)


def _peek_closing_bracket(stream: _ExpressionTokenStream) -> bool:
    current = stream.peek()
    return current is not None and current.type == token.OP and current.string == "]"


def _peek_colon(stream: _ExpressionTokenStream) -> bool:
    current = stream.peek()
    return current is not None and current.type == token.OP and current.string == ":"


def _looks_like_keyword_argument(stream: _ExpressionTokenStream) -> bool:
    current = stream.peek()
    next_token = stream.peek(1)
    return (
        current is not None
        and next_token is not None
        and current.type == token.NAME
        and next_token.type == token.OP
        and next_token.string == "="
    )


def _parse_starred_list_element(stream: _ExpressionTokenStream, source: str) -> Expression:
    if stream.match_op("**"):
        raise UnsupportedPytonyExpressionSyntaxError("`**` non e valido in questa collezione.")
    if stream.match_op("*"):
        return StarredExpression(source=source, value=_parse_lambda_expression(stream, source))
    return _parse_lambda_expression(stream, source)


def _format_python_syntax_error(error: SyntaxError) -> str:
    line = error.lineno or 1
    column = error.offset or 1
    detail = error.msg or "Sintassi non valida."
    return f"Sintassi Pytony non valida: {detail} (riga {line}, colonna {column})"


def _format_native_syntax_error(
    detail: str,
    token_info: tokenize.TokenInfo,
    lines: list[str],
) -> str:
    line = token_info.start[0] or 1
    column = token_info.start[1] + 1
    line_text = ""
    if 1 <= line <= len(lines):
        line_text = lines[line - 1]

    pointer = ""
    if line_text:
        caret_padding = max(column - 1, 0)
        pointer = f"\n    {line_text}\n    {' ' * caret_padding}^"

    return f"Sintassi Pytony non valida: {detail} (riga {line}, colonna {column}){pointer}"


def _convert_augassign_operator(node: ast.operator) -> str:
    operator_map = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.Mod: "%",
        ast.FloorDiv: "//",
        ast.MatMult: "@",
        ast.BitAnd: "&",
        ast.BitOr: "|",
        ast.BitXor: "^",
        ast.RShift: ">>",
        ast.LShift: "<<",
        ast.Pow: "**",
    }
    for operator_type, symbol in operator_map.items():
        if isinstance(node, operator_type):
            return symbol
    raise UnsupportedPytonySyntaxError(
        f"Operatore di assegnazione aumentata non supportato: `{type(node).__name__}`."
    )
