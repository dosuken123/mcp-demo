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
from backend.mcp.schema import JSONRPCRequest

JSONRPCRequest(id="1", method="test", params={"a": "b"})
```

## Regenerate MCP JSONRPC 2.0 schema

MCP provides the [schema](https://modelcontextprotocol.io/specification/2025-03-26/basic#schema) for server-client communication.
This schema is provided as [typescript](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2025-03-26/schema.ts) as single source of truth,
and [JSON](https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-03-26/schema.json) as auto-converted version.

You can convert the JSON schema into python module by the following script:

```shell
export ANTHROPIC_API_KEY=[REDACTED]
export JSON_SCHEMA_URL=https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2025-03-26/schema.json

make schema
```

Later you can test by:

```shell
poetry run python
```

```python
from backend.mcp.schema import JSONRPCRequest

JSONRPCRequest(id="1", method="test", params={"a": "b"})
```
