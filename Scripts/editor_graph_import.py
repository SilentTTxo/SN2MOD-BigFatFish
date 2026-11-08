"""Editor-only adapter for UE 5.6.1's exported graph text importer.

Python has no public graph-pin wiring wrapper. Invoke the editor's own T3D
import API, without installing a runtime plugin or touching asset bytes/pins.
Use only in a disposable commandlet with the project's pinned custom editor.
"""
import ctypes as C
from pathlib import Path
import unreal

class FString(C.Structure):
    _fields_ = [("data", C.c_void_p), ("num", C.c_int32), ("max", C.c_int32)]

def remove_node(blueprint, node):
    binaries = Path(__file__).resolve().parents[1] / "Engine/SN2-Engine-V4/Engine/Binaries/Win64"
    core = C.WinDLL(str(binaries / "UnrealEditor-CoreUObject.dll"))
    find = getattr(core, "?StaticFindObject@@YAPEAVUObject@@PEAVUClass@@PEAV1@PEB_W_N@Z")
    find.argtypes = [C.c_void_p, C.c_void_p, C.c_wchar_p, C.c_bool]
    find.restype = C.c_void_p
    editor = C.WinDLL(str(binaries / "UnrealEditor-UnrealEd.dll"))
    remove = getattr(editor, "?RemoveNode@FBlueprintEditorUtils@@SAXPEAVUBlueprint@@PEAVUEdGraphNode@@_N@Z")
    remove.argtypes = [C.c_void_p, C.c_void_p, C.c_bool]
    remove.restype = None
    remove(find(None,None,blueprint.get_path_name(),False), find(None,None,node.get_path_name(),False), True)

def connect_nodes(source, source_pin, destination, destination_pin):
    binaries = Path(__file__).resolve().parents[1] / "Engine/SN2-Engine-V4/Engine/Binaries/Win64"
    core = C.WinDLL(str(binaries / "UnrealEditor-CoreUObject.dll"))
    find = getattr(core, "?StaticFindObject@@YAPEAVUObject@@PEAVUClass@@PEAV1@PEB_W_N@Z")
    find.argtypes = [C.c_void_p,C.c_void_p,C.c_wchar_p,C.c_bool];find.restype=C.c_void_p
    engine=C.WinDLL(str(binaries / "UnrealEditor-Engine.dll"))
    pin=getattr(engine,"?FindPin@UEdGraphNode@@QEBAPEAVUEdGraphPin@@PEB_WW4EEdGraphPinDirection@@@Z")
    pin.argtypes=[C.c_void_p,C.c_wchar_p,C.c_int];pin.restype=C.c_void_p
    a=pin(find(None,None,source.get_path_name(),False),source_pin,1)
    b=pin(find(None,None,destination.get_path_name(),False),destination_pin,0)
    assert a and b, f"Missing graph pins: {source.get_name()}.{source_pin} -> {destination.get_name()}.{destination_pin}"
    link=getattr(engine,"?MakeLinkTo@UEdGraphPin@@QEAAXPEAV1@_N@Z")
    link.argtypes=[C.c_void_p,C.c_void_p,C.c_bool];link.restype=None
    link(a,b,True)

def import_nodes(graph, text):
    assert unreal.SystemLibrary.get_engine_version().startswith("5.6.1-"), "Pinned editor ABI required"
    binaries = Path(__file__).resolve().parents[1] / "Engine/SN2-Engine-V4/Engine/Binaries/Win64"
    core = C.WinDLL(str(binaries / "UnrealEditor-CoreUObject.dll"))
    find = getattr(core, "?StaticFindObject@@YAPEAVUObject@@PEAVUClass@@PEAV1@PEB_W_N@Z")
    find.argtypes = [C.c_void_p, C.c_void_p, C.c_wchar_p, C.c_bool]
    find.restype = C.c_void_p
    graph_pointer = find(None, None, graph.get_path_name(), False)
    assert graph_pointer, "Graph must already be owned by the animation blueprint"
    editor = C.WinDLL(str(binaries / "UnrealEditor-UnrealEd.dll"))
    importer = getattr(editor, "?ImportNodesFromText@FEdGraphUtilities@@SAXPEAVUEdGraph@@AEBVFString@@AEAV?$TSet@PEAVUEdGraphNode@@U?$DefaultKeyFuncs@PEAVUEdGraphNode@@$0A@@@VFDefaultSetAllocator@@@@@Z")
    importer.argtypes = [C.c_void_p, C.POINTER(FString), C.c_void_p]
    importer.restype = None
    buffer = C.create_unicode_buffer(text)
    source = FString(C.cast(buffer, C.c_void_p), len(text) + 1, len(text) + 1)
    # Empty FDefaultSetAllocator storage; import initializes and fills this
    # output-only set. Its allocations live only until this commandlet exits.
    imported_nodes = (C.c_uint64 * 64)()
    importer(graph_pointer, C.byref(source), C.byref(imported_nodes))
