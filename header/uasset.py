#Uasset

from primitives import *
from ue4basic import *
from ue4arrays import *

class UAsset(Primitive):
	def __init__(self, stream):
		super().__init__(stream)
		self.Summary = FPackageFileSummary(ctx)