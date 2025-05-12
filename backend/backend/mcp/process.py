from typing import Annotated, Optional, List, Dict, Any, TypeAlias
from backend.mcp.schema import (
    ListToolsResult,
    Tool,
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    ClientRequest,
    Result,
    InitializeRequest as InitializeRequestBase,
    ListToolsRequest as ListToolsRequestBase,
)

JSONRPC: TypeAlias = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse


class InitializeRequest(InitializeRequestBase):
    def process(self) -> Result:
        pass


class ListToolsRequest(ListToolsRequestBase):
    def process(self) -> Result:
        return ListToolsResult(
            tools=[
                Tool(
                    name="read_user_blog_post",
                    description="Read a blog post that the user wrote",
                    inputSchema={"blog_post_id": {"type": "str"}},
                ),
                Tool(
                    name="create_user_blog_post",
                    description="Create a new blog post",
                    inputSchema={
                        "content": {
                            "type": "str",
                            "description": "Content of the blog post",
                        }
                    },
                ),
                Tool(
                    name="update_user_blog_post",
                    description="Update an existing blog post",
                    inputSchema={
                        "blog_post_id": {"type": "str"},
                        "new_content": {
                            "type": "str",
                            "description": "New content of the blog post",
                        },
                    },
                ),
            ]
        )


def _cast_client_request(rpc: JSONRPCRequest):
    match rpc.method:
        case "initialize":
            return InitializeRequest(**rpc.params)
        case "tools/list":
            return ListToolsRequest(**rpc.params)
        case _:
            raise ValueError(f"Unknown request method: {rpc.method}")


def process_rpc(rpc: JSONRPC):
    if not isinstance(rpc, JSONRPCRequest):
        raise NotImplementedError(f"{rpc.__class__} is not implemented")

    request: ClientRequest = _cast_client_request(rpc)
    result: Result = request.process()

    return JSONRPCResponse(
        id=rpc.id,
        result=result,
    )
