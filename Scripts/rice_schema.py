"""Build a reflected type dependency closure for commandlet-safe farming authoring."""
import gzip
import json
from pathlib import Path

ROOTS = [
    "/Script/UWEAbilitySystem.UWEGameplayAbility",
    "/Script/UWEInventory.UWEBaseItem", "/Script/UWEInventory.UWEItemType",
    "/Script/UWECrafting.UWECraftingRecipe", "/Script/Subnautica2.SN2BuilderConstructActionData",
    "/Script/UWEFarming.UWEPlantGrowerComponent", "/Script/UWEFarming.UWESeedGrowerComponent",
    "/Script/UWEFarming.UWESeedGrowerReplicatorComponent", "/Script/UWEFarming.UWESeedData",
    "/Script/UWESaveSystem.UWESaveComponent", "/Script/UWEAssetRegistry.UWEAssetUserData",
    "/Script/UWEAssetRegistry.UWEAssetDataComponent", "/Script/Subnautica2.UWEPlacementAnchor",
    "/Script/Subnautica2.UWEPlacementVolumeComponent",
]

def build_schema(source, destination):
    data=json.loads(gzip.decompress(Path(source).read_bytes()))
    objects=data['objects']; selected={}; pending=list(ROOTS)
    def references(value):
        if isinstance(value,str):
            if value.startswith('/Script/') and value in objects and objects[value].get('type') != 'Package': yield value
        elif isinstance(value,dict):
            for field,child in value.items():
                if field != 'outer': yield from references(child)
        elif isinstance(value,list):
            for child in value: yield from references(child)
    while pending:
        key=pending.pop()
        if key in selected: continue
        definition=dict(objects[key])
        # Actor/component native implementation executes in the game. Editor
        # authoring needs reflected properties and delegate signatures only;
        # unrelated methods pull in the entire UI/game class graph and CDOs.
        if definition.get('type') == 'Class': definition['children']=[]
        selected[key]=definition
        pending.extend(references(definition))
    payload={'metadata':data.get('metadata',{}),'objects':selected}
    Path(destination).write_bytes(gzip.compress(json.dumps(payload).encode('utf8')))
    return len(selected)
