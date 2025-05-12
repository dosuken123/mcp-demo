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
    JSONRPCError,
)
from backend.mcp.process import process_rpc, JSONRPC


def validate_mcp_headers(request: Request):
    if not request.headers.get("Origin"):
        raise HTTPException(status_code=400, detail="Missing Origin header")
    return request


router = APIRouter(dependencies=[Depends(validate_mcp_headers)])


@router.get("/mcp")
async def mcp_get(
    current_user: Annotated[User, Depends(get_current_user)],
    accept: Annotated[str | None, Header()] = "text/event-stream",
):
    if "text/event-stream" in accept:
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid Accept header")

    # https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#sending-messages-to-the-server
    # Listening for Messages from the Server
    # The client MAY issue an HTTP GET to the MCP endpoint. This can be used to open an SSE stream, allowing the server to communicate to the client, without the client first sending data via HTTP POST.
    raise HTTPException(
        status_code=405,
        detail="Not implemented: Listening for Messages from the Server",
    )


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

    responses: List[JSONRPCResponse] = []
    for r in rpc:
        try:
            response = process_rpc(r)
        except Exception as e:
            response = JSONRPCError(id=r.id, error={"message": str(e)})
        responses.append(response)

    # https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#sending-messages-to-the-server
    # The SSE stream SHOULD eventually include one JSON-RPC response per each JSON-RPC request sent in the POST body. These responses MAY be batched.
    # The server MAY send JSON-RPC requests and notifications before sending a JSON-RPC response. These messages SHOULD relate to the originating client request. These requests and notifications MAY be batched.
    async def streaming_response():
        yield "event: begin\n"
        for r in responses:
            yield "data: " + r.model_dump_json(serialize_as_any=True)
            yield "\n\n"
        yield "event: end\n"
        yield "data: {}\n\n"

    if len(responses) == 1:
        return JSONResponse(
            content=responses[0].model_dump(serialize_as_any=True),
            media_type="application/json",
        )
    else:
        return StreamingResponse(streaming_response(), media_type="text/event-stream")
