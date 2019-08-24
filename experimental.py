#UAsset parser based on FPropertyTag lengths
import os
import json
import binascii
from header import dumper

class To_Dump_Encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			return str(binascii.hexlify(obj))
		return obj.to_dump()

if __name__ == "__main__":

	with open("PB_DT_DropRateMaster-v1.03.uasset", 'rb') as file:
		#print(file.name)
		ctx = dumper.ParserCtx(file, debug=False)
		uasset = dumper.UAsset(ctx)
		print("Parsing complete, creating json for each export")
		for i,export in enumerate(uasset.Summary.Exports):
			if (ctx.debug):
				print("{}...".format(i))
			j = json.dumps(export.Object, cls=To_Dump_Encoder, indent=2, sort_keys=True)
			with open(file.name[:-7] + "-export-" + str(i) + ".json", "w") as outputfile:
				outputfile.write(j)
		print("JSON dump complete, writing out")		