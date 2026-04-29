from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Expression:
    source: str


@dataclass(slots=True)
class RawExpression(Expression):
    pass


@dataclass(slots=True)
class NameExpression(Expression):
    identifier: str


@dataclass(slots=True)
class LiteralExpression(Expression):
    value_source: str


@dataclass(slots=True)
class StarredExpression(Expression):
    value: Expression


@dataclass(slots=True)
class DoubleStarredExpression(Expression):
    value: Expression


@dataclass(slots=True)
class UnaryExpression(Expression):
    operator: str
    operand: Expression


@dataclass(slots=True)
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass(slots=True)
class BoolExpression(Expression):
    operator: str
    values: list[Expression] = field(default_factory=list)


@dataclass(slots=True)
class ComparePart:
    operator: str
    right: Expression


@dataclass(slots=True)
class CompareExpression(Expression):
    left: Expression
    comparisons: list[ComparePart] = field(default_factory=list)


@dataclass(slots=True)
class CallExpression(Expression):
    function: Expression
    arguments: list[Expression] = field(default_factory=list)
    starred_arguments: list[Expression] = field(default_factory=list)
    keyword_arguments: list["KeywordArgument"] = field(default_factory=list)
    double_starred_arguments: list[Expression] = field(default_factory=list)


@dataclass(slots=True)
class KeywordArgument:
    name: str
    value: Expression


@dataclass(slots=True)
class AttributeExpression(Expression):
    value: Expression
    attribute: str


@dataclass(slots=True)
class IndexExpression(Expression):
    value: Expression
    index: Expression


@dataclass(slots=True)
class SliceExpression(Expression):
    value: Expression
    start: Expression | None = None
    stop: Expression | None = None
    step: Expression | None = None


@dataclass(slots=True)
class ListExpression(Expression):
    elements: list[Expression] = field(default_factory=list)


@dataclass(slots=True)
class TupleExpression(Expression):
    elements: list[Expression] = field(default_factory=list)


@dataclass(slots=True)
class DictEntry:
    key: Expression | None
    value: Expression
    is_unpack: bool = False


@dataclass(slots=True)
class DictExpression(Expression):
    entries: list[DictEntry] = field(default_factory=list)


@dataclass(slots=True)
class SetExpression(Expression):
    elements: list[Expression] = field(default_factory=list)


@dataclass(slots=True)
class ComprehensionClause:
    target: str
    iterator: Expression
    conditions: list[Expression] = field(default_factory=list)


@dataclass(slots=True)
class ListComprehensionExpression(Expression):
    element: Expression
    clauses: list[ComprehensionClause] = field(default_factory=list)


@dataclass(slots=True)
class DictComprehensionExpression(Expression):
    key: Expression
    value: Expression
    clauses: list[ComprehensionClause] = field(default_factory=list)


@dataclass(slots=True)
class SetComprehensionExpression(Expression):
    element: Expression
    clauses: list[ComprehensionClause] = field(default_factory=list)


@dataclass(slots=True)
class GeneratorExpression(Expression):
    element: Expression
    clauses: list[ComprehensionClause] = field(default_factory=list)


@dataclass(slots=True)
class LambdaExpression(Expression):
    parameters: list[str] = field(default_factory=list)
    body: Expression | None = None


@dataclass(slots=True)
class GroupExpression(Expression):
    expression: Expression


@dataclass(slots=True)
class Parameter:
    name: str
    annotation: str | None = None


@dataclass(slots=True)
class WithItem:
    context: Expression
    target: str | None = None


@dataclass(slots=True)
class ExceptHandler:
    exception: Expression | None = None
    target: str | None = None
    body: list["Statement"] = field(default_factory=list)


@dataclass(slots=True)
class MatchPattern:
    pass


@dataclass(slots=True)
class RawMatchPattern(MatchPattern):
    source: str


@dataclass(slots=True)
class LiteralMatchPattern(MatchPattern):
    value_source: str


@dataclass(slots=True)
class CaptureMatchPattern(MatchPattern):
    name: str


@dataclass(slots=True)
class WildcardMatchPattern(MatchPattern):
    pass


@dataclass(slots=True)
class ValueMatchPattern(MatchPattern):
    value: Expression


@dataclass(slots=True)
class StarMatchPattern(MatchPattern):
    name: str | None = None


@dataclass(slots=True)
class SequenceMatchPattern(MatchPattern):
    kind: str
    elements: list["MatchPattern"] = field(default_factory=list)


@dataclass(slots=True)
class KeywordMatchPattern:
    name: str
    pattern: MatchPattern


@dataclass(slots=True)
class ClassMatchPattern(MatchPattern):
    class_name: Expression
    patterns: list[MatchPattern] = field(default_factory=list)
    keyword_patterns: list[KeywordMatchPattern] = field(default_factory=list)


@dataclass(slots=True)
class OrMatchPattern(MatchPattern):
    patterns: list[MatchPattern] = field(default_factory=list)


@dataclass(slots=True)
class AsMatchPattern(MatchPattern):
    pattern: MatchPattern
    name: str


@dataclass(slots=True)
class MatchCase:
    pattern: MatchPattern
    pattern_source: str
    guard: Expression | None = None
    body: list["Statement"] = field(default_factory=list)


@dataclass(slots=True)
class Statement:
    pass


@dataclass(slots=True)
class ImportAlias:
    name: str
    asname: str | None = None


@dataclass(slots=True)
class ImportStatement(Statement):
    aliases: list[ImportAlias] = field(default_factory=list)


@dataclass(slots=True)
class ImportFromStatement(Statement):
    module: str | None
    aliases: list[ImportAlias] = field(default_factory=list)
    level: int = 0


@dataclass(slots=True)
class ExprStatement(Statement):
    expression: Expression


@dataclass(slots=True)
class AssignStatement(Statement):
    targets: list[str]
    value: Expression


@dataclass(slots=True)
class AugAssignStatement(Statement):
    target: str
    operator: str
    value: Expression


@dataclass(slots=True)
class PassStatement(Statement):
    pass


@dataclass(slots=True)
class BreakStatement(Statement):
    pass


@dataclass(slots=True)
class ContinueStatement(Statement):
    pass


@dataclass(slots=True)
class ReturnStatement(Statement):
    value: Expression | None = None


@dataclass(slots=True)
class RaiseStatement(Statement):
    exception: Expression | None = None
    cause: Expression | None = None


@dataclass(slots=True)
class AssertStatement(Statement):
    test: Expression
    message: Expression | None = None


@dataclass(slots=True)
class IfStatement(Statement):
    test: Expression
    body: list[Statement] = field(default_factory=list)
    orelse: list[Statement] = field(default_factory=list)


@dataclass(slots=True)
class WhileStatement(Statement):
    test: Expression
    body: list[Statement] = field(default_factory=list)
    orelse: list[Statement] = field(default_factory=list)


@dataclass(slots=True)
class ForStatement(Statement):
    target: str
    iterator: Expression
    body: list[Statement] = field(default_factory=list)
    orelse: list[Statement] = field(default_factory=list)


@dataclass(slots=True)
class FunctionDefStatement(Statement):
    name: str
    parameters: list[Parameter] = field(default_factory=list)
    body: list[Statement] = field(default_factory=list)
    return_annotation: str | None = None


@dataclass(slots=True)
class ClassDefStatement(Statement):
    name: str
    bases: list[Expression] = field(default_factory=list)
    body: list[Statement] = field(default_factory=list)


@dataclass(slots=True)
class WithStatement(Statement):
    items: list[WithItem] = field(default_factory=list)
    body: list[Statement] = field(default_factory=list)


@dataclass(slots=True)
class TryStatement(Statement):
    body: list[Statement] = field(default_factory=list)
    handlers: list[ExceptHandler] = field(default_factory=list)
    orelse: list[Statement] = field(default_factory=list)
    finalbody: list[Statement] = field(default_factory=list)


@dataclass(slots=True)
class MatchStatement(Statement):
    subject: Expression
    cases: list[MatchCase] = field(default_factory=list)


@dataclass(slots=True)
class Module:
    body: list[Statement] = field(default_factory=list)
