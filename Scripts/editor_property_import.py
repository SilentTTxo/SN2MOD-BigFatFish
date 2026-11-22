"""Use UE 5.6.1's own property-text importer for Suzie reflected enums/structs.

Suzie adds game types after Python has generated its wrappers. Primitive
properties remain accessible, but some game enums/structs have no Python type.
This calls the editor's exported ImportObjectProperties API; it never patches
object/property memory or asset bytes. The ABI is pinned to this editor build.
"""
import ctypes as C
from pathlib import Path
import unreal

class ImportParams(C.Structure):
    _fields_=[('dest',C.c_void_p),('source',C.c_wchar_p),('object_struct',C.c_void_p),
              ('root',C.c_void_p),('outer',C.c_void_p),('warn',C.c_void_p),
              ('depth',C.c_int32),('line',C.c_int32),('instance_graph',C.c_void_p),
              ('remapper',C.c_void_p),('edit_change',C.c_bool)]

def set_properties(obj,text):
    assert unreal.SystemLibrary.get_engine_version().startswith('5.6.1-')
    assert C.sizeof(ImportParams)==80
    binaries=Path(__file__).resolve().parents[1]/'Engine/SN2-Engine-V4/Engine/Binaries/Win64'
    core_object=C.WinDLL(str(binaries/'UnrealEditor-CoreUObject.dll'))
    find=getattr(core_object,'?StaticFindObject@@YAPEAVUObject@@PEAVUClass@@PEAV1@PEB_W_N@Z')
    find.argtypes=[C.c_void_p,C.c_void_p,C.c_wchar_p,C.c_bool];find.restype=C.c_void_p
    pointer=find(None,None,obj.get_path_name(),False)
    class_pointer=find(None,None,obj.get_class().get_path_name(),False)
    assert pointer and class_pointer,obj.get_path_name()
    core=C.WinDLL(str(binaries/'UnrealEditor-Core.dll'))
    warn=C.c_void_p.in_dll(core,'?GWarn@@3PEAVFFeedbackContext@@EA').value
    editor=C.WinDLL(str(binaries/'UnrealEditor-UnrealEd.dll'))
    importer=getattr(editor,'?ImportObjectProperties@@YAPEB_WAEAUFImportObjectParams@@@Z')
    importer.argtypes=[C.POINTER(ImportParams)];importer.restype=C.c_void_p
    source=C.create_unicode_buffer(text.rstrip()+'\n')
    params=ImportParams(pointer,C.cast(source,C.c_wchar_p),class_pointer,pointer,pointer,warn,0,-1,None,None,True)
    assert importer(C.byref(params)),('Property import failed',obj.get_path_name())
