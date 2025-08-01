## Installation

1. Install [mise](https://mise.jdx.dev/getting-started.html).
1. Run `mise install` to install runtime.
1. Install dependencies:
    ```
    cd backend
    poetry install
    ```

## Start server

Open a terminal and run:

```shell
poetry run fastapi dev backend/main.py --host localhost
```

If you test inference, you need to set the following environment variables before running the command:

```
export ANTHROPIC_API_KEY=[REDACTED]
```

## Test modules

Enter python interactive session:

```python
poetry run python
```

Try out a module:

```python
from backend.mcp.schema import JSONRPCRequest

JSONRPCRequest(id="1", method="test", params={"a": "b"})
```

## Regenerate MCP JSONRPC 2.0 schema

MCP provides the [schema](https://modelcontextprotocol.io/specification/2025-06-18/basic#schema) for server-client communication.
This schema is provided as [typescript](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2025-06-18/schema.ts) as single source of truth,
and [JSON](https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-06-18/schema.json) as auto-converted version.

You can convert the JSON schema into python module by the following script:

```shell
export ANTHROPIC_API_KEY=[REDACTED]
export MCP_VERSION=$(cat backend/mcp/VERSION)
export JSON_SCHEMA_URL=https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/${MCP_VERSION}/schema.json

make schema
```

Later you can test the generated module by [test modules](#test-modules) section.

## Test MCP endpoints

Run a server with `BYPASS_AUTH=true`.
Setting `BYPASS_AUTH=true` allows you to directly access to the MCP endpoints:

```shell
export BYPASS_AUTH=true
poetry run fastapi dev backend/main.py --host localhost
```

Send a single message:

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -d '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/list",
  "params": {
    "additionalProp1": {}
  }
}'
```

Send a batch messages:

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -d '[
  {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "string",
    "params": {
      "additionalProp1": {}
    }
  },
  {
    "jsonrpc": "2.0",
    "method": "string",
    "params": {
      "additionalProp1": {}
    }
  },
  {
    "jsonrpc": "2.0",
    "id": "2",
    "result": {}
  }
]'
```

### Example: Initialization

https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle#initialization

**method: initialize**

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "ExampleClient",
      "version": "1.0.0"
    }
  }
}'
```

**method: notifications/initialized**

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}'
```

**method: ping**

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "id": "123",
  "method": "ping"
}'
```

### Example: Tools

#### method: tools/list

Request:

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/list",
  "params": {
    "additionalProp1": {}
  }
}'
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "tools": [
      {
        "name": "read_blog_post",
        "inputSchema": {
          "blog_post_id": {
            "type": "str"
          }
        },
        "description": "Read a blog post that the user wrote"
      },
      {
        "name": "create_blog_post",
        "inputSchema": {
          "content": {
            "type": "str",
            "description": "Content of the blog post"
          }
        },
        "description": "Create a new blog post"
      },
      {
        "name": "update_blog_post",
        "inputSchema": {
          "blog_post_id": {
            "type": "str"
          },
          "new_content": {
            "type": "str",
            "description": "New content of the blog post"
          }
        },
        "description": "Update an existing blog post"
      }
    ]
  }
}
```

#### method: tools/call

Request `read_blog_post`:

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "read_blog_post",
    "arguments": {
      "blog_post_id": 1
    }
  }
}'
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Here is the content of the blog post 1 authored by johndoe\n\nYesterday was a good day"
      }
    ]
  }
}
```

Request `create_blog_post`:

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -d '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "create_blog_post",
    "arguments": {
      "content": "Tomorrow will be a nice day"
    }
  }
}'
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "New blog post 3 is successfully created by johndoe"
      }
    ]
  }
}
```

Request `update_blog_post`:

```shell
curl -X POST \
     http://localhost:8000/mcp \
     -H 'Content-Type: application/json' \
     -H 'Accept: application/json, text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "update_blog_post",
    "arguments": {
      "blog_post_id": 1,
      "new_content": "Day after tomorrow will be an awesome day"
    }
  }
}'
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Existing blog post 1 is successfully updated by johndoe"
      }
    ]
  }
}
```

## Test inference

Backend also provides a inference endpoint for generating an AI response.
You can test by the following endpoint:

```shell
curl -X POST \
     http://localhost:8000/inference \
     -H 'Content-Type: application/json' \
     -H 'Accept: text/event-stream' \
     -H 'Authorization: Bearer dummy' \
     -H 'Origin: localhost:5173' \
     -H 'MCP-Protocol-Version: 2025-06-18' \
     -d '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "update_blog_post",
    "arguments": {
      "blog_post_id": 1,
      "new_content": "Day after tomorrow will be an awesome day"
    }
  }
}'
```

## Test Login screen for OAuth

Access this URL in a web browser:

```
http://localhost:8000/oauth/authorize?response_type=code&client_id=my-mcp-client&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fcallback&code_challenge=abc123
```
