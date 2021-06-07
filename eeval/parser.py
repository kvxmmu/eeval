from .types import (AstTree, Token,
                    Iterator, TokenType,
                    TokenSubtype)
from .exceptions import ParseSyntaxError
from ._parsers import (_parse_number, _parse_operator,
                       _parse_id, _parse_brackets,
                       _parse_skippable, _parse_comma)
from re import compile


USED_TOKENIZERS = (
    _parse_skippable,
    _parse_number,
    _parse_operator,
    _parse_id,
    _parse_brackets,
    _parse_comma
)


DEFAULT_TOKENS = (
    (compile(r'\d+\.\d+'), TokenType.NUMBER),
    (compile(r'\d+'), TokenType.NUMBER),

    (compile(r'\+'), TokenType.OPERATOR, TokenSubtype.ADD),
    (compile(r'\-'), TokenType.OPERATOR, TokenSubtype.SUB),

    (compile(r'\*'), TokenType.OPERATOR, TokenSubtype.MUL),
    (compile(r'\/'), TokenType.OPERATOR, TokenSubtype.DIV),

    (compile(r'\^'), TokenType.OPERATOR, TokenSubtype.POW),

    (compile(r'\('), TokenType.OPEN_BRACKET),
    (compile(r'\)'), TokenType.CLOSE_BRACKET),

    (compile(r'[\w\_]+[\_\d]*'), TokenType.ID),

    (compile(r'\s'), None)  # Skip token, do nothing
)


def parse(tokens, parse_until=None,
          start_from=0):
    """
    :param tokens: Tokens to parse
    :type tokens: list[Token]

    :param parse_until:
    :param start_from:

    :return: AstTree
    """

    tree = AstTree()
    it = Iterator(tokens, start_from=start_from)

    while not it.is_done():
        token = it.peek()

        if token.type == parse_until:
            it.next()

            break
        elif token.type == TokenType.OPEN_BRACKET:
            it.next()

            ptree, shift = parse(tokens, parse_until=TokenType.CLOSE_BRACKET,
                                 start_from=it.get_position())
            tree.add_tree(ptree)
            it.shift = shift

            continue

        tree.add_token(token)
        it.next()

    if start_from != 0:
        return tree, it.shift

    return tree


def tokenize(text, tokens=None):
    """
    :param text: Text to tokenize
    :param tokens: a list of tokens parsers

    :return: list[Token]
    """

    if tokens is None:
        tokens = DEFAULT_TOKENS

    found = []
    pos = 0
    result = None

    while pos < len(text):
        for token in tokens:
            pattern, tag, *subtag = token

            if subtag:
                subtag = subtag[0]
            else:
                subtag = None

            result = pattern.match(text, pos)

            if result is not None:
                if tag is not None:
                    found.append(Token(result.group(0), tag,
                                       subtag))

                break

        if result is None:
            raise SyntaxError("Invalid expression on %d char" % pos)

        pos = result.end(0)

    return found


