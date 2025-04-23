## Installation

1. Install [mise](https://mise.jdx.dev/getting-started.html).
1. Run `mise install` to install runtime.
1. Install dependencies:
    ```
    cd backend
    poetry install
    ```

## Start server

```
cd backend
poetry run fastapi dev backend/main.py --host localhost
```

## Test modules

```python
poetry run python
```

```python
from backend.mcp import ErrorCode, Error, ErrorResponse

e = Error(code=ErrorCode.ErrorCodeParseError, message="error desc")
res = ErrorResponse(error=e, id=1)
res.model_dump_json()
```

