from json import loads
from pathlib import Path
from typing import Any

import yaml

PATH_METADATA: Path = Path(__file__).parents[2] / "metadata/all_variables.json"


def read_meta_data() -> dict:
    return loads(PATH_METADATA.read_text())


def convert_type(t: str):
    match t:
        case "integer" | "int":
            res = {"type": "integer"}
        case "float":
            res = {"type": "number", "format": "float"}
        case "object":
            res = {"type": "object"}
        case _:
            res = {"type": "string"}
    return res


def extract_properties(d: dict) -> dict:
    _default = d.get("default", None)
    _type = d["type"]
    prop = convert_type(_type)
    prop["description"] = d.get("description", "")
    if _default is not None:
        prop["default"] = float(_default) if _type == "float" else int(_default) if _type == "integer" else _default
    if "minimum" in d:
        prop["minimum"] = d["minimum"]
    if "maximum" in d:
        prop["maximum"] = d["maximum"]

    return prop


def create_schema_properties(meta: dict) -> dict[str, Any]:
    schema_props = {}
    for name, spec in meta.items():
        schema_props[name] = extract_properties(d=spec)
        if 'properties' in spec:
            schema_props[name]['properties'] = {}
            for k, v in spec['properties'].items():
                schema_props[name]['properties'].update({k: extract_properties(v)})

    return schema_props


def create_openapi_specs(schema_props: dict[str, Any]) -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "random-api",
            "version": "1.0.0"
        },
        "paths": {
            "/metadata/schema": {
                "get": {
                    "summary": "Get JSON Schema",
                    "responses": {
                        "200": {
                            "description": "JSON Schema for input validation",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
            "/run": {
                "post": {
                    "summary": "Run the entrypoint of random-api",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TheComponent"}
                            }
                        }

                    },
                    "responses": {
                        "200": {
                            "description": "Result of entrypoint run",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                    }
                                }
                            },
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "TheComponent": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": schema_props,
                }
            }
        },
    }


def set_openapi_specs(schemas_properties: dict, is_write_specs: bool = False) -> None:
    openapi = create_openapi_specs(schema_props=schemas_properties)
    if is_write_specs:
        Path("openapi.yaml").write_text(yaml.dump(openapi, sort_keys=False))


if __name__ == "__main__":
    set_openapi_specs(
        schemas_properties=create_schema_properties(meta=read_meta_data()),
        is_write_specs=True,
    )
