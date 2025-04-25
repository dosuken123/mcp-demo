from fastapi import APIRouter
from typing import Annotated, Optional, List, Dict, Any
from backend.auth.utils import User, get_current_user
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form


def validate_mcp_headers(request: Request):
    if not request.headers.get("Origin"):
        raise HTTPException(status_code=400, detail="Missing Origin header")
    return request


router = APIRouter(dependencies=[Depends(validate_mcp_headers)])


@router.get("/mcp")
async def mcp_get(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.post("/mcp")
async def mcp_post(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
