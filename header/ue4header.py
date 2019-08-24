#UE4 Header information structures

from primitives import *
from ue4basic import *
from ue4arrays import *

class EObjectFlags(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Flags = UInt4(ctx)
class EDynamicType(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Flags = UInt4(ctx)

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

class FName(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Index = Int8(ctx)
		self._get_names = lambda: ctx.Names
		
class FPackageIndex(Primitive):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.Index = Int4(ctx)
		self._get_imports = lambda: ctx.Imports
		self._get_exports = lambda: ctx.Exports

class FObjectImport(BaseElem):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.ClassPackage = FName(ctx)
		self.ClassName = FName(ctx)
		self.PackageRef = FPackageIndex(ctx)
		self.ObjectName = FName(ctx)
		
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
		self.DynamicType = EDynamicType(ctx)
		
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
		self.GatherableNameCount = Int4(ctx)
		self.GatherableNameOffset = Int4(ctx)
		self.ExportCount = Int4(ctx)
		self.ExportOffset = Int4(ctx)
		self.ImportCount = Int4(ctx)
		self.ImportOffset = Int4(ctx)
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