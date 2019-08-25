#UE4 header-essential primitives

import struct
import binascii
import json


from io import BytesIO

class To_Dump_Encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			return str(binascii.hexlify(obj))
		return obj.to_dump()


class ParserCtx():
	def __init__(self, stream, debug=False):
		self.stream = stream
		self.debug = debug
	def seek(self, i):
		return self.stream.seek(i)
	def tell(self):
		return self.stream.tell()
	def read(self, i):
		return self.stream.read(i)
	def decodeHash(self, hash):
		lookup = {
			0x69E3 : UArrayProperty,
			0xFC9C : UStructProperty,
			0xEAB3 : UObjectProperty,
			0xFAAE : USoftObjectProperty,
			0xC02D : UByteProperty,
			0x2472 : UStrProperty,
			0x4A08 : UNameProperty,
			0x4A36 : UIntProperty,
			0x4A38 : UUInt32Property,
			0x8AB0 : UBoolProperty,
			0xFDDE : UFloatProperty,
			0x409D : UEnumProperty,
			0xB774 : UTextProperty,
			0x2AAB : UMulticastDelegateProperty,
		}
		
		if hash in lookup:
			return lookup[hash]
		else:
			raise NotImplementedError("Tag hash# 0x{:02X}".format(hash))

class BaseElem():
	def __init__(self, ctx):
		self.offset = ctx.tell()
		
class Primitive(BaseElem):
	def __init__(self, ctx):
		super().__init__(ctx)
	def __str__(self):
		return self.__class__.__name__ + "( {}, offset={} )".format(self.value(), self.offset)

class IntX(Primitive):
	def __init__(self, ctx, size):
		super().__init__(ctx)
		self.raw = ctx.read(size)
	@classmethod
	def from_constant(cls, value):
		stream = BytesIO(b'')
		obj = cls(stream, 0)
		obj.offset = -1
		obj.raw = b''
		obj.value = lambda: value
		return obj
	def to_dump(self):
		return {
			'Type' : self.__class__.__name__,
			'Value' : self.value(),
			'offset' : self.offset,
		}
		

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
		
		
class PrefixArray(Primitive):
	def __init__(self, Type, ctx):
		super().__init__(ctx)
		self.Count = Int4(ctx)
		self.Elems = [Type(ctx) for _ in range(self.Count.value())]
	def __getitem__(self, key):
		if (key in range(self.Count.value()+1)):
			return self.Elems[key]
		else:
			raise AttributeError("Bad key: {} / {}".format(key, self.Count.value()))
		
class FixedArray(Primitive):
	def __init__(self, Type, Count, ctx):
		super().__init__(ctx)
		self.Count = Count
		self.Elems = [Type(ctx) for _ in range(self.Count.value())]
		self._ctx = ctx
	def __getitem__(self, key):
		if (key in range(self.Count.value()+1)):
			return self.Elems[key]
		else:
			raise AttributeError("Bad key: {} / {}".format(key, self.Count.value()))
	def to_dump(self):
		d = {
			'Count' : self.Count,
		}
		for i,entry in enumerate(self.Elems):
			d[i] = entry
		return d
			
class EObjectFlags(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Flags = UInt4(ctx)
class EDynamicType(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Flags = UInt4(ctx)
	def value(self):
		return self.Flags
class FCustomVersion(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Key = UE4Guid(ctx)
	
class FGenerationInfo(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.ExportCount = Int4(ctx)
		self.NameCount = Int4(ctx)
		
class FEngineVersion(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Major = UInt4(ctx)
		self.Minor = UInt4(ctx)
		self.Patch = UInt4(ctx)
		self.Changeset = UInt4(ctx)
		
class FNameEntry(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Name = UE4String(ctx)
		self.NonCasePreservingHash = UInt2(ctx)
		self.CasePreservingHash = UInt2(ctx)
	def to_dump(self):
		return {
			'Name' : self.Name.String
		}
class FName(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Index = Int4(ctx)
		self._unknown = UInt4(ctx)
		self._get_names = lambda: ctx.Names
	def value(self):
		return self._get_names()[self.Index.value()]
	def to_dump(self):
		return {
			'String' : self.value().Name.String,
			'Index' : self.Index,
		}
class FName_short(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Index = Int4(ctx)
		self._get_names = lambda: ctx.Names
	def value(self):
		return self._get_names()[self.Index.value()]
	def to_dump(self):
		return {
			'Index' : self.Index,
			'Value' : self.value(),
		}
		
class FPackageIndex(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Index = Int4(ctx)
		self._get_imports = lambda: ctx.Imports
		self._get_exports = lambda: ctx.Exports
	def ref(self):
		importIndex = 0 - self.Index.value() - 1
		exportIndex = self.Index.value() - 1
		isImport = self.Index.value() < 0
		isExport = self.Index.value() > 0
		if (isImport):
			return self._get_imports()[importIndex]
		if (isExport):
			return self._get_exports()[exportIndex]
		return None
	
	def value(self):
		obj = self.ref()
		if obj is None:
			return "Null"
		else:
			return self.ref()
			
	def to_dump(self):
		return {
			'Index' : self.Index,
			'Value' : self.value()
		}

class FObjectImport(BaseElem):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.ClassPackage = FName(ctx)
		self.ClassName = FName(ctx)
		self.PackageRef = FPackageIndex(ctx)
		self.ObjectName = FName(ctx)
	def to_dump(self):
		return {
			'ObjectName' : self.ObjectName
		}
class FObjectExport(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.ClassIndex = FPackageIndex(ctx)
		self.SuperIndex = FPackageIndex(ctx)
		self.TemplateIndex = FPackageIndex(ctx)
		self.OuterIndex = FPackageIndex(ctx)
		self.ObjectName = FName(ctx)
		self.ObjectFlags = EObjectFlags(ctx)
		self.SerialSize = Int8(ctx)
		self.SerialOffset = Int8(ctx)
		self.ForcedExport = UE4Bool(ctx)
		self.NotForClient = UE4Bool(ctx)
		self.NotForServer = UE4Bool(ctx)
		self.PackageGuid = UE4Guid(ctx)
		self.PackageFlags = UInt4(ctx)
		self.NotAlwaysLoadedForEditorGame = UE4Bool(ctx)
		self.IsAsset = UE4Bool(ctx)
		self.FirstExportDependency = Int4(ctx)
		self.SerializationBeforeSerializationDependencies = UE4Bool(ctx)
		self.CreateBeforeSerializationDependencies = UE4Bool(ctx)
		self.SerializationBeforeCreateDependnecies = UE4Bool(ctx)
		self.CreateBeforeCreateDependencies = UE4Bool(ctx)
		#self.DynamicType = EDynamicType(ctx)
	def to_dump(self):
		return {
			'ClassIndex' : self.ClassIndex.ref().ObjectName.value().Name.String,
			'ObjectName' : self.ObjectName.value().Name.String
		}
class FPackageFileSummary(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Tag = Int4(ctx)
		self.FileVersionUE4 = Int4(ctx)
		self.FileVersionLicenseeUE4 = Int4(ctx)
		self.FileVersionUE3 = Int4(ctx)
		self.FileVersionLicenseeUE3 = Int4(ctx)
		self.CustomVersion = PrefixArray(FCustomVersion, ctx)
		self.TotalHeaderSize = Int4(ctx)
		self.FolderName = UE4String(ctx)
		self.PackageFlags = UInt4(ctx)
		self.NameCount = Int4(ctx)
		self.NameOffset = Int4(ctx)
		
		if (ctx.debug):
			print("Creating Names array @ {}".format(self.NameOffset.value()))
		saved = ctx.tell()
		ctx.seek(self.NameOffset.value())
		self.Names = FixedArray(FNameEntry, self.NameCount, ctx)
		ctx.Names = self.Names
		ctx.seek(saved)
		

		
		self.GatherableNameCount = Int4(ctx)
		self.GatherableNameOffset = Int4(ctx)
		self.ExportCount = Int4(ctx)
		self.ExportOffset = Int4(ctx)
		
		if (ctx.debug):
			print("Creating Export (len={}) array @ {}".format(self.ExportCount.value(), self.ExportOffset.value()))
		saved = ctx.tell()
		ctx.seek(self.ExportOffset.value())
		self.Exports = FixedArray(FObjectExport, self.ExportCount, ctx)
		ctx.Exports = self.Exports
		ctx.seek(saved)
		
		self.ImportCount = Int4(ctx)
		self.ImportOffset = Int4(ctx)
		
		if (ctx.debug):
			print("Creating Import array @ {}".format(self.ImportOffset.value()))
		saved = ctx.tell()
		ctx.seek(self.ImportOffset.value())
		self.Imports = FixedArray(FObjectImport, self.ImportCount, ctx)
		ctx.Imports = self.Imports
		ctx.seek(saved)
		
		self.DependsOffset = Int4(ctx)
		self.SoftPackageReferenceCount = Int4(ctx)
		self.SoftPackageReferenceOffset = Int4(ctx)
		self.SearchableNameOffset = Int4(ctx)
		self.ThumbnailTableOffset = Int4(ctx)
		self.Guid = UE4Guid(ctx)
		self.Generations = PrefixArray(FGenerationInfo, ctx)
		self.SavedByEngineVersion = FEngineVersion(ctx)
		self.CompatibleWithEngineVersion = FEngineVersion(ctx)
		self.CompressionFlags = UInt4(ctx)
		self.PackageSource = UInt4(ctx)
		self.UnVersioned = UE4Bool(ctx)
		self.AssetRegistryDataOffset = Int4(ctx)
		self.BulkDataStartOffset = Int8(ctx)
		self.WorldTileInfoDataOffset = Int4(ctx)
		self.ChunkIDs = PrefixArray(Int4, ctx)
		self.PreloadDependencyCount = Int4(ctx)
		self.PreloadDependencyOffset = Int4(ctx)
		
		"""
		if (ctx.debug):
			print("Exports:")
			for export in self.Exports:
				print(json.dumps(export, cls=CustomEncoder, indent=2, sort_keys=True))
				print("\n")
			print("\n\n\n")
		"""
		
class UAsset(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Summary = FPackageFileSummary(ctx)
		
		if (ctx.debug):
			print("Summary finished parsing, creating exports...")
		"""
		print("Names:")
		for i,n in enumerate(self.Summary.Names):
			print(i, n)
		"""
		
		for export in self.Summary.Exports:
			if (ctx.debug):
				print("Serial offset={}".format(export.SerialOffset))
				print("Total Header Size={}".format(self.Summary.TotalHeaderSize.value()))
				
			save = ctx.tell()
			
			
			#if (self.Summary.TotalHeaderSize.value() <= export.SerialOffset.value()):
			if (False):
				if (ctx.debug):
					print("SerialOffset >= TotalHeaderSize! Attempting to use .uexp...")
					f = ctx.stream.name #blah.uasset
					fname = f[:-7] + ".uexp"
					with open(fname, 'rb') as file:
						subctx = ParserCtx(file, ctx.debug)
						subctx.Names = ctx.Names
						subctx.Exports = ctx.Exports
						subctx.Imports = ctx.Imports
						
						subctx.seek( export.SerialOffset.value() - self.Summary.TotalHeaderSize.value())
						export.Object = UObject(subctx, doPad=True, extra=export)
			else:
				ctx.seek(export.SerialOffset.value())
				export.Object = UObject(ctx, doPad=True, extra=export)
				
			ctx.seek(save)
			
class UObject(Primitive):
	def __init__(self, ctx, doPad=False, extra=None):
		super().__init__(ctx)
		if (ctx.debug):
			print("UObject starting @ {}".format(ctx.tell()))
		self.Tags = []
		self.Extra = None
		while(True):		
			if (ctx.debug):
				print("Decoding tag @ {}".format(ctx.tell()))
			saved = ctx.tell()
			#Grab FName, see if it is 'None'
			temp = FName(ctx)
			s = temp.value().Name.value()
			if 'None' in s:
				if (ctx.debug):
					print("'None' tag found @ {}\n".format(temp.offset))
				break
			#Not a 'None' tag, revert position	
			ctx.seek(saved)
			#Decode full FPropertyTag header
			tag = FPropertyTag(ctx)			
			#Use tag.TypeName to decode proper tag
			ctx.seek(saved)
			if (ctx.debug):
				print("Header decoded:")
				print(tag.to_dump())
			#Grab Type hash
			hash = tag.Type.value().CasePreservingHash.value()
			#decode and construct full tag
			dec = ctx.decodeHash(hash)(ctx)
			
			if (ctx.debug):
				print("Final:")
				print(dec.to_dump())
				
			self.Tags.append(dec)
		
		if (doPad):
			if (ctx.debug):
				print("Reading in padding @ {}".format( ctx.tell()))
			self.padding = UInt4(ctx)				
			
		if (extra is not None):
			if (ctx.debug):
				print("Processing extra data starting @ {}".format(ctx.tell()))
				print("Extra data:")
				print(extra.to_dump())
				
			objname = extra.ClassIndex.ref().ObjectName
			taghash = objname.value().CasePreservingHash.value()
				
			lookup = {
				0x10EE : UDataTable,
				0x8FD5 : UStringTable,
				
			}
				
			if (taghash in lookup):
				self.Extra = lookup[taghash](ctx)
			else:
				#print("Hash not in lookup")
				#raise NotImplementedError("{} hash=0x{:02X}".format(objname, taghash))
				self.Extra = UUnknownExport(ctx, objname, taghash, extra.SerialSize)
		if (ctx.debug):
			print("[UObject] end")
	def to_dump(self):
		return {
			'Tags' : self.Tags,
			'Extra' : self.Extra
		}

class UUnknownExport(Primitive):
	def __init__(self, ctx, name, hash, size):
		super().__init__(ctx)
		if (ctx.debug):
			print("Unknown top-level export type: {} (hash=0x{:04X})".format(name, hash))
			print("Blindly reading in {} bytes...".format(size.value()))
		self.Unknown = ctx.read(size.value())
		
class UStructProperty_special(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		if (ctx.debug):
			print("Unknown top-level StructProperty!?")
			print("Blindly reading in bytes specified in ExportSize...")
		self.Unknown = ctx.read(36)
class UDataTable(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		if (ctx.debug):
			print("[UDataTable] @ {}".format(ctx.tell()))
		self.Count = Int4(ctx)
		self.Data = [UDataTable_Entry(ctx) for _ in range(self.Count.value())]
	def to_dump(self):
		return {
			'Count' : self.Count,
			'Data' : self.Data
		}
		

class UDataTable_Entry(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Index = FName_short(ctx)
		self._unknown = UInt4(ctx)
		self.Obj = UObject(ctx, doPad=False, extra=None)
	def to_dump(self):
		return {
			'Name' : self.Index.value().Name.String,
			'Obj' : self.Obj
		}
		
class UStringTable(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Unknown = UInt4(ctx)
		self.Count = Int4(ctx)
		self.Elems = dict()
		if (ctx.debug):
			print("String Table: reading in {} elements".format(self.Count))
		for i in range(self.Count.value()):
			self.Elems[ UE4String(ctx) ] = UE4String(ctx)
		if (ctx.debug):
			print("String table ends @ {}".format(ctx.tell()))
		
class FPropertyGuid(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.HasGuid = UInt1(ctx)
		if (self.HasGuid.value() != 0):
			self.Guid = UInt16(ctx)
class FPropertyTag(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Name = FName(ctx)
		self.Type = FName(ctx)
		self.Size = Int4(ctx)
		self.Index = Int4(ctx)
	def __str__(self):
		return "FPropertyTag(Name={}, Type={}, Size={}, Index={})".format(self.Name, self.Type, self.Size, self.Index)
	def to_dump(self):
		d = {
			'Name' : self.Name.value().Name.String,
			'Type' : self.Type.value().Name.String,
		}
		if hasattr(self, 'value'):
			if callable(self.value):
				d['value'] = self.value()
			else:
				d['value'] = self.value
		if hasattr(self, 'Value'):
			if callable(self.Value):
				d['Value'] = self.Value()
			else:
				d['Value'] = self.Value
		return d

		
class UArrayProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.ArrayType = FName(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Count = Int4(ctx)
		
		h = self.ArrayType.value().CasePreservingHash.value()
		tagclass = ctx.decodeHash(h)
		#Store size to figure out how much extra crap to read
		saved = ctx.tell()
		
		self.Elems = []
		if tagclass is UStructProperty:
			self.Elems.append(tagclass(ctx))
		else:
			
			for i in range(self.Count.value()):
			
				lookup = {
					UBoolProperty : lambda ctx: UInt1(ctx),
					UIntProperty : lambda ctx: Int4(ctx),
					UUInt32Property : lambda ctx: UInt4(ctx),
					UByteProperty : lambda ctx: UInt1(ctx),
					UFloatProperty : lambda ctx: Float4(ctx),
					UStrProperty : lambda ctx: UE4String(ctx),
					UObjectProperty : lambda ctx: FPackageIndex(ctx),
					UNameProperty : lambda ctx: FName(ctx)
				}
				if tagclass in lookup:
					self.Elems.append(lookup[tagclass](ctx))
					
				else:
					raise NotImplementedError("ArrayProp w/ {}, hash={}".format(tagclass, h))
		current = ctx.tell()
		nextTag = saved + self.Size.value() - 4
		if (nextTag - current) > 0:
			if (ctx.debug):
				print("Current={}, NextTag={}".format(current, nextTag))
			self.Unknown = ctx.read(nextTag - current)
		ctx.seek( saved + self.Size.value()-4)
		if (ctx.debug):
			print("ArrayProperty(Type={}, Count={})".format(self.ArrayType, self.Count))
	def to_dump(self):
		raise NotImplementedError(self.__class__.__name__ + " can't be dumped")
		
class UStructProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.StructName = FName(ctx)
		self.StructGuid = UE4Guid(ctx)
		self.Guid = FPropertyGuid(ctx)
		
		saved = ctx.tell()
		try:
			self.Value = UObject(ctx, doPad=False, extra=None)
		except Exception as e:
			if (ctx.debug):
				print("Exception in UStructProperty: {}".format(e))
				print("Continuing by blind-reading {} bytes from {} to {}" \
				.format(self.Size.value(), ctx.tell(), ctx.tell() + self.Size.value()))
			ctx.seek(saved)
			self.Value = ctx.read(self.Size.value())
class UObjectProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = FPackageIndex(ctx)
class USoftObjectProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Package = FName(ctx)
		self.Path = UE4String(ctx)
	def to_dump(self):
		raise NotImplementedError(self.__class__.__name__ + " can't be dumped")
class UByteProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.EnumName = FName(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = FName(ctx)
class UStrProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = UE4String(ctx)
class UNameProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = FName(ctx)
class UIntProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = Int4(ctx)
class UUInt32Property(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Value = UInt4(ctx)
		self.Guid = FPropertyGuid(ctx)
class UBoolProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Value = UInt1(ctx)
		self.Guid = FPropertyGuid(ctx)
class UFloatProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = Float4(ctx)
class UEnumProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.EnumName = FName(ctx)
		self.Guid = FPropertyGuid(ctx)
		self.Value = FName(ctx)
class UTextProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		if self.Size.value() < 8:			
			pos = ctx.tell()
			ctx.seek(pos + 0x19 + self.Size.value())
			if (ctx.debug):
				print("TextProperty jump forward to {}".format(ctx.tell()))
		self.Guid = FPropertyGuid(ctx)
		self.Unknown = UInt8(ctx)
		self.Key = FPropertyGuid(ctx)
		self.Hash = UE4String(ctx)
		self.Value = UE4String(ctx)
	def to_dump(self):
		raise NotImplementedError(self.__class__.__name__ + " can't be dumped")
		
class UMulticastDelegateProperty(FPropertyTag):
	def __init__(self, ctx):
		super().__init__(ctx)
		#TODO: wtf is this
		self.Guid = FPropertyGuid(ctx)
		self.Unknown = ctx.read(16)
	def to_dump(self):
		raise NotImplementedError(self.__class__.__name__ + " can't be dumped")