#UE4 Array types

from primitives import *

class PrefixArray(Primitive):
	def __init__(self, Type, ctx):
		super().__init__(ctx)
		self.Count = Int4(ctx)
		self.Elems = [Type(ctx) for _ in range(self.Count.value())]
	def __getitem__(self, key):
		if (key in range(self.Count.value()-1)):
			return self.Elems[key]
		else:
			raise AttributeError("Bad key access: {}".format(key))
		
class FixedArray(Primitive):
	def __init__(self, Type, Count, ctx):
		super().__init__(ctx)
		self.Count = Count
		self.Elems = [Type(ctx) for _ in range(self.Count.value())]
	def __getitem__(self, key):
		if (key in range(self.Count.value()-1)):
			return self.Elems[key]
		else:
			raise AttributeError("Bad key access: {}".format(key))