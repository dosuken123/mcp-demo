from fastapi import APIRouter
from typing import Annotated
from backend.auth.utils import User, get_current_user
from fastapi import (
    Depends,
    Request,
    Response,
)
from fastapi.responses import StreamingResponse
from anthropic import AsyncAnthropic, BadRequestError

router = APIRouter()


@router.post("/inference", status_code=202)
async def inference(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    inferenceRequest: dict,
):
    client = AsyncAnthropic()

    try:
        stream = await client.messages.create(
            max_tokens=1024,
            messages=inferenceRequest['messages'],
            tools=inferenceRequest['tools'],
            model="claude-3-5-sonnet-latest",
            stream=True,
        )
    except BadRequestError as ex:
        return Response(content=f"Failed to perform inference. error: {ex}", status_code=ex.status_code)
    except Exception as ex:
        return Response(content=f"Failed to perform inference. error: {ex}", status_code=500)

    async def streaming_response():
        async for event in stream:
            yield "event: " + event.type + "\n"
            yield "data: " + event.model_dump_json() + "\n\n"

    return StreamingResponse(streaming_response(), media_type="text/event-stream")
