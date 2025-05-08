from fastapi import APIRouter
from typing import Annotated, Optional, List, Dict, Any
from backend.auth.utils import User, get_current_user
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from backend.mcp.schema import ListToolsResult, Tool


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


@router.post("/mcp")
async def mcp_post(
    current_user: Annotated[User, Depends(get_current_user)],
):
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
    return result.model_dump()
