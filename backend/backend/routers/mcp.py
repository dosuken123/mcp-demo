from fastapi import APIRouter
from typing import Annotated, Optional, List, Dict, Any, TypeAlias
from backend.auth.utils import User, get_current_user
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Form,
    Header,
    Response,
)
from fastapi.responses import JSONResponse, StreamingResponse
from backend.mcp.schema import (
    ListToolsResult,
    Tool,
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
)


def validate_mcp_headers(request: Request):
    if not request.headers.get("Origin"):
        raise HTTPException(status_code=400, detail="Missing Origin header")
    return request


router = APIRouter(dependencies=[Depends(validate_mcp_headers)])


@router.get("/mcp")
async def mcp_get(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"message": "not implemented"}]


JSONRPC: TypeAlias = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse


@router.post("/mcp", status_code=202)
async def mcp_post(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    rpc: JSONRPC | List[JSONRPC],
    accept: Annotated[str | None, Header()] = "application/json, text/event-stream",
):
    if "application/json" in accept and "text/event-stream" in accept:
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid Accept header")

    if not isinstance(rpc, List):
        rpc = [rpc]

    result = ListToolsResult(
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
    # return JSONResponse(content=result.model_dump(), media_type="application/json")

    # https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#sending-messages-to-the-server
    # The SSE stream SHOULD eventually include one JSON-RPC response per each JSON-RPC request sent in the POST body. These responses MAY be batched.
    async def streaming_response():
        yield "event: begin\n"
        for r in rpc:
            if isinstance(r, JSONRPCRequest):
                yield "data: " + JSONRPCResponse(
                    id=r.id, result=result
                ).model_dump_json(serialize_as_any=True)
                yield "\n\n"
        yield "event: end\n"
        yield "data: {}\n\n"

    return StreamingResponse(streaming_response(), media_type="text/event-stream")
