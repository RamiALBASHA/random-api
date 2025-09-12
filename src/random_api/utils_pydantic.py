import re
from typing import Dict, Any, Optional, get_args, get_origin

from pydantic import Field, create_model, BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from random_api.config import FILE_NAME_GENERATED_PYDANTIC_CLASSES_MODULE


def verify_is_nested_field(d: dict) -> bool:
    return d["type"] == "object"  # and "properties" in d


def get_python_type(field_type: str) -> type:
    """Map string types to Python types."""
    type_mapping = {
        "integer": int,
        "int": int,
        "float": float,
        "number": float,
        "string": str,
        "str": str,
        "boolean": bool,
        "bool": bool,
        "array": list,
        "list": list,
        "object": dict,
        "dict": dict,
    }
    return type_mapping.get(field_type.lower(), str)


def create_field_definition(field_config: Dict[str, Any]) -> tuple:
    """Create a Pydantic field definition from config."""
    python_type = get_python_type(field_type=field_config.get("type", "str"))

    # Build Field parameters
    field_kwargs = {"description": field_config.get("description", "")}

    # Add constraints based on type
    if any([python_type is int, python_type is float]):
        if "minimum" in field_config:
            field_kwargs["ge"] = field_config["minimum"]
        if "maximum" in field_config:
            field_kwargs["le"] = field_config["maximum"]
    elif python_type is str:
        if "min_length" in field_config:
            field_kwargs["min_length"] = field_config["min_length"]
        if "max_length" in field_config:
            field_kwargs["max_length"] = field_config["max_length"]
    elif python_type is list:
        if "min_items" in field_config:
            field_kwargs["min_length"] = field_config["min_items"]
        if "max_items" in field_config:
            field_kwargs["max_length"] = field_config["max_items"]

    return python_type, Field(default=field_config['default'], **field_kwargs)


def process_schema(
        schema_dict: Dict[str, Any],
        model_name: str
) -> type[BaseModel]:
    """Recursively process schema and create Pydantic models."""
    fields = {}
    nested_models = {}

    for field_name, field_config in schema_dict.items():
        if verify_is_nested_field(d=field_config):
            # Handle nested objects
            nested_class_name = field_name.capitalize()
            nested_model = process_schema(
                schema_dict=field_config["properties"],
                model_name=nested_class_name)
            nested_models[nested_class_name] = nested_model

            if "default" in field_config:
                # If there's a default, make it optional
                fields[field_name] = (Optional[nested_model], None)
            else:
                fields[field_name] = (nested_model, ...)

            if "description" in field_config:
                if fields[field_name][1] is None:
                    fields[field_name] = (fields[field_name][0],
                                          Field(None, description=field_config["description"]))
                else:
                    fields[field_name] = (fields[field_name][0], Field(description=field_config["description"]))
        else:
            fields[field_name] = create_field_definition(field_config)

    # Create the model
    model = create_model(model_name, **fields)

    # Store nested models as class attributes for easy access
    for nested_name, nested_model in nested_models.items():
        setattr(model, nested_name, nested_model)

    return model


def dict_to_pydantic_classes(schema: Dict[str, Any], class_name: str = "GeneratedModel") -> type[BaseModel]:
    """
    Convert a dictionary schema to Pydantic classes.

    Args:
        schema: Dictionary containing field definitions with type, description, default, etc.
        class_name: Name for the main Pydantic class

    Returns:
        Pydantic model class
    """

    return process_schema(
        schema_dict=schema,
        model_name=class_name)


def _is_nested_model(annotation: type) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


def _get_type_string(annotation: type) -> str:
    if isinstance(annotation, type):
        type_str = annotation.__name__
    elif get_origin(annotation):
        args = ", ".join(getattr(a, "__name__", str(a)) for a in get_args(annotation))
        type_str = f"{get_origin(annotation).__name__}[{args}]"
    else:
        type_str = str(annotation)
    return type_str


def _get_field_args(field: FieldInfo) -> list[str]:
    field_args: list[str] = []
    if all([
        field.default is not None,
        field.default is not ...,
        field.default is not PydanticUndefined,
    ]):
        field_args.append(f"default={repr(field.default)}")
    elif field.is_required():
        field_args.append("...")
    else:
        field_args.append("None")
    if field.description:
        field_args.append(f"description={repr(field.description)}")
    if field.title:
        field_args.append(f"title={repr(field.title)}")
    if field.metadata is not None:
        for md in field.metadata:
            field_args.append(re.search(r'\((.*?)\)', str(md)).group(1))

    return field_args


def build_pydantic_model_scripts(
        model: type[BaseModel],
        seen: set[type[BaseModel]] | None = None
) -> str:
    """Generate Python source code for a Pydantic model class (recursive)."""
    if seen is None:
        seen = set()

    if model in seen:
        return ""

    seen.add(model)

    lines: list[str] = []

    for name, field in model.model_fields.items():
        annotation = field.annotation
        if _is_nested_model(annotation=annotation):
            lines.append(build_pydantic_model_scripts(model=annotation, seen=seen))

    lines.append(f"class {model.__name__}(BaseModel):")

    for name, field in model.model_fields.items():
        type_str = _get_type_string(annotation=field.annotation)
        field_args = _get_field_args(field)

        lines.append(f"    {name}: {type_str} = Field({', '.join(field_args)})")

    lines += ["", ""]

    return "\n".join(lines)


def write_pydantic_classes(model: type[BaseModel]):
    return "\n\n".join([
        f'"""\nThis file is generated automatically using func `{write_pydantic_classes.__name__}`\n"""',
        "from pydantic import BaseModel, Field\n",
        build_pydantic_model_scripts(model=model, seen=None),
    ])


if __name__ == "__main__":
    from random_api.api_funcs import create_schema_properties, read_meta_data

    generated_model = dict_to_pydantic_classes(
        schema=create_schema_properties(read_meta_data()),
        class_name="InputsClass")

    with open(FILE_NAME_GENERATED_PYDANTIC_CLASSES_MODULE, mode='w', encoding='utf-8') as f:
        f.write(write_pydantic_classes(model=generated_model))
