#UAsset parser based on FPropertyTag lengths
import os
import json
import binascii
import dumper




if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser( \
		description="UAsset to JSON dumper",
		usage="%(prog)s [filename]"
	)
	parser.add_argument('filename', help='UAsset filename')
	parser.add_argument('--debug', help='Verbose (and buggy) printing of parsing progress', action='store_true')
	
	args = parser.parse_args()
	
	names, exports, imports = dumper.dumpFile(args.filename, args.debug)
	
	with open(args.filename[:-7]+"-names.json", 'w') as file:
		file.write(names)
	
	for i,exp in enumerate(exports):
		with open(args.filename[:-7]+"-export-{}.json".format(i), 'w') as file:
			file.write(exp)
	for i,imp in enumerate(imports):
		with open(args.filename[:-7]+"-import-{}.json".format(i), 'w') as file:
			file.write(imp)	