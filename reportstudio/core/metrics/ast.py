"""AST node definitions for metrics DSL expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class NumberLiteral:
    value: float


@dataclass(frozen=True)
class Identifier:
    name: str


@dataclass(frozen=True)
class UnaryOp:
    op: str
    operand: "Expr"


@dataclass(frozen=True)
class BinaryOp:
    op: str
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class FunctionCall:
    name: str
    args: list["Expr"]


@dataclass(frozen=True)
class RawExpression:
    """Fallback node that preserves the original DSL string (P1 dsl_basic layer)."""

    text: str


Expr = Union[NumberLiteral, Identifier, UnaryOp, BinaryOp, FunctionCall, RawExpression]
