#UE4 basic entities

from primitives import *

class UE4Bool(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Raw = UInt4(ctx)
	def value(self):
		return self.Raw.value() != 0
		
class UE4Guid(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Raw = UInt16(ctx)
	def value(self):
		return self.Raw.value()
		
class UE4String(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Length = Int4(ctx)
		if (self.Length.value() >= 0):
			self.String = ctx.read( self.Length.value()).decode("utf-8")
		else:
			self.String = ctx.read( self.Length.value()*-2).decode("utf-16")
	def value(self):
		return self.String
		