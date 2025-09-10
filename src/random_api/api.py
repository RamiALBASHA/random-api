from fastapi import FastAPI

from random_api.api_funcs import create_schema_properties, build_pydantic_models
from random_api.main import entrypoint

RandomVariables = build_pydantic_models(schema_properties=create_schema_properties())

app = FastAPI(title="Random API", version="1.0.0", openapi_version="3.1.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Random API service"}


@app.get("/metadata/schema")
def get_schema():
    """Return JSON Schema for validation"""
    return RandomVariables.model_json_schema()


@app.post("/generate")
def generate(input_data: RandomVariables):
    """Echo back validated inputs (baseline test)"""
    return {"inputs": input_data.dict()}


@app.post("/run")
def run_entrypoint(input_data: RandomVariables):
    """Run entrypoint() from main.py with validated inputs"""
    try:
        result = entrypoint(**input_data.dict())
        res = {"status": "success", "result": result}
    except Exception as e:
        res = {"status": "failure", "error": str(e)}
    return res
