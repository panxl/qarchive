jsonschema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema#",
    "name": "qarchive_schema",
    "version": "1.dev",
    "description": "The Q-Chem archive file",
    "type": "object",
    "properties": {
        "job": {}
    }
}


def convert_schema(source, dest, is_top_level=False, add_extras=False):
    for key, value in source.items():
        if key == "job":
            convert_schema(value, dest['properties']['job'], is_top_level=True, add_extras=add_extras)
            for key, value in dest['properties']['job']['items']['properties'].items():
                dest[key] = value
                dest['properties']['job']['items']['properties'][key] = {"$ref": f"#/{key}"}
                if add_extras:
                    dest['properties']['job']['items']['properties'][key]["x-init"] = False
                    dest['properties']['job']['items']['properties'][key]["x-repr"] = False
            return

        if isinstance(value, dict):
            if key == "_layers":
                key = "properties"
            if dest.get("items") is not None:
                dest = dest["items"]
            if key not in dest:
                dest[key] = {}
            convert_schema(value, dest[key], is_top_level=False, add_extras=add_extras)
        else:
            if key == "#ref":
                key = "$ref"
            elif key == "type" and value == "layer":
                value = "object"
            elif key == "docstring":
                key = "description"
            elif key == "shape" and value != []:
                dest["items"] = {}
            dest[key] = value

            if value == "iterable_layer" or value ==  "countable_layer":
                dest[key] = "array"
                if "items" not in dest:
                    dest['items'] = {"type": "object"}
            elif value == "double":
                dest[key] = "number"
            elif value == "int" or value == "size_t" or value == "unsigned":
                dest[key] = "integer"
            elif value == "bool":
                dest[key] = "boolean"
            elif value == "std::complex<double>":
                dest[key] = "number"
            elif value == "#/observables/multipole_moments":
                dest[key] = "#/observables/properties/multipole_moments"

            if add_extras:
                dest["x-init"] = False
                dest["x-repr"] = False

    if "shape" in source and source['shape'] != []:
        dest["items"]["type"] = dest["type"]
        dest["type"] = "array"

    if not is_top_level:
        if "_metadata" in source and source["_metadata"].get("can_add_sp"):
            dest["properties"]['sp'] = {
                "$ref": "#/sp",
                }
            if add_extras:
                dest["properties"]['sp']["x-init"] = False
                dest["properties"]['sp']["x-repr"] = False
            

if __name__ == "__main__":
    import sys
    import json

    with open(sys.argv[1], 'r') as f:
        schema = json.load(f)

    convert_schema(schema, jsonschema, add_extras=True)

    json.dump(jsonschema, open('qarchive_schema.json', 'w'), indent=4)
