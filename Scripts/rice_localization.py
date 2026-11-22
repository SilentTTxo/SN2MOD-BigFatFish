"""Native FText identities; source English falls back for every other culture."""
import json
CATALOG={
 'GrainName':('Sea Rice Grain','海稻'),
 'PlantName':('Sea Rice','海稻'),
 'GrainDescription':('Plant in an aquafarm with the builder. Keep some grains for replanting.','使用建造器在种植槽栽种，留一部分海稻再种。'),
 'PlantDescription':('Grow sea rice in a planter. Harvest the ripe panicles at the crown.','在种植槽栽种海稻，采收顶部成熟的稻穗。'),
 'BuildDescription':('Plant sea rice in a planter.','在种植槽里栽种海稻。'),
 'Growth':('Sea Rice: {0}%','海稻：{0}%'),
 'FoodName':('Steamed Rice','大白饭'),
 'FoodDescription':('Freshly steamed sea rice. Restores 25 food. Drop a bowl for more than 3 seconds to attract a new Big Fat Fish.','热腾腾的大白饭，食用恢复 25 饱食度。丢下一碗超过 3 秒，会引来一只新的大肥鱼。'),
 'MealDescription':('Steam 1 sea rice grain with 1 water.','使用 1 份海稻和 1 份净水蒸制。'),
}
def set_text(obj,prop,key):
 from editor_property_import import set_properties
 set_properties(obj,prop+'=NSLOCTEXT("BigFatFishRice",'+json.dumps(key)+','+json.dumps(CATALOG[key][0])+')')
