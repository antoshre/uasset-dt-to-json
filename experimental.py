#UAsset parser based on FPropertyTag lengths
import os
import json
import binascii
import dumper



#Filename is an open file handle
#TODO: rename it
def dumpFile(filename, debug=False):
	print("Parsing {}".format(filename))
	with open(filename, 'rb') as file:
		ctx = dumper.ParserCtx(file, debug=debug)
		uasset = dumper.UAsset(ctx)
		print("Dumping Names...")
		j = json.dumps(uasset.Summary.Names, cls=dumper.To_Dump_Encoder, indent=2, sort_keys=False)
		with open(file.name[:-7] + "-names.json", 'w') as outputfile:
			outputfile.write(j)
		print("done")
		
		print("Dumping exports...")
		for i,export in enumerate(uasset.Summary.Exports):
			j = json.dumps(export.Object, cls=dumper.To_Dump_Encoder, indent=2, sort_keys=True)
			with open(file.name[:-7] + "-export-" + str(i) + ".json", "w") as outputfile:
				outputfile.write(j)
		print("done")
		
		print("Dumping imports...")
		for i,imp in enumerate(uasset.Summary.Imports):
			j = json.dumps(export.Object, cls=dumper.To_Dump_Encoder, indent=2, sort_keys=True)
			with open(file.name[:-7] + "-import-" + str(i) + ".json", "w") as outputfile:
				outputfile.write(j)
		print("done")
if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser( \
		description="UAsset to JSON dumper",
		usage="%(prog)s [filename]"
	)
	parser.add_argument('filename', help='UAsset filename')
	parser.add_argument('--debug', help='Verbose (and buggy) printing of parsing progress', action='store_true')
	
	args = parser.parse_args()
	
	dumpFile(args.filename, args.debug)