import json


def dump_json(filename, payload):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
