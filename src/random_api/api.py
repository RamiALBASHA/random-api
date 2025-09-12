from pathlib import Path

from fastapi import FastAPI

from random_api.config import FILE_NAME_GENERATED_PYDANTIC_CLASSES_MODULE
from random_api.main import entrypoint

with (Path(__file__).parent / FILE_NAME_GENERATED_PYDANTIC_CLASSES_MODULE).open(mode='r') as f:
    exec(f.read())
app = FastAPI(title="Random API", version="1.0.0", openapi_version="3.1.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Random API service"}


@app.get("/metadata/schema")
def get_schema():
    """Return JSON Schema for validation"""
    return InputsClass.model_json_schema()


@app.post("/run")
def run_entrypoint(input_data: InputsClass):
    """Run entrypoint() from main.py with validated inputs"""
    try:
        result = entrypoint(**input_data.dict())
        res = {"status": "success", "result": result}
    except Exception as e:
        res = {"status": "failure", "error": str(e)}
    return res
