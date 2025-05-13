from typing import Annotated, Optional, List, Dict, Any, TypeAlias
from backend.mcp.schema import (
    ListToolsResult,
    Tool,
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    ClientRequest,
    Result,
    InitializeResult,
    EmptyResult,
    Implementation,
    ServerCapabilities,
    ToolsCapabilities,
    InitializeRequest as InitializeRequestBase,
    ListToolsRequest as ListToolsRequestBase,
    PingRequest as PingRequestBase,
)
from backend.auth.utils import User
from abc import ABC, abstractmethod


JSONRPC: TypeAlias = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse


class Processable(ABC):
    user: User  # For authorization and filtering data based on user

    @abstractmethod
    def process(self) -> Result: ...


class InitializeRequest(Processable, InitializeRequestBase):
    def process(self) -> Result:
        # See https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle#capability-negotiation
        # for more capability negotiations
        return InitializeResult(
            serverInfo=Implementation(name="My MCP Server", version="0.0.1"),
            protocolVersion="2025-03-26",
            capabilities=ServerCapabilities(tools=ToolsCapabilities(listChanged=False)),
            instructions="Optional instructions for the client",
        )


class ListToolsRequest(Processable, ListToolsRequestBase):
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


class PingRequest(Processable, PingRequestBase):
    def process(self) -> Result:
        return EmptyResult()


def process_rpc(rpc: JSONRPC, user: User):
    if not isinstance(rpc, JSONRPCRequest):
        raise NotImplementedError(f"{rpc.__class__} is not implemented")

    request: ClientRequest = None

    match rpc.method:
        case "initialize":
            request = InitializeRequest(user=user, params=rpc.params)
        case "ping":
            request = PingRequest(user=user)
        case "tools/list":
            request = ListToolsRequest(user=user, **rpc.params)
        case _:
            raise ValueError(f"Unknown request method: {rpc.method}")

    result: Result = request.process()

    return JSONRPCResponse(
        id=rpc.id,
        result=result,
    )
