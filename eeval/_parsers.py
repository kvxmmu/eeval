from .types import (Iterator, Token,
                    TokenSubtype, TokenType)
from .exceptions import ParseSyntaxError

from string import ascii_letters, digits


ID_DICTIONARY = set(ascii_letters + digits)


def _parse_skippable(it, tokens):
    """
    :param it:
    :type it: Iterator

    :param tokens:
    :type tokens: list

    :return: bool
    """

    char = it.peek()
    result = char in ('\n', ' ', '\t')

    if result:
        it.next()

    return result


def _parse_comma(it, tokens):
    """
    :param it:
    :type it: Iterator

    :param tokens:
    :type tokens: list

    :return: bool
    """

    char = it.peek()

    if char == ',':
        tokens.append(Token(',', TokenType.COMMA))
        it.next()

        return True

    return False


def _parse_number(it, tokens):
    """
    :param it:
    :type it: Iterator

    :param tokens:
    :type tokens: list

    :return: bool
    """

    offset = 0
    number_type = TokenSubtype.INT
    number = ""

    while not it.is_done(offset):
        char = it.peek(offset)

        if char == '.':
            if number_type == TokenSubtype.FLOAT:
                raise ParseSyntaxError(char, it.get_position(offset))

            number_type = TokenSubtype.FLOAT
        elif not char.isdigit():
            break

        offset += 1
        number += char

    if not number:
        return False

    it.next(offset)
    tokens.append(Token(number, TokenType.NUMBER,
                        number_type))

    return True


def _parse_operator(it, tokens):
    """
    :param it:
    :type it: Iterator

    :param tokens:
    :type tokens: list

    :return: bool
    """

    first = it.peek()
    subtype = TokenSubtype.NONE

    if first == '^':
        subtype = TokenSubtype.POW
    elif first == '*':
        subtype = TokenSubtype.MUL
    elif first == '/':
        subtype = TokenSubtype.DIV
    elif first == '+':
        subtype = TokenSubtype.ADD
    elif first == '-':
        subtype = TokenSubtype.SUB

    if subtype == TokenSubtype.NONE:
        return False

    it.next()
    tokens.append(Token(first, TokenType.OPERATOR,
                        subtype))

    return True


def _parse_brackets(it, tokens):
    """
    :param it:
    :type it: Iterator

    :param tokens:
    :type tokens: list

    :return: bool
    """

    first = it.peek()
    type_ = None

    if first == '(':
        type_ = TokenType.OPEN_BRACKET
    elif first == ')':
        type_ = TokenType.CLOSE_BRACKET

    if type_ is None:
        return False

    it.next()
    tokens.append(Token(first, type_))

    return True


def _parse_id(it, tokens):
    """
    :param it:
    :type it: Iterator

    :param tokens:
    :type tokens: list

    :return: bool
    """

    offset = 0
    id_ = ""

    while not it.is_done(offset):
        char = it.peek(offset)

        if char not in ID_DICTIONARY:
            break

        offset += 1
        id_ += char

    if not id_:
        return False

    it.next(offset)
    tokens.append(Token(id_, TokenType.ID))

    return True
