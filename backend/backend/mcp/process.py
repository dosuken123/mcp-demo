from typing import TypeAlias
from backend.mcp.schema import (
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
    ListToolsResult,
    CallToolResult,
    TextContent,
    InitializeRequest as InitializeRequestBase,
    ListToolsRequest as ListToolsRequestBase,
    CallToolRequest as CallToolRequestBase,
    PingRequest as PingRequestBase,
)
from backend.auth.utils import User, db_in_memory
from abc import ABC, abstractmethod
from functools import lru_cache
import os

JSONRPC: TypeAlias = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse


class Processable(ABC):
    user: User  # For authorization and filtering data based on user

    @abstractmethod
    def process(self) -> Result: ...


class InitializeRequest(Processable, InitializeRequestBase):
    def process(self) -> Result:
        # See https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle#capability-negotiation
        # for more capability negotiations
        return InitializeResult(
            serverInfo=Implementation(name="My MCP Server", version="0.0.1"),
            protocolVersion="2025-06-18",
            capabilities=ServerCapabilities(tools=ToolsCapabilities(listChanged=False)),
            instructions="Optional instructions for the client",
        )


class ListToolsRequest(Processable, ListToolsRequestBase):
    def process(self) -> Result:
        return ListToolsResult(
            tools=[
                Tool(
                    name="read_blog_post",
                    description="Read a blog post that the user wrote",
                    inputSchema={"blog_post_id": {"type": "str"}},
                ),
                Tool(
                    name="create_blog_post",
                    description="Create a new blog post",
                    inputSchema={
                        "content": {
                            "type": "str",
                            "description": "Content of the blog post",
                        }
                    },
                ),
                Tool(
                    name="update_blog_post",
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


class CallToolRequest(Processable, CallToolRequestBase):
    def process(self) -> Result:
        if self.params.name == "read_blog_post":
            return self.read_blog_post()
        elif self.params.name == "create_blog_post":
            return self.create_blog_post()
        elif self.params.name == "update_blog_post":
            return self.update_blog_post()
        else:
            raise ValueError(f"Tool name {self.params.name} not Found")

    def read_blog_post(self):
        blog_post_id = int(self.params.arguments["blog_post_id"])

        for blog_post_dict in db_in_memory["blog_posts"]:
            if (
                blog_post_dict["user_id"] == self.user.id
                and blog_post_dict["id"] == blog_post_id
            ):
                return CallToolResult(
                    content=[
                        TextContent(
                            text=f"Here is the content of the blog post {blog_post_id} authored by {self.user.username}\n\n{blog_post_dict['content']}"
                        )
                    ],
                )

        return CallToolResult(
            content=[
                TextContent(
                    text=f"Blog post {blog_post_id} not found for user {self.user.id}"
                )
            ],
            isError=True,
        )

    def create_blog_post(self):
        new_blog_post_id = len(db_in_memory["blog_posts"]) + 1
        blog_post_dict = {
            "id": new_blog_post_id,
            "user_id": self.user.id,
            "content": self.params.arguments["content"],
        }
        db_in_memory["blog_posts"].append(blog_post_dict)

        return CallToolResult(
            content=[
                TextContent(
                    text=f"New blog post {new_blog_post_id} is successfully created by {self.user.username}"
                )
            ]
        )

    def update_blog_post(self):
        blog_post_id = int(self.params.arguments["blog_post_id"])

        for blog_post_dict in db_in_memory["blog_posts"]:
            if (
                blog_post_dict["user_id"] == self.user.id
                and blog_post_dict["id"] == blog_post_id
            ):
                blog_post_dict["content"] = self.params.arguments["new_content"]

                return CallToolResult(
                    content=[
                        TextContent(
                            text=f"Existing blog post {blog_post_id} is successfully updated by {self.user.username}"
                        )
                    ],
                )

        return CallToolResult(
            content=[
                TextContent(
                    text=f"Blog post {blog_post_id} not found for user {self.user.id}"
                )
            ],
            isError=True,
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
            request = ListToolsRequest(user=user, params=rpc.params)
        case "tools/call":
            request = CallToolRequest(user=user, params=rpc.params)
        case _:
            raise ValueError(f"Unknown request method: {rpc.method}")

    result: Result = request.process()

    return JSONRPCResponse(
        id=rpc.id,
        result=result,
    )


@lru_cache
def get_mcp_version():
    path = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(path) as f:
        version = f.read()
    return version
