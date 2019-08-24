#ParserCtx class
from io import BytesIO


class ParserCtx(BytesIO):
	def __init__(self, stream):
		super().__init__(stream)