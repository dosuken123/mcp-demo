from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum

# JSON-RPC 2.0 Specification https://www.jsonrpc.org/specification
class JSONRPC(BaseModel):
    jsonrpc: str = '2.0'

class Request(JSONRPC):
    method: str
    id: str | int
    params: Optional[list | dict]

class Notification(JSONRPC):
    method: str
    params: Optional[list | dict]

class SuccessResponse(JSONRPC):
    result: dict = None
    id: str | int = None

class ErrorCode(Enum):
    ErrorCodeParseError = -32700
    ErrorCodeInvalidRequest = -32600
    ErrorCodeMethodNotFound = -32601
    ErrorCodeInvalidParams = -32602
    ErrorCodeInternalError = -32603
    ErrorCodeServerError = -32000

class Error(BaseModel):
    code: int | ErrorCode
    message: str
    data: Optional[str | dict] = None

class ErrorResponse(JSONRPC):
    error: Error
    id: Optional[str | int] = None

