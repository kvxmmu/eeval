from re import compile


NORMAL_PRIORITY = 0
MEDIUM_PRIORITY = 1
HIGH_PRIORITY = 2
MAX_PRIORITY = 3

NUMBER = "NUMBER"
OPERATOR = "OPERATOR"
OPEN_BLOCK = "OPEN_BLOCK"
CLOSE_BLOCK = "CLOSE_BLOCK"
CONSTANT = "CONSTANT"

UNARY = "UNARY"
PLUS = "PLUS"
SUB = "SUB"
POW = "POW"
MUL = "MUL"
DIV = "DIV"
UNARY_PLUS = UNARY + PLUS
UNARY_SUB = UNARY + SUB

NO_TYPE = "NO_TYPE"


DEFAULT_TOKENS = (
	(compile(r'\d+\.\d+'), NUMBER),
	(compile(r'\d+'), NUMBER),
	
	(compile(r'\+'), OPERATOR, PLUS),
	(compile(r'\-'), OPERATOR, SUB),
	
	(compile(r'\*'), OPERATOR, MUL),
	(compile(r'\/'), OPERATOR, DIV),
	
	(compile(r'\^'), OPERATOR, POW),
	
	(compile(r'\('), OPEN_BLOCK),
	(compile(r'\)'), CLOSE_BLOCK),
	
	(compile(r'[\w\_]+[\_\d]*'), CONSTANT),
	
	(compile(r'\s'), None)  # Skip token, do nothing
)

PRIORITY_TABLE = {
	POW: HIGH_PRIORITY,
	
	MUL: MEDIUM_PRIORITY,
	DIV: MEDIUM_PRIORITY,
}

OPERATORS_TABLE = {
	PLUS: lambda x, y: x + y,
	SUB: lambda x, y: x - y,
	
	POW: lambda x, y: x**y,
	
	MUL: lambda x, y: x * y,
	DIV: lambda x, y: x / y,
	
	UNARY_PLUS: lambda x: +x,
	UNARY_SUB: lambda x: -x
}
