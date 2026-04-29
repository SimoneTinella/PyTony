from __future__ import annotations

from .ast_nodes import (
    AssignStatement,
    AssertStatement,
    AttributeExpression,
    AugAssignStatement,
    BinaryExpression,
    BreakStatement,
    BoolExpression,
    CallExpression,
    ClassDefStatement,
    ComprehensionClause,
    ContinueStatement,
    CompareExpression,
    ComparePart,
    DictComprehensionExpression,
    DictExpression,
    ExceptHandler,
    ExprStatement,
    ForStatement,
    FunctionDefStatement,
    GeneratorExpression,
    GroupExpression,
    ImportFromStatement,
    ImportStatement,
    IndexExpression,
    IfStatement,
    ImportAlias,
    LambdaExpression,
    LiteralExpression,
    ListComprehensionExpression,
    ListExpression,
    Module,
    MatchCase,
    MatchStatement,
    NameExpression,
    KeywordArgument,
    PassStatement,
    RawExpression,
    RaiseStatement,
    ReturnStatement,
    SetComprehensionExpression,
    SetExpression,
    SliceExpression,
    StarredExpression,
    Statement,
    TryStatement,
    TupleExpression,
    UnaryExpression,
    WithItem,
    WithStatement,
    WhileStatement,
    DoubleStarredExpression,
)


INDENT = "    "


def lower_module(module: Module) -> str:
    lines: list[str] = []
    for statement in module.body:
        lines.extend(_lower_statement(statement, 0))
    return "\n".join(lines) + ("\n" if lines else "")


def _lower_statement(statement: Statement, level: int) -> list[str]:
    indent = INDENT * level

    if isinstance(statement, ImportStatement):
        aliases = ", ".join(_lower_import_alias(alias) for alias in statement.aliases)
        return [f"{indent}import {aliases}"]

    if isinstance(statement, ImportFromStatement):
        module = "." * statement.level + (statement.module or "")
        aliases = ", ".join(_lower_import_alias(alias) for alias in statement.aliases)
        return [f"{indent}from {module} import {aliases}"]

    if isinstance(statement, ExprStatement):
        return [f"{indent}{_lower_expression(statement.expression)}"]

    if isinstance(statement, AssignStatement):
        targets = " = ".join(statement.targets)
        return [f"{indent}{targets} = {_lower_expression(statement.value)}"]

    if isinstance(statement, AugAssignStatement):
        return [f"{indent}{statement.target} {statement.operator}= {_lower_expression(statement.value)}"]

    if isinstance(statement, PassStatement):
        return [f"{indent}pass"]

    if isinstance(statement, BreakStatement):
        return [f"{indent}break"]

    if isinstance(statement, ContinueStatement):
        return [f"{indent}continue"]

    if isinstance(statement, ReturnStatement):
        if statement.value is None:
            return [f"{indent}return"]
        return [f"{indent}return {_lower_expression(statement.value)}"]

    if isinstance(statement, RaiseStatement):
        if statement.exception is None:
            return [f"{indent}raise"]
        if statement.cause is None:
            return [f"{indent}raise {_lower_expression(statement.exception)}"]
        return [
            f"{indent}raise {_lower_expression(statement.exception)} from {_lower_expression(statement.cause)}"
        ]

    if isinstance(statement, AssertStatement):
        if statement.message is None:
            return [f"{indent}assert {_lower_expression(statement.test)}"]
        return [f"{indent}assert {_lower_expression(statement.test)}, {_lower_expression(statement.message)}"]

    if isinstance(statement, IfStatement):
        return _lower_if(statement, level)

    if isinstance(statement, WhileStatement):
        lines = [f"{indent}while {_lower_expression(statement.test)}:"]
        lines.extend(_lower_block(statement.body, level + 1))
        if statement.orelse:
            lines.append(f"{indent}else:")
            lines.extend(_lower_block(statement.orelse, level + 1))
        return lines

    if isinstance(statement, ForStatement):
        lines = [f"{indent}for {statement.target} in {_lower_expression(statement.iterator)}:"]
        lines.extend(_lower_block(statement.body, level + 1))
        if statement.orelse:
            lines.append(f"{indent}else:")
            lines.extend(_lower_block(statement.orelse, level + 1))
        return lines

    if isinstance(statement, FunctionDefStatement):
        parameters = ", ".join(_lower_parameter(parameter) for parameter in statement.parameters)
        annotation = f" -> {statement.return_annotation}" if statement.return_annotation else ""
        lines = [f"{indent}def {statement.name}({parameters}){annotation}:"]
        lines.extend(_lower_block(statement.body, level + 1))
        return lines

    if isinstance(statement, ClassDefStatement):
        bases = ""
        if statement.bases:
            bases = f"({', '.join(_lower_expression(base) for base in statement.bases)})"
        lines = [f"{indent}class {statement.name}{bases}:"]
        lines.extend(_lower_block(statement.body, level + 1))
        return lines

    if isinstance(statement, WithStatement):
        items = ", ".join(_lower_with_item(item) for item in statement.items)
        lines = [f"{indent}with {items}:"]
        lines.extend(_lower_block(statement.body, level + 1))
        return lines

    if isinstance(statement, TryStatement):
        lines = [f"{indent}try:"]
        lines.extend(_lower_block(statement.body, level + 1))
        for handler in statement.handlers:
            lines.extend(_lower_except_handler(handler, level))
        if statement.orelse:
            lines.append(f"{indent}else:")
            lines.extend(_lower_block(statement.orelse, level + 1))
        if statement.finalbody:
            lines.append(f"{indent}finally:")
            lines.extend(_lower_block(statement.finalbody, level + 1))
        return lines

    if isinstance(statement, MatchStatement):
        lines = [f"{indent}match {_lower_expression(statement.subject)}:"]
        for case in statement.cases:
            lines.extend(_lower_match_case(case, level + 1))
        return lines

    raise TypeError(f"Unsupported statement for lowering: {type(statement).__name__}")


def _lower_if(statement: IfStatement, level: int) -> list[str]:
    indent = INDENT * level
    lines = [f"{indent}if {_lower_expression(statement.test)}:"]
    lines.extend(_lower_block(statement.body, level + 1))

    if not statement.orelse:
        return lines

    if len(statement.orelse) == 1 and isinstance(statement.orelse[0], IfStatement):
        nested_if = statement.orelse[0]
        lines.append(f"{indent}elif {_lower_expression(nested_if.test)}:")
        lines.extend(_lower_block(nested_if.body, level + 1))
        if nested_if.orelse:
            lines.extend(_lower_else_tail(nested_if.orelse, level))
        return lines

    lines.extend(_lower_else_tail(statement.orelse, level))
    return lines


def _lower_else_tail(orelse: list[Statement], level: int) -> list[str]:
    indent = INDENT * level
    lines = [f"{indent}else:"]
    lines.extend(_lower_block(orelse, level + 1))
    return lines


def _lower_block(statements: list[Statement], level: int) -> list[str]:
    if not statements:
        return [f"{INDENT * level}pass"]

    lines: list[str] = []
    for child in statements:
        lines.extend(_lower_statement(child, level))
    return lines


def _lower_parameter(parameter: object) -> str:
    annotation = getattr(parameter, "annotation", None)
    name = getattr(parameter, "name")
    if annotation is None:
        return name
    return f"{name}: {annotation}"


def _lower_with_item(item: WithItem) -> str:
    context = _lower_expression(item.context)
    if item.target is None:
        return context
    return f"{context} as {item.target}"


def _lower_except_handler(handler: ExceptHandler, level: int) -> list[str]:
    indent = INDENT * level
    header = "except"
    if handler.exception is not None:
        header += f" {_lower_expression(handler.exception)}"
    if handler.target is not None:
        header += f" as {handler.target}"
    header += ":"
    lines = [f"{indent}{header}"]
    lines.extend(_lower_block(handler.body, level + 1))
    return lines


def _lower_match_case(case: MatchCase, level: int) -> list[str]:
    indent = INDENT * level
    header = f"{indent}case {case.pattern_source}"
    if case.guard is not None:
        header += f" if {_lower_expression(case.guard)}"
    header += ":"
    lines = [header]
    lines.extend(_lower_block(case.body, level + 1))
    return lines


def _lower_expression(expression: object) -> str:
    if isinstance(expression, RawExpression):
        return expression.source

    if isinstance(expression, NameExpression):
        return expression.identifier

    if isinstance(expression, LiteralExpression):
        return expression.value_source

    if isinstance(expression, StarredExpression):
        return f"*{_lower_expression(expression.value)}"

    if isinstance(expression, DoubleStarredExpression):
        return f"**{_lower_expression(expression.value)}"

    if isinstance(expression, UnaryExpression):
        operand = _lower_expression(expression.operand)
        if expression.operator == "not":
            return f"not {operand}"
        return f"{expression.operator}{operand}"

    if isinstance(expression, BinaryExpression):
        left = _lower_expression(expression.left)
        right = _lower_expression(expression.right)
        return f"{left} {expression.operator} {right}"

    if isinstance(expression, BoolExpression):
        return f" {expression.operator} ".join(_lower_expression(value) for value in expression.values)

    if isinstance(expression, CompareExpression):
        pieces = [_lower_expression(expression.left)]
        for comparison in expression.comparisons:
            pieces.append(_lower_compare_part(comparison))
        return " ".join(pieces)

    if isinstance(expression, CallExpression):
        function = _lower_expression(expression.function)
        parts = [_lower_expression(argument) for argument in expression.arguments]
        parts.extend(_lower_expression(argument) for argument in expression.starred_arguments)
        parts.extend(_lower_keyword_argument(argument) for argument in expression.keyword_arguments)
        parts.extend(_lower_expression(argument) for argument in expression.double_starred_arguments)
        arguments = ", ".join(parts)
        return f"{function}({arguments})"

    if isinstance(expression, AttributeExpression):
        return f"{_lower_expression(expression.value)}.{expression.attribute}"

    if isinstance(expression, IndexExpression):
        return f"{_lower_expression(expression.value)}[{_lower_expression(expression.index)}]"

    if isinstance(expression, SliceExpression):
        start = _lower_optional_expression(expression.start)
        stop = _lower_optional_expression(expression.stop)
        if expression.step is None:
            slice_body = f"{start}:{stop}"
        else:
            slice_body = f"{start}:{stop}:{_lower_expression(expression.step)}"
        return f"{_lower_expression(expression.value)}[{slice_body}]"

    if isinstance(expression, ListExpression):
        return f"[{', '.join(_lower_expression(element) for element in expression.elements)}]"

    if isinstance(expression, TupleExpression):
        if not expression.elements:
            return "()"
        if len(expression.elements) == 1:
            return f"({_lower_expression(expression.elements[0])},)"
        return f"({', '.join(_lower_expression(element) for element in expression.elements)})"

    if isinstance(expression, DictExpression):
        entries = []
        for entry in expression.entries:
            if entry.is_unpack:
                entries.append(f"**{_lower_expression(entry.value)}")
            else:
                entries.append(f"{_lower_expression(entry.key)}: {_lower_expression(entry.value)}")
        return f"{{{', '.join(entries)}}}"

    if isinstance(expression, DictComprehensionExpression):
        clauses = " ".join(_lower_comprehension_clause(clause) for clause in expression.clauses)
        key = _lower_expression(expression.key)
        value = _lower_expression(expression.value)
        return f"{{{key}: {value} {clauses}}}"

    if isinstance(expression, SetExpression):
        return f"{{{', '.join(_lower_expression(element) for element in expression.elements)}}}"

    if isinstance(expression, SetComprehensionExpression):
        clauses = " ".join(_lower_comprehension_clause(clause) for clause in expression.clauses)
        return f"{{{_lower_expression(expression.element)} {clauses}}}"

    if isinstance(expression, ListComprehensionExpression):
        clauses = " ".join(_lower_comprehension_clause(clause) for clause in expression.clauses)
        return f"[{_lower_expression(expression.element)} {clauses}]"

    if isinstance(expression, GeneratorExpression):
        clauses = " ".join(_lower_comprehension_clause(clause) for clause in expression.clauses)
        return f"({_lower_expression(expression.element)} {clauses})"

    if isinstance(expression, LambdaExpression):
        parameters = ", ".join(expression.parameters)
        prefix = "lambda" if not parameters else f"lambda {parameters}"
        return f"{prefix}: {_lower_expression(expression.body)}"

    if isinstance(expression, GroupExpression):
        return f"({_lower_expression(expression.expression)})"

    raise TypeError(f"Unsupported expression for lowering: {type(expression).__name__}")


def _lower_compare_part(comparison: ComparePart) -> str:
    return f"{comparison.operator} {_lower_expression(comparison.right)}"


def _lower_comprehension_clause(clause: ComprehensionClause) -> str:
    result = f"for {clause.target} in {_lower_expression(clause.iterator)}"
    if clause.conditions:
        result = f"{result} " + " ".join(
            f"if {_lower_expression(condition)}" for condition in clause.conditions
        )
    return result


def _lower_optional_expression(expression: object | None) -> str:
    if expression is None:
        return ""
    return _lower_expression(expression)


def _lower_keyword_argument(argument: KeywordArgument) -> str:
    return f"{argument.name}={_lower_expression(argument.value)}"


def _lower_import_alias(alias: ImportAlias) -> str:
    if alias.asname is None:
        return alias.name
    return f"{alias.name} as {alias.asname}"
