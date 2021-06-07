from .parser import tokenize, parse
from .types import AstTree, TokenSubtype, TokenType, Iterator, Token

from operator import (add, sub, truediv,
                      mul, pow)
from copy import copy

from enum import IntEnum

LOW_PRIOR = 0
MID_PRIOR = 1
HIGH_PRIOR = 2
TOP_PRIOR = 3
MAX_PRIOR = 4


OPERATOR_SUBTYPES = {
    TokenSubtype.ADD: add,
    TokenSubtype.SUB: sub,

    TokenSubtype.MUL: mul,
    TokenSubtype.DIV: truediv,

    TokenSubtype.POW: pow
}


class SequenceType(IntEnum):
    BINARY_OP = 1
    UNARY_OP = 2

    CALL = 3
    BRACKETS = 4
    RESPONSE = 5


def get_priority(obj):
    if isinstance(obj, AstTree):
        return HIGH_PRIOR

    subtype = obj.subtype

    if (subtype == TokenSubtype.ADD) or \
            (subtype == TokenSubtype.SUB):
        return LOW_PRIOR
    elif (subtype == TokenSubtype.MUL) or \
            (subtype == TokenSubtype.DIV):
        return MID_PRIOR
    elif subtype == TokenSubtype.POW:
        return TOP_PRIOR

    return -1


class _PriorCls:
    def __init__(self, max_prior,
                 max_prior_pos, seq_type):
        self.max_prior = max_prior
        self.max_prior_pos = max_prior_pos
        self.seq_type = seq_type

        self.next_offset = 0


def is_token(obj):
    return isinstance(obj, Token)


def is_tree(obj):
    return isinstance(obj, AstTree)


def is_operator(obj):
    if not isinstance(obj, Token):
        return False

    return obj.type == TokenType.OPERATOR


def check_priority(priors, seq_type,
                   offset, operator):
    op_prior = get_priority(operator)

    if seq_type == SequenceType.CALL:
        op_prior = MAX_PRIOR
        priors.next_offset = 1
    elif seq_type == SequenceType.BRACKETS:
        op_prior = TOP_PRIOR
        priors.next_offset = 1
    elif seq_type == SequenceType.BINARY_OP:
        priors.next_offset = 2
    elif seq_type == SequenceType.UNARY_OP:
        priors.next_offset = 1

    if priors.max_prior < op_prior:
        priors.max_prior = op_prior
        priors.seq_type = seq_type
        priors.max_prior_pos = offset


def get_max_priority(it):
    offset = 0
    priors = _PriorCls(-1, -1, SequenceType.BINARY_OP)

    # next level of parsers shitty code, TODO: Refactor

    while not it.is_done(offset):
        first = it.peek(offset)
        second = it.peek(offset + 1)
        third = it.peek(offset + 2)

        if second is None:
            check_priority(priors, SequenceType.RESPONSE if is_token(first) else SequenceType.BRACKETS,
                           it.get_position(offset), first)

            break

        if is_token(first) and first.type == TokenType.ID and is_tree(second):
            check_priority(priors, SequenceType.CALL,
                           it.get_position(offset), first)
        elif is_operator(first):
            check_priority(priors, SequenceType.UNARY_OP,
                           it.get_position(offset), first)

            if is_tree(second):
                check_priority(priors, SequenceType.BRACKETS,
                               it.get_position(offset+1), second)

        if is_tree(first):
            check_priority(priors, SequenceType.BRACKETS,
                           it.get_position(offset), first)

        if is_tree(third):
            check_priority(priors, SequenceType.BRACKETS,
                           it.get_position(offset + 2), third)

        if is_operator(second):
            check_priority(priors, SequenceType.BINARY_OP,
                           it.get_position(offset), second)

        offset += priors.next_offset
        priors.next_offset = 0

    return priors


def perform_binary_operation(left, right,
                             operator, int_class):
    left.parse(int_class)
    right.parse(int_class)

    result = OPERATOR_SUBTYPES[operator.subtype](left.data, right.data)

    return Token(result, TokenType.NUMBER)


def perform_unary_operation(operator, right,
                            int_class):
    right.parse(int_class)

    if operator.subtype == TokenSubtype.ADD:
        return Token(+right.data, TokenType.NUMBER)
    elif operator.subtype == TokenSubtype.SUB:
        return Token(-right.data, TokenType.NUMBER)

    raise SyntaxError("Unknown operator %r" % operator.data)


def split_by_comma(objects):
    result = []
    buffer = []

    for obj in objects:
        if is_token(obj) and obj.type == TokenType.COMMA:
            result.append(AstTree(objects=copy(buffer)))
            buffer.clear()

            continue

        buffer.append(obj)

    if buffer:
        result.append(AstTree(objects=buffer))

    return result


def ast_eval(tree, int_class,
             functions, constants):
    tree = tree  # type: AstTree
    it = tree.create_iterator()

    while True:
        if len(tree.objects) == 1 and is_token(tree.objects[0]):
            break

        operation = get_max_priority(it)
        offset = operation.max_prior_pos

        if operation.seq_type == SequenceType.BINARY_OP:
            first = it.peek(offset)
            second = it.peek(offset+1)
            third = it.peek(offset+2)

            if not is_operator(second):
                raise SyntaxError("Unexpected object type %r in binary expression" % type(second))

            if first.type == TokenType.ID:
                first.type = TokenType.NUMBER
                first.data = constants[first.data]

            if third.type == TokenType.ID:
                third.type = TokenType.NUMBER
                third.data = constants[third.data]

            result_token = perform_binary_operation(first, third,
                                                    second, int_class)
            tree.replace(result_token, offset, 3)
        elif operation.seq_type == SequenceType.UNARY_OP:
            operation = it.peek(offset)
            operand = it.peek(offset+1)

            if operand.type == TokenType.ID:
                operand.type = TokenType.NUMBER
                operand.data = constants[operand.data]

            result_token = perform_unary_operation(operation, operand,
                                                   int_class)

            tree.replace(result_token, offset, 2)
        elif operation.seq_type == SequenceType.BRACKETS:
            result = ast_eval(it.peek(offset), int_class,
                              functions, constants)

            tree.replace(Token(result, TokenType.NUMBER),
                         offset, 1)
        elif operation.seq_type == SequenceType.CALL:
            function_name = it.peek(offset).data
            arguments = split_by_comma(it.peek(offset+1).objects)
            positional = []

            for arg in arguments:
                result = ast_eval(arg, int_class,
                                  functions, constants)
                positional.append(result)

            result = functions[function_name](*positional)

            tree.replace(Token(result, TokenType.NUMBER),
                         offset, 2)

    last = tree.objects[0]
    last.parse(int_class)

    return last.data


def evaluate(text, constants=None,
             functions=None, int_class=float):
    if constants is None:
        constants = {}

    if functions is None:
        functions = {}

    tree = parse(tokenize(text))

    return ast_eval(tree, int_class,
                    functions, constants)
