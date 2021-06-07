from enum import IntEnum


class TokenType(IntEnum):
    NUMBER = 1
    OPERATOR = 2

    OPEN_BRACKET = 3
    CLOSE_BRACKET = 4

    ID = 5
    COMMA = 6


class TokenSubtype(IntEnum):
    ADD = 1
    SUB = 2

    MUL = 3
    DIV = 4

    POW = 5

    FLOAT = 6
    INT = 7

    NONE = 8


class Token:
    def __init__(self, data, type_,
                 subtype=TokenSubtype.NONE,
                 char=0):
        self.data = data
        self.type = type_
        self.subtype = subtype

        self.char = char

    def parse(self, parser):
        if isinstance(self.data, str):
            self.data = parser(self.data)

    def __repr__(self):
        return 'Token(data=%r type=%r subtype=%r)' % (self.data, self.type, self.subtype)

    __str__ = __repr__


class Iterator:
    def __init__(self, container,
                 default_value=None, start_from=0):
        self.container = container
        self.shift = start_from

        self.default_value = default_value

    def next(self, step=1):
        self.shift += step

    def is_done(self, step=0):
        return (self.shift + step) >= len(self.container)

    def get_position(self, step=0):
        return self.shift + step

    def peek(self, step=0):
        if self.is_done(step):
            return self.default_value

        return self.container[step + self.shift]


class AstTree:
    def __init__(self, indent=0,
                 objects=None):
        self.objects = objects or []
        self.indent = indent

    def add_token(self, token):
        """
        Add token to the objects list

        :param token:
        :type token: Token

        :return: None
        """

        self.objects.append(token)

    def replace(self, obj,
                pos, count):
        if count == 1:
            self.objects[pos] = obj

            return

        del self.objects[pos:pos+count-1]
        self.objects[pos] = obj

    def add_tree(self, tree):
        """
        Add tree object to the objects list

        :return: None
        """

        self.objects.append(tree)

    def create_iterator(self):
        """
        :return: Iterator
        """

        return Iterator(self.objects)
