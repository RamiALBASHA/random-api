# random_api
`random-api` is a small learning project that implements an API structure using `FastAPI` with `OpenAPI 3.1`
specifications for a simple Python package.

# How it works
- The Python package (`random_api`) is provided with metadata (`metadata/all_variables.json`) that specify the specs of
all input variables used by the entrypoint `main.entrypoint()`.
- The module `api_funcs.py` allows reading the metadata and creates a JSON schema compliant with `OpenAPI 3.1` specs.
- The module `main_pydantic.py` uses `api_funcs.py` functions to create the JSON schema which is in turn used to
build `pydantic` models that are necessary for validating the API inputs. The `pydantic` model declarations are written
in a module named `pydantic_models.py` stored under `automatically_generated`.
The name of this module is defined in `config.py`.
- When launched, the script in `api.py` imports the `pydantic` models from `pydantic_models.py` which are then used to
validate the user inputs when calling the endpoint `/run`. 


# Installation

1. Clone the repo from github
    ```bash
    git clone git@github.com:RamiALBASHA/random-api.git
    cd random-api
    ```

2. Install the package using `pip`
    ```bash
    pip install -e .
    ```

3. Expose the API with `FastAPI` and `uvicorn`
    ```bash
    uvicorn random_api.api:app --reload --port 8080
    ```

4. Check out the doc in your browser

    With Swagger UI: http://127.0.0.1:8080/docs

    Alternative, with ReDoc documentation: http://127.0.0.1:8080/redoc  

5. Check out the entrypoint endpoint

    * Open a new terminal and call the endpoint with empty inputs, which will results in using the default values defined
    in the `metadata` file `all_variables.json`:
 
    ```bash
    curl -X POST http://127.0.0.1:8080/run -H "Content-Type: application/json" -d '{"stuff": {"a": 1, "b": 2}}'
    ```
    You should get:

    ```bash
    {"status":"success","result":{"done_this":0.5,"done_that":-1.0,"do_it":3}}
    ```

    * Alternatively, provide input values:
    ```bash
    curl -X POST http://127.0.0.1:8080/run -H "Content-Type: application/json" -d '{"toto": -1, "tata": 1, "titi": 1, "param": 1, "stuff": {"a": 1, "b": 2}}'
    ```

    * You should get:

    ```bash
    {"status":"success","result":{"done_this":-1.0,"done_that":0.0,"do_it":3}}
    ```

   * Now test with unallowed values:
    ```bash
    curl -X POST http://127.0.0.1:8080/run -H "Content-Type: application/json" -d '{"toto": -100, "stuff": {"a": 1, "b": 2}}'
    ```
 
    You should get:

    ```bash
    {"detail":[{"type":"greater_than_equal","loc":["body","toto"],"msg":"Input should be greater than or equal to -5","input":-100,"ctx":{"ge":-5}}]}
    ```
   
   You're done!
 