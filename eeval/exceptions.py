class ParseSyntaxError(Exception):
    def __init__(self, char_pos,
                 character=None):
        if character is None:
            super().__init__("Unexpected sequence at char %d" % char_pos)
        else:
            super().__init__("Unexpected sequence %r at char %d" % (character, char_pos))
