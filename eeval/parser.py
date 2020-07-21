from .constants import (PRIORITY_TABLE, DEFAULT_TOKENS,
                        NO_TYPE, OPEN_BLOCK,
                        CLOSE_BLOCK, NORMAL_PRIORITY)
from .types import (Token, Peekable,
                    AstTree)


def lex(text, tokens=None,
        priority_table=None):
    if tokens is None:
        tokens = DEFAULT_TOKENS

    if priority_table is None:
        priority_table = PRIORITY_TABLE

    found = []
    pos = 0
    result = None

    while pos < len(text):
        for token in tokens:
            pattern, tag, *subtag = token

            if subtag:
                subtag = subtag[0]
            else:
                subtag = NO_TYPE

            result = pattern.match(text, pos)

            if result is not None:
                if tag is not None:
                    found.append(Token(result.group(0), tag,
                                       subtag,
                                       priority_table.get(subtag, NORMAL_PRIORITY)))

                break

        if result is None:
            raise SyntaxError("Invalid expression on %d char" % pos)

        pos = result.end(0)

    return found


def parse(tokens, until_tag=None,
          tree=None, it=None):
    if tree is None:
        tree = AstTree()

    if it is None:
        it = Peekable(tokens)

    while not it.is_done():
        token = it.peek(0)

        if token.tag == until_tag:
            it.next()

            break

        if token.tag == OPEN_BLOCK:
            it.next()

            new_tree = tree.add_tree()
            parse(tokens, CLOSE_BLOCK,
                  new_tree, it)

            continue
        elif token.tag == CLOSE_BLOCK:
            raise SyntaxError("Invalid expression: Unknown CLOSE_BLOCK on"
                              "char %d" % it.pos)

        tree.add_token(token)

        it.next()

    return tree
