from .parser import lex, parse
from .types import (Peekable, AstTree,
									Token)
from .constants import (OPERATOR, NUMBER,
											OPERATORS_TABLE,
											UNARY, CONSTANT)

def mix_operands(op, right, int_class, constants):
	subtag = UNARY + op.subtag
	func = OPERATORS_TABLE.get(subtag)
	
	if func is None:
		raise SyntaxError("Unknown operator %r" % op)
	
	if right.tag == CONSTANT:
		right.tag = NUMBER
		right.data = constants[right.data]
	
	try:
		right = int_class(right.data)
	except (ValueError, AttributeError):
		raise SyntaxError("Invalid expression")
	
	result = func(right)
	
	return Token(int_class(result), NUMBER)


def get_highest_priority_expr(iterable):
	it = Peekable(iterable)
	
	max_priority = -1
	max_pos = -1
	
	while not it.is_done():
		left = it.peek(0)
		op = it.peek(1)
		right = it.peek(2)
		
		if isinstance(left, AstTree) or left.tag in (OPERATOR, CONSTANT):
			return it.get_position(0)
		
		if op is None:
			it.next()
			
			continue
		
		if isinstance(right, AstTree) or right.tag == CONSTANT:
			return it.get_position(2)
		
		if op.priority > max_priority:
			max_priority = op.priority
			max_pos = it.get_position(0)
		
		it.next(2)

	return max_pos

def ast_eval(tree, int_class, constants=None):
	if constants is None:
		constants = {}
	
	while True:
		pos = get_highest_priority_expr(tree.tree)
		
		if pos == -1:
			break
		
		left = tree.tree[pos]
		
		if isinstance(left, AstTree):
			value = ast_eval(left, int_class, constants)
			
			tree.replace(Token(value, NUMBER), pos)
			
			continue
		
		if left.tag == CONSTANT:
			left.tag = NUMBER
			left.data = constants[left.data]
		
		op = tree.tree[pos+1]
		
		if isinstance(op, AstTree):
			value = ast_eval(op, int_class, constants)
			
			tree.replace(Token(value, NUMBER), pos+1)
			
			continue
		
		if left.tag == OPERATOR:
			token = mix_operands(left, op, int_class, constants)
			tree.replace(token, pos, 2)
			
			continue
		
		try:
			right = tree.tree[pos+2]
		except IndexError:
			raise SyntaxError("Token expected at %d" % (pos+2))
		
		if right.tag == OPERATOR:
			shifted = tree.tree[pos+3]
			
			if shifted.tag == CONSTANT:
				shifted.tag = NUMBER
				shifted.data = constants[shifted.data]
			
			result = mix_operands(shifted, right, int_class, constants)
			
			tree.replace(result, pos+2, 2)
		
			continue
		elif right.tag == CONSTANT:
			right.tag = NUMBER
			right.data = constants[right.data]
		
		func = OPERATORS_TABLE.get(op.subtag)
		
		if func is None:
			raise SyntaxError("Invalid operator: %r" % op)
		
		left, right = int_class(left.data), int_class(right.data)
		value = int_class(func(left, right))
		
		tree.replace(Token(value, NUMBER), pos, 3)
		
	return int_class(tree.tree[0].data)

def evaluate(expression, lex_tokens=None,
					   lex_priority_table=None,
					   int_class=float, constants=None):
	tokens = lex(expression, lex_tokens,
						   lex_priority_table)
	tree = parse(tokens)
	
	return ast_eval(tree, int_class, constants)
