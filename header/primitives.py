#UE4 header-essential primitives

import struct

class BaseElem():
	def __init__(self, ctx):
		self.offset = ctx.tell()
		
class Primitive(BaseElem):
	def __init__(self, ctx):
		super().__init__(ctx)
	def value(self):
		return self.__class__.__name__ + ":None"

class IntX(Primitive):
	def __init__(self, ctx, size):
		super().__init__(ctx)
		self.raw = ctx.read(size)
	@classmethod
	def from_constant(cls, value):
		stream = BytesIO(b'')
		obj = cls(steam, 0)
		obj.offset = -1
		obj.raw = b''
		obj.value = lambda: value
		return obj

class Int2(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 2)
	def value(self):
		return struct.unpack("h", self.raw)[0]
class Int4(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 4)
	def value(self):
		return struct.unpack("i", self.raw)[0]
class Int8(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 8)
	def value(self):
		return struct.unpack("q", self.raw)[0]
		
class UInt1(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 1)
	def value(self):
		return struct.unpack("B", self.raw)[0]
class UInt2(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 2)
	def value(self):
		return struct.unpack("H", self.raw)[0]
class UInt4(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 4)
	def value(self):
		return struct.unpack("I", self.raw)[0]
class UInt8(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 8)
	def value(self):
		return struct.unpack("Q", self.raw)[0] 
class UInt16(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 16)
	def value(self):
		return struct.unpack("16B", self.raw)[0]
		
class Float4(IntX):
	def __init__(self, ctx):
		super().__init__(ctx, 4)
	def value(self):
		return struct.unpack("f", self.raw)[0]