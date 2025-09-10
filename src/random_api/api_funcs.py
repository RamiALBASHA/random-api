from json import loads
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, create_model


def convert_type(t: str):
    if t == "integer":
        return {"type": "integer"}
    elif t == "float":
        return {"type": "number", "format": "float"}
    else:
        return {"type": "string"}


def create_schema_properties() -> dict[str, Any]:
    meta = loads(Path("metadata/all_variables.json").read_text())

    schema_props = {}
    for name, spec in meta.items():
        _default = spec.get("default", None)
        _type = spec["type"]
        prop = convert_type(_type)
        prop["description"] = spec.get("description", "")
        if _default is not None:
            prop["default"] = float(_default) if _type == "float" else int(_default) if _type == "integer" else _default
        if "minimum" in spec:
            prop["minimum"] = spec["minimum"]
        if "maximum" in spec:
            prop["maximum"] = spec["maximum"]
        schema_props[name] = prop

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


def build_pydantic_models(schema_properties: dict[str, Any]) -> BaseModel:
    fields = {}
    for name, spec in schema_properties.items():
        _type = spec["type"]
        typ = int if _type == "integer" else float if _type == "number" else str
        constraints = {}
        if "minimum" in spec:
            constraints["ge"] = spec["minimum"]
        if "maximum" in spec:
            constraints["le"] = spec["maximum"]
        default_value = spec.get("default")
        if isinstance(typ, float):
            default_value = float(default_value)

        # Add field
        fields[name] = (
            typ,
            Field(
                default=default_value,
                description=spec.get("description", ""),
                **constraints),
        )

    return create_model("TheComponent", **fields)


if __name__ == "__main__":
    set_openapi_specs(
        schemas_properties=create_schema_properties(),
        is_write_specs=True,
    )
