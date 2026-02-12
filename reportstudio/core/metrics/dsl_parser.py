"""Recursive-descent parser for ReportStudio metrics DSL -> AST."""

from __future__ import annotations

from dataclasses import dataclass
import re

from reportstudio.core.metrics.ast import BinaryOp, Expr, FunctionCall, Identifier, NumberLiteral, RawExpression, UnaryOp


class DSLParseError(ValueError):
    """Syntax error with error code and position details."""

    def __init__(self, message: str, *, token: str, line: int, col: int):
        self.code = "E2001"
        self.token = token
        self.line = line
        self.col = col
        full = f"E2001 at line {line}, col {col} near '{token}': {message}"
        super().__init__(full)


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    col: int


_TOKEN_RE = re.compile(
    r"""
    (?P<WS>\s+)
    |(?P<NUMBER>\d+(?:\.\d+)?)
    |(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
    |(?P<OP>[+\-*/(),])
    |(?P<BAD>.)
    """,
    re.VERBOSE,
)


def _tokenize(text: str) -> list[Token]:
    line = 1
    col = 1
    tokens: list[Token] = []
    for match in _TOKEN_RE.finditer(text):
        kind = match.lastgroup or "BAD"
        value = match.group()
        start_col = col

        if kind == "WS":
            pass
        elif kind == "BAD":
            raise DSLParseError("unexpected character", token=value, line=line, col=start_col)
        else:
            tkind = kind if kind != "OP" else value
            tokens.append(Token(tkind, value, line, start_col))

        for ch in value:
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1

    tokens.append(Token("EOF", "<eof>", line, col))
    return tokens


class _Parser:
    def __init__(self, text: str):
        self.tokens = _tokenize(text)
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def match(self, kind: str) -> bool:
        if self.current().kind == kind:
            self.pos += 1
            return True
        return False

    def expect(self, kind: str, message: str) -> Token:
        tok = self.current()
        if tok.kind != kind:
            raise DSLParseError(message, token=tok.value, line=tok.line, col=tok.col)
        self.pos += 1
        return tok

    def parse(self) -> Expr:
        expr = self.parse_expression()
        eof = self.current()
        if eof.kind != "EOF":
            raise DSLParseError("unexpected trailing token", token=eof.value, line=eof.line, col=eof.col)
        return expr

    def parse_expression(self) -> Expr:
        node = self.parse_term()
        while self.current().kind in {"+", "-"}:
            op = self.current().kind
            self.pos += 1
            right = self.parse_term()
            node = BinaryOp(op=op, left=node, right=right)
        return node

    def parse_term(self) -> Expr:
        node = self.parse_factor()
        while self.current().kind in {"*", "/"}:
            op = self.current().kind
            self.pos += 1
            right = self.parse_factor()
            node = BinaryOp(op=op, left=node, right=right)
        return node

    def parse_factor(self) -> Expr:
        tok = self.current()

        if tok.kind in {"+", "-"}:
            self.pos += 1
            return UnaryOp(op=tok.kind, operand=self.parse_factor())

        if tok.kind == "NUMBER":
            self.pos += 1
            return NumberLiteral(value=float(tok.value))

        if tok.kind == "IDENT":
            self.pos += 1
            name = tok.value
            if self.match("("):
                args = self.parse_call_args()
                if name.lower() == "lag":
                    self._validate_lag(args)
                return FunctionCall(name=name, args=args)
            return Identifier(name=name)

        if self.match("("):
            inner = self.parse_expression()
            self.expect(")", "missing closing parenthesis")
            return inner

        raise DSLParseError("expected number, identifier, function call or parenthesized expression", token=tok.value, line=tok.line, col=tok.col)

    def parse_call_args(self) -> list[Expr]:
        args: list[Expr] = []
        if self.match(")"):
            return args

        args.append(self.parse_expression())
        while self.match(","):
            args.append(self.parse_expression())
        self.expect(")", "missing ')' after function arguments")
        return args

    def _validate_lag(self, args: list[Expr]) -> None:
        if len(args) not in {1, 2}:
            tok = self.current()
            raise DSLParseError("lag() expects 1 or 2 arguments", token=tok.value, line=tok.line, col=tok.col)
        if len(args) == 2:
            offset = args[1]
            if not isinstance(offset, NumberLiteral) or int(offset.value) != offset.value:
                tok = self.current()
                raise DSLParseError(
                    "lag() second argument must be an integer literal",
                    token=tok.value,
                    line=tok.line,
                    col=tok.col,
                )


def dsl_basic_parse(expression: str) -> RawExpression:
    """P1 fallback/migration parser: preserve raw DSL without strict parsing."""

    return RawExpression(text=expression.strip())


def parse_expression_to_ast(expression: str, *, fallback_to_dsl_basic: bool = False) -> Expr:
    """Parse DSL expression into AST.

    When ``fallback_to_dsl_basic`` is True, syntax errors return a RawExpression node
    to preserve P1 compatibility for migration stages.
    """

    try:
        return _Parser(expression).parse()
    except DSLParseError:
        if fallback_to_dsl_basic:
            return dsl_basic_parse(expression)
        raise
