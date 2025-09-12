from pathlib import Path

_PATH_ROOT = Path(__file__).parent
_PATH_AUTOMATICALLY_GENERATED = _PATH_ROOT / 'automatically_generated'
PATH_GENERATED_PYDANTIC_CLASSES_MODULE: Path = _PATH_AUTOMATICALLY_GENERATED / 'pydantic_models.py'
