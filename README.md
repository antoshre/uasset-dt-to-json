# uasset-dt-to-json
Parses UAsset files with embedded DataTables and dumps the contents to JSON.  Tracks byte offsets to allow easier hex editing.

DataTables are how the Unreal 3 engine handles database-like data for objects inside the engine.  The source is technically visible but I wanted something that wasn't bound by license issues and decided to try reverse-engineering it from first principles.  Consequently this will probably only work on Bloodstained: Ritual Of The Night datafiles as I have no other examples to work from.

This script is most definitely a work-in-progress.  Not all property types are supported, and not all those that are supported are 100% correct in all cases.  Pull requests welcome.

## Usage

JSON output is printed to standard out.  It can and will quickly overflow the terminal scrollback buffer, re-directing to a file is basically mandatory.

```
usage: datatable-to-json.py [file]

Dump UAsset DataTable to JSON

positional arguments:
  file           Input UAsset file

optional arguments:
  -h, --help     show this help message and exit
  --no-names     Do not dump name table
  --no-data      Do not dump exported data
  --values-only  Only print values, not offset/length information
```

## Example output:

```
{
    "Key": {
      "Index": {
        "offset": 43329,
        "raw": "0x32030000",
        "Value": 818,
        "Type": "Int32"
      },
      "offset": 43329,
      "Value": {
        "Length": {
          "offset": 21465,
          "raw": "0x14000000",
          "Value": 20,
          "Type": "Int32"
        },
        "String": "P0000_NSWORD_LIDDYL\u0000",
        "offset": 21465
      },
      "Type": "FName_special"
    },
    "Properties": {
      "DamageId\u0000": [
        "IntProperty\u0000",
        {
          "offset": 43362,
          "raw": "0x18000000",
          "Value": 24,
          "Type": "Int32"
        }
      ],
      "ArtsID\u0000": [
        "ByteProperty\u0000",
        {
          "Index": {
            "offset": 43399,
            "raw": "0x6d00000000000000",
            "Value": 109,
            "Type": "Int64"
          },
          "offset": 43399,
          "Value": {
            "Length": {
              "offset": 2669,
              "raw": "0x12000000",
              "Value": 18,
              "Type": "Int32"
            },
            "String": "EWpnSPEntry::None\u0000",
            "offset": 2669
          },
          "Type": "FName"
        }
      ],
      "DamageType\u0000": [
        "IntProperty\u0000",
        {
          "offset": 43432,
          "raw": "0x01000000",
          "Value": 1,
          "Type": "Int32"
        }
      ],
      "ShardId\u0000": [
        "NameProperty\u0000",
        {
          "Index": {
            "offset": 43461,
            "raw": "0xc8020000",
            "Value": 712,
            "Type": "Int32"
          },
          "offset": 43461,
          "Value": {
            "Length": {
              "offset": 18467,
              "raw": "0x05000000",
              "Value": 5,
              "Type": "Int32"
            },
            "String": "None\u0000",
            "offset": 18467
          },
          "Type": "FName_special"
        }
      ],
	}
}
```
