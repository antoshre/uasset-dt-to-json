import os
import struct
import binascii
import json
from collections import OrderedDict
from functools import total_ordering
from io import *

#
class BaseElem():
	def __init__(self, stream):
		self.offset = stream.tell()
@total_ordering
class IntX(BaseElem):
	def __init__(self, size, stream):
		super().__init__(stream)
		self.raw = stream.read(size)
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.value() == other.value()
		if isinstance(other, int):
			return self.value() == other
		raise NotImplementedError(type(other))
	def __lt__(self, other):
		if isinstance(other, self.__class__):
			return self.value() < other.value()
		if isinstance(other, int):
			return self.value() < other
		raise NotImplementedError(type(other))
	@classmethod
	def from_constant(cls, value):
		stream = BytesIO(b'')
		obj = cls(0, stream)
		obj.offset = -1
		obj.raw = b''
		obj.value = lambda : value
		return obj
class Int8(IntX):
	def __init__(self, stream):
		super().__init__(1, stream)
	def value(self):
		return struct.unpack("b", self.raw)[0]
class Int16(IntX):
	def __init__(self, stream):
		super().__init__(2, stream)
	def value(self):
		return struct.unpack("h", self.raw)[0]
class Int32(IntX):
	def __init__(self, stream):
		super().__init__(4, stream)
	def value(self):
		return struct.unpack("i", self.raw)[0]
class Int64(IntX):
	def __init__(self, stream):
		super().__init__(8, stream)
	def value(self):
		return struct.unpack("q", self.raw)[0]
class Int32_BS(Int32):
	def value(self):
		return super().value()//256
@total_ordering
class UIntX(BaseElem):
	def __init__(self, size, stream):
		super().__init__(stream)
		self.raw = stream.read(size)
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.value() == other.value()
		if isinstance(other, int):
			return self.value() == other
		raise NotImplementedError(type(other))
	def __lt__(self, other):
		if isinstance(other, self.__class__):
			return self.value() < other.value()
		if isinstance(other, int):
			return self.value() < other
		raise NotImplementedError(type(other))
	@classmethod
	def from_constant(cls, value):
		stream = BytesIO(b'')
		obj = cls(0, stream)
		obj.offset = -1
		obj.raw = b''
		obj.value = lambda : value
		return obj	
class UInt8(IntX):
	def __init__(self, stream):
		super().__init__(1, stream)
	def value(self):
		return struct.unpack("B", self.raw)[0]
class UInt16(IntX):
	def __init__(self, stream):
		super().__init__(2, stream)
	def value(self):
		return struct.unpack("H", self.raw)[0]
class UInt32(IntX):
	def __init__(self, stream):
		super().__init__(4, stream)
	def value(self):
		return struct.unpack("I", self.raw)[0]
class UInt64(IntX):
	def __init__(self, stream):
		super().__init__(8, stream)
	def value(self):
		return struct.unpack("Q", self.raw)[0]
class UInt32_BS(UInt32):
	def value(self):
		return super().value() // 256
	
@total_ordering
class FloatX(BaseElem):
	def __init__(self, size, stream):
		super().__init__(stream)
		self.raw = stream.read(size)
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.value() == other.value()
		if isinstance(other, int):
			return self.value() == other
		raise NotImplementedError(type(other))
	def __lt__(self, other):
		if isinstance(other, self.__class__):
			return self.value() < other.value()
		if isinstance(other, int):
			return self.value() < other
		if isinstance(other, float):
			return self.value() < other
		raise NotImplementedError(type(other))
	@classmethod
	def from_constant(cls, value):
		stream = BytesIO(b'')
		obj = cls(0, stream)
		obj.offset = -1
		obj.raw = b''
		obj.value = lambda : value
		return obj
class Float4(FloatX):
	def __init__(self, stream):
		super().__init__(4, stream)
	def value(self):
		return struct.unpack("f", self.raw)[0]
	
class PrefixArray(BaseElem):
	def __init__(self, Type, stream):
		super().__init__(stream)
		self.Count = Int32(stream)
		#print("Creating PrefixArray of type {} size {}".format(Type, self.Count.value()))
		self.Elems = [Type(stream) for _ in range(self.Count.value())]
	def __getitem__(self, key):
		return self.Elems[key]
class FixedArray(BaseElem):
	def __init__(self, Type, Count, stream):
		super().__init__(stream)
		self.Count = Count
		#print("Creating FixedArray of type {} size {}".format(Type, self.Count.value()))
		self.Elems = [Type(stream) for _ in range(self.Count.value())]
	def __getitem__(self, key):
		if (key >= 0 and key <= len(self.Elems)):
			return self.Elems[key]
		else:
			#print("Bad key access: {}".format(key))
			msg = "BADKEY:{}".format(key)
			bytestream = struct.pack("i", len(msg)) + msg.encode("utf-8") + struct.pack("hh", 0,0)
			fake = FNameEntry( BytesIO(bytestream))
			fake.offset = -1
			return fake
		
class UE4Bool(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.raw = stream.read(4)
	def value(self):
		return self.raw != b'\x00\x00\x00\x00'
class UE4Guid(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.raw = stream.read(16)
	def value(self):
		return self.raw
class UE4String(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Length = Int32(stream)
		if (self.Length >= 0):
			self.String = stream.read(self.Length.value()).decode("utf-8")
		else:
			self.String = stream.read(self.Length.value() * -2).decode("utf-16")
		self.Value = self.String
			
class EObjectFlags(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Flags = UInt32(stream)
class EDynamicType(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Flags = UInt32(stream)
		
class FCustomVersion(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Key = UE4Guid(stream)
class FGenerationInfo(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.ExportCount = Int32(stream)
		self.NameCount = Int32(stream)
class FEngineVersion(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Major = UInt32(stream)
		self.Minor = UInt32(stream)
		self.Patch = UInt32(stream)
		self.Changeset = UInt32(stream)
class FNameEntry(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Name = UE4String(stream)
		self.NonCasePreservingHash = UInt16(stream)
		self.CasePreservingHash = UInt16(stream)
class FName(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Index = Int64(stream)
	def value(self):
		return SummaryNames[self.Index.value()]
class FPackageIndex(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Index = Int32(stream)
	def value(self):
		importIndex = 0 - self.Index.value() - 1
		exportIndex = self.Index.value() - 1
		isImport = self.Index.value() < 0
		isExport = self.Index.value() > 0
		if isImport and SummaryImports.Count > importIndex:
			return SummaryImports[importIndex]
		if isExport and SummaryExports.Count > exportIndex:
			return SummaryExports[exportIndex]
		return None
		#raise LookupError("Index: {}".format(self.Index.value()))
class FObjectImport(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.ClassPackage = FName(stream)
		self.ClassName = FName(stream)
		self.PackageRef = FPackageIndex(stream)
		self.ObjectName = FName(stream)
class FObjectExport(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.ClassIndex = FPackageIndex(stream)
		self.SuperIndex = FPackageIndex(stream)
		self.TemplateIndex = FPackageIndex(stream)
		self.OuterIndex = FPackageIndex(stream)
		self.ObjectName = FName(stream)
		self.ObjectFlags = EObjectFlags(stream)
		self.SerialSize = Int64(stream)
		self.SerialOffset = Int64(stream)
		self.ForcedExport = UE4Bool(stream)
		self.NotForClient = UE4Bool(stream)
		self.NotForServer = UE4Bool(stream)
		self.PackageGuid = UE4Guid(stream)
		self.PackageFlags = UInt32(stream)
		self.NotAlwaysLoadedForEditorGame = UE4Bool(stream)
		self.IsAsset = UE4Bool(stream)
		self.FirstExportDependency = Int32(stream)
		self.SerializationBeforeSerializationDependencies = UE4Bool(stream)
		self.CreateBeforeSerializationDependencies = UE4Bool(stream)
		self.SerializationBeforeCreateDependnecies = UE4Bool(stream)
		self.CreateBeforeCreateDependencies = UE4Bool(stream)
		self.DynamicType = EDynamicType(stream)
		
class FPackageFileSummary(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Tag = Int32(stream)
		self.FileVersionUE4 = Int32(stream)
		self.FileVersionLicenseeUE4 = Int32(stream)
		self.FileVersionUE3 = Int32(stream)
		self.FileVersionLicenseeUE3 = Int32(stream)
		self.CustomVersion = PrefixArray(FCustomVersion, stream)
		self.TotalHeaderSize = Int32(stream)
		self.FolderName = UE4String(stream)
		self.PackageFlags = UInt32(stream)
		self.NameCount = Int32(stream)
		self.NameOffset = Int32(stream)
		self.GatherableNameCount = Int32(stream)
		self.GatherableNameOffset = Int32(stream)
		self.ExportCount = Int32(stream)
		self.ExportOffset = Int32(stream)
		self.ImportCount = Int32(stream)
		self.ImportOffset = Int32(stream)
		self.DependsOffset = Int32(stream)
		self.SoftPackageReferenceCount = Int32(stream)
		self.SoftPackageReferenceOffset = Int32(stream)
		self.SearchableNameOffset = Int32(stream)
		self.ThumbnailTableOffset = Int32(stream)
		self.Guid = UE4Guid(stream)
		self.Generations = PrefixArray(FGenerationInfo, stream)
		self.SavedByEngineVersion = FEngineVersion(stream)
		self.CompatibleWithEngineVersion = FEngineVersion(stream)
		self.CompressionFlags = UInt32(stream)
		self.PackageSource = UInt32(stream)
		self.UnVersioned = UE4Bool(stream)
		self.AssetRegistryDataOffset = Int32(stream)
		self.BulkDataStartOffset = Int64(stream)
		self.WorldTileInfoDataOffset = Int32(stream)
		self.ChunkIDs = PrefixArray(Int32, stream)
		self.PreloadDependencyCount = Int32(stream)
		self.PreloadDependencyOffset = Int32(stream)
		
		#Time to start bouncing around decoding fields
		#save current position
		before_names = stream.tell()
		#move to NameOffset
		stream.seek(self.NameOffset.value(), SEEK_SET)
		#decode Names
		self.Names = FixedArray(FNameEntry, self.NameCount, stream)
		#return to saved position
		stream.seek(before_names, SEEK_SET)
		
		global SummaryNames
		SummaryNames = self.Names
		
		before_imports = stream.tell()
		#print("Parsing Imports...")
		stream.seek(self.ImportOffset.value())
		self.Imports = FixedArray(FObjectImport, self.ImportCount, stream)
		stream.seek(before_imports)
		global SummaryImports
		SummaryImports = self.Imports
		
		before_exports = stream.tell()
		stream.seek(self.ExportOffset.value())
		self.Exports = FixedArray(FObjectExport, self.ExportCount, stream)
		stream.seek(before_exports)
		global SummaryExports
		SummaryExports = self.Exports
		
class FPropertyTag(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Name = FName(stream)
		self.Type = FName(stream)
		self.Size = Int32(stream)
		self.Index = Int32(stream)
		
class FPropertyGuid(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.HasGuid = UInt8(stream)
		if (self.HasGuid.value() == 0):
			self.Guid = None
		else:
			self.Guid = UE4Guid(stream)
	def value(self):
		return self.Guid
	
class UObjectProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Id = FPropertyGuid(stream)
		self.Package = FPackageIndex(stream)
		self.Value = self.Package
class UArrayProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Type = FName(stream)
		self.Guid = FPropertyGuid(stream)
		self.Size = Int32(stream)
		
		typename = SummaryNames[self.Type.Index.value()]
		cph = typename.CasePreservingHash.value()
		
		lookup = {
			0x4A08 : USpecialName
		}
		if (cph in lookup):
			func = lookup[cph]
			self.Elems = FixedArray(func, self.Size, stream)
			#self.elems = [func(stream) for _ in range(self.Size.value())]
		else:
			raise NotImplementedError(typename, cph)
			
		self.Value = self.Elems
#wtf is this for
class USpecialName(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Index = Int32(stream)
		self._unknown = UInt32(stream)
		self.Value = SummaryNames[self.Index.value()]
		#print("USpecialName @ {}, Index: {}".format(self.offset, self.Index.value()))
class UStrProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		self.String = UE4String(stream)
		self.Value = self.String

class UNameProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		#Why is this name offset only 32 bits?!
		self.Value = FName_special(stream)
		self._unknown = UInt32(stream)
		#self.Value = FName(stream)
class UByteProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.EnumName = FName(stream)
		self.Guid = FPropertyGuid(stream)
		self.Value = FName(stream)
class UIntProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		self.Value = Int32(stream)
class UUInt32Property(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		self.Value = UInt32(stream)
		
		#print("UUint32Property @ {}:\n\tGuid: {}\n\tValue: {}\n".format(self.offset, self.Guid.value(), self.Value.value()))
class UFloatProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		self.Value = Float4(stream)
class UBoolProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Value = UInt8(stream)
		self.Guid = FPropertyGuid(stream)

class USoftObjectProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		self.Package = FName(stream)
		self.Path = UE4String(stream)
		#self.Length = UInt32(stream)
		#self.Path = FixedArray(Int8, self.Length, stream)
		self.Value = self.Path
		
class UEnumProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.EnumName = FName(stream)
		self.Guid = FPropertyGuid(stream)
		self.Value = FName(stream)
		
class UTextProperty(FPropertyTag):
	def __init__(self, stream):
		super().__init__(stream)
		if (debug):
			print(self.__class__.__name__  + " @ {}".format(stream.tell()))
		self.Guid = FPropertyGuid(stream)
		self._unknown = UInt64(stream) #TODO: what is this?
		self.Key = FPropertyGuid(stream)
		self.Hash = UE4String(stream)
		self.Value = UE4String(stream)
		
class UAsset(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Summary = FPackageFileSummary(stream)
			
#		for i,v in enumerate(self.Summary.Names):
#			print("{}, {}".format(i, v.Name.String))
		for export in self.Summary.Exports:
			save = stream.tell()
			stream.seek(export.SerialOffset.value())
			export.Object = UObject(stream, doPad=True, extra=export)
			stream.seek(save)

class UObject(BaseElem):
	def __init__(self, stream, doPad=False, extra=None):
		super().__init__(stream)
		self.Tags = []
		while(True):
			#Check if a 'None' FName is next in the stream, break if true
			saved = stream.tell()
			temp = FName(stream)
			if (temp.value().CasePreservingHash.value() == 0xDC5):
				break
			stream.seek(saved)
			
			#decode a full FPropertyTag to get next Type name
			tag = FPropertyTag(stream)
			
			if(debug):
				print("UObject tag decoded:\n",
						tag.Name.value().Name.String,
						tag.Type.value().Name.String,
						tag.Size.value(),
						tag.Index.value()
					)
			
			stream.seek(saved)
			
			taghash = tag.Type.value().CasePreservingHash.value()
			
			lookup = {
				0xEAB3 : UObjectProperty,
				0x2472 : UStrProperty,
				0xC02D : UByteProperty,
				0x4A36 : UIntProperty,
				0x4A08 : UNameProperty,
				0x69E3 : UArrayProperty,
				0x8AB0 : UBoolProperty,
				0x4A38 : UUInt32Property,
				0xFDDE : UFloatProperty,
				0xB774 : UTextProperty,
				0xFAAE : USoftObjectProperty,
				0x409D : UEnumProperty,
			}
			
			if (taghash in lookup):
				self.Tags.append(lookup[taghash](stream))
			else:
				raise NotImplementedError("Unknown tag type: {}, hash: 0x{:X}" \
										  .format(tag.Type.value().Name.String, \
										  tag.Type.value().CasePreservingHash.value()))
		
		if (doPad):
			self._pad = UInt32(stream)
		
		if (extra is not None):
			objref = extra.ClassIndex.value()
			taghash = objref.ObjectName.value().CasePreservingHash.value()
			
			lookup = {
				0x10EE : UDataTable
			}
			
			if (taghash in lookup):
				self.ObjectData = lookup[taghash](stream)
				
#Special FName just for UDataTable entries
class FName_special(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Index = Int32(stream)
	def value(self):
		return SummaryNames[self.Index.value()]

class UDataTable_Entry(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		#wtf this FName index is only 32 bits, not 64
		#but the field is 64-bits wide..
		self.Index = FName_special(stream)
		#TODO: what the hell are these 32 bits used for?
		self._unknown = UInt32(stream)
		self.Obj = UObject(stream, doPad=False, extra=None)
class UDataTable(BaseElem):
	def __init__(self, stream):
		super().__init__(stream)
		self.Count = Int32(stream)
		self.Data = [UDataTable_Entry(stream) for _ in range(self.Count.value())]
		

class UAssetEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			return "0x" + str(binascii.hexlify(obj))[2:-1]
		if isinstance(obj, UE4Guid):
			return obj.raw
		if isinstance(obj, FNameEntry):
			return obj.Name
		d = obj.__dict__		
		do = OrderedDict()
		for k,v in sorted(d.items()):
			do[k] = v
		
		if hasattr(obj, 'value'):
			if callable(obj.value):
				do['Value'] = obj.value()
				if not hasattr(obj, 'Type'):
					do['Type'] = obj.__class__.__name__
		
		return do

#helper class to organize export tags into something manageable
#This is what will actually be JSON'ized
#tags is a UDataTable_Entry object
class Item():
	def __init__(self, tags):
		self.Key = tags.Index
		d = {}
		for prop in tags.Obj.Tags:
			k = prop.Name.value().Name.String
			v = (prop.Type.value().Name.String, prop.Value)
			d[k] = v
		self.Properties = OrderedDict()
		for k,v in sorted(d.items(), key= lambda obj: obj[1][1].offset):
			self.Properties[k] = v

class ItemInfoOnly():
	def __init__(self, tags):
		self.Key = tags.Index
		d = {}
		for prop in tags.Obj.Tags:
			k = prop.Name.value().Name.String
			obj = prop.Value
			if hasattr(obj, 'Value'):
				if callable(obj.Value):
					v = prop.Value.Value()
				else:
					v = prop.Value.Value
			if hasattr(obj, 'value'):
				if callable(obj.value):
					v = prop.Value.value()
				else:
					v = prop.Value.value
			v = (prop.Type.value().Name.String, v)
			d[k] = v
		self.Properties = d
		
if __name__ == "__main__":
	import argparse
	import sys
	parser = argparse.ArgumentParser( \
			description='Dump UAsset DataTable to JSON',
			usage='%(prog)s [filename]'
			)
	parser.add_argument('filename', help='UAsset filename', type=argparse.FileType('rb'))
	parser.add_argument('--no-names', help='Do not dump name table', action='store_true') #don't output Names
	parser.add_argument('--no-data', help='Do not dump exported data', action='store_true') #don't output exported data
	parser.add_argument('--values-only', help='Only print values, not offset/length information', action='store_true')
	parser.add_argument('--debug', help='Verbose (and buggy) printing of FPropertyTag parsing. This *will* break JSON formatting!', action='store_true')
	args = parser.parse_args()
	
	#set debug flag from argument
	debug = args.debug
	
	#Parse uasset file
	uasset = UAsset(args.filename)
	
	if (args.values_only):
		iclass = ItemInfoOnly
	else:
		iclass =  Item
	
	#Output Names
	if not args.no_names:
		print( json.dumps( uasset.Summary.Names, cls=UAssetEncoder, indent=2) )
	#Output exported data
	if not args.no_data:
		#Assuming only one export!
		assert(uasset.Summary.ExportCount.value() == 1)
		#TODO: handle multiple exports
		#Grab the export'ed stuff we actually care about
		items = [ iclass(obj) for obj in uasset.Summary.Exports[0].Object.ObjectData.Data]
		#JSONify it
		print(json.dumps(items, cls=UAssetEncoder, indent=2))
	sys.exit()