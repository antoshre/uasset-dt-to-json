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
	import argparse
	
	parser = argparse.ArgumentParser( \
		description="UAsset to JSON dumper",
		usage="%(prog)s [filename]"
	)
	parser.add_argument('filename', help='UAsset filename', type=argparse.FileType('rb'))
	parser.add_argument('--debug', help='Verbose (and buggy) printing of parsing progress', action='store_true')
	
	args = parser.parse_args()
	
	
	print("Parsing {}".format(args.filename.name))
	ctx = dumper.ParserCtx(args.filename, debug=args.debug)
	uasset = dumper.UAsset(ctx)
	print("Dumping Names...", end='')
	j = json.dumps(uasset.Summary.Names, cls=To_Dump_Encoder, indent=2, sort_keys=False)
	with open(args.filename.name[:-7] + "-names.json", 'w') as outputfile:
		outputfile.write(j)
	print(" done.")
		
	print("Dumping exports...", end='')
	for i,export in enumerate(uasset.Summary.Exports):
		j = json.dumps(export.Object, cls=To_Dump_Encoder, indent=2, sort_keys=True)
		with open(args.filename.name[:-7] + "-export-" + str(i) + ".json", "w") as outputfile:
			outputfile.write(j)
	print(" done.")
	
	print("Dumping imports...", end='')
	for i,imp in enumerate(uasset.Summary.Imports):
		j = json.dumps(export.Object, cls=To_Dump_Encoder, indent=2, sort_keys=True)
		with open(args.filename.name[:-7] + "-import-" + str(i) + ".json", "w") as outputfile:
			outputfile.write(j)
	print(" done.")