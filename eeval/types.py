from .constants import (NORMAL_PRIORITY, MAX_PRIORITY,
											NO_TYPE)

from pprint import pformat


class Token:
	def __init__(self, data, tag,
						subtag=NO_TYPE, priority=NORMAL_PRIORITY):
		self.data = data
		self.tag = tag
		self.subtag = subtag
		
		self.priority = priority
	
	def __str__(self):
		return "Token(data=%r, tag=%s, subtag=%s, priority=%d)" % (
			self.data, self.tag,
			self.subtag, self.priority
		)
	
	__repr__ = __str__
		

class AstTree:
	def __init__(self):
		self.tree = []
		self.priority = MAX_PRIORITY
	
	def add_token(self, token):
		self.tree.append(token)
	
	def add_tree(self):
		tree = AstTree()
		self.tree.append(tree)
		
		return tree
	
	def replace(self, token, pos, count=1):
		del self.tree[pos:pos+count]
		
		self.tree.insert(pos, token)
	
	def __repr__(self):
		return pformat(self.tree)
	
	__str__ = __repr__

class Peekable:
	def __init__(self, iterable):
		self.iterable = iterable
		self.pos = 0
	
	@property
	def length(self):
		return len(self.iterable)
	
	def is_done(self, step=0):
		return (self.pos + step) >= self.length
	
	def get_position(self, step):
		return self.pos + step
	
	def peek(self, step):
		if self.is_done(step):
			return
		
		return self.iterable[self.get_position(step)]

	def next(self, step=1):
		self.pos += step

