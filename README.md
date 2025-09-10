# random_api
`random-api` is a testing Python package for learning how to implement an API structure with `FastAPI` and
`OpenAPI 3.1` specifications.

# The testing package
The package entrypoint is `main.entrypoint()`. This entrypoint is called by the API endpoint `/run`. The API itself
is built with `OpenAPI 3.1` specifications which are dynamically created out of the manually-set metadata specifications
(`metadata/all_variables.json`). `Pydantic` classes are dynamically built out of the `OpenAPI` specifications,
allowing to validate user inputs when calling the endpoints.

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
    curl -X POST http://127.0.0.1:8080/run -H "Content-Type: application/json" -d '{}'
    ```
    You should get:

    ```bash
    {"status":"success","result":{"done_this":0.5,"done_that":-1.0}}
    ```

    * Alternatively, provide input values:
    ```bash
    curl -X POST http://127.0.0.1:8080/run -H "Content-Type: application/json" -d '{"toto": -1, "tata": 1, "titi": 1, "param": 1}'
    ```

    * You should get:

    ```bash
    {"status":"success","result":{"done_this":-1.0,"done_that":0.0}}
    ```

   * Now test with unallowed values:
    ```bash
    curl -X POST http://127.0.0.1:8080/run -H "Content-Type: application/json" -d '{"toto": -100}'
    ```
 
    You should get:

    ```bash
    {"detail":[{"type":"greater_than_equal","loc":["body","toto"],"msg":"Input should be greater than or equal to -5","input":-100,"ctx":{"ge":-5}}]}
    ```
   
   You're done!
 