from __future__ import annotations

import pytest

from reportstudio.core.metrics.ast import BinaryOp, FunctionCall, Identifier, NumberLiteral, RawExpression, UnaryOp
from reportstudio.core.metrics.dsl_parser import DSLParseError, parse_expression_to_ast


@pytest.mark.parametrize(
    ("expr", "expected_type"),
    [
        ("1", NumberLiteral),
        ("123.45", NumberLiteral),
        ("revenue", Identifier),
        ("-1", UnaryOp),
        ("+cost", UnaryOp),
        ("1+2", BinaryOp),
        ("1+2*3", BinaryOp),
        ("(1+2)*3", BinaryOp),
        ("a/b-c", BinaryOp),
        ("sum(revenue)", FunctionCall),
        ("avg(sum(revenue))", FunctionCall),
        ("lag(revenue)", FunctionCall),
        ("lag(revenue,1)", FunctionCall),
        ("lag(sum(revenue),2)", FunctionCall),
        ("sum(revenue)+lag(cost,1)", BinaryOp),
        ("(sum(a)+sum(b))/(lag(c,2)-1)", BinaryOp),
        ("foo(bar(baz(1,2),3),4)", FunctionCall),
        ("x1 + _y2", BinaryOp),
        ("((a))", Identifier),
        ("-(a+b)", UnaryOp),
        ("((1+2)*(3+4))/5", BinaryOp),
    ],
)
def test_valid_expressions_parse(expr: str, expected_type: type[object]):
    ast = parse_expression_to_ast(expr)
    assert isinstance(ast, expected_type)


@pytest.mark.parametrize(
    "expr",
    [
        "",
        "1+",
        "sum(",
        "sum(,a)",
        "a**b",
        "a+)",
        "(a+b",
        "lag()",
        "lag(a, 1, 2)",
        "lag(a, b)",
        "a $ b",
    ],
)
def test_invalid_expressions_raise_e2001(expr: str):
    with pytest.raises(DSLParseError) as exc:
        parse_expression_to_ast(expr)
    msg = str(exc.value)
    assert "E2001" in msg
    assert "line" in msg and "col" in msg


def test_operator_precedence_ast_shape():
    ast = parse_expression_to_ast("1+2*3")
    assert isinstance(ast, BinaryOp)
    assert ast.op == "+"
    assert isinstance(ast.left, NumberLiteral)
    assert isinstance(ast.right, BinaryOp)
    assert ast.right.op == "*"


def test_nested_function_args_shape():
    ast = parse_expression_to_ast("avg(sum(revenue)+lag(cost,2))")
    assert isinstance(ast, FunctionCall)
    assert ast.name == "avg"
    assert len(ast.args) == 1
    assert isinstance(ast.args[0], BinaryOp)


def test_fallback_to_p1_dsl_basic_layer():
    ast = parse_expression_to_ast("a +", fallback_to_dsl_basic=True)
    assert isinstance(ast, RawExpression)
    assert ast.text == "a +"
