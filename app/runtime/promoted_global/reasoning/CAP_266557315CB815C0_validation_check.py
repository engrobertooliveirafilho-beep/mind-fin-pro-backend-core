import json, os

base = os.path.dirname(__file__)
map_path = os.path.join(base, "promotion_map.json")

with open(map_path,"r") as f:
    data=json.load(f)

assert len(data["promote_shadow"])==5
assert len(data["promote_review"])==5
assert data["production_enabled"] is False
assert data["runtime_mutation"] is False

print("P19P53A VALIDATION OK")
