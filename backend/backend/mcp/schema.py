
# This file is auto-generated based on https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2025-03-26/schema.json - do not modify manually.
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class Role(StrEnum):
    """The sender or recipient of messages and data in a conversation."""
    ASSISTANT = "assistant"
    USER = "user"

class Annotations(BaseModel):
    """Optional annotations for the client. The client can use annotations to inform how objects are used or displayed"""
    audience: Optional[List[Role]] = None
    priority: Optional[float] = None

class TextContent(BaseModel):
    """Text provided to or from an LLM."""
    text: str
    type: str = "text"
    annotations: Optional[Annotations] = None

class ImageContent(BaseModel):
    """An image provided to or from an LLM."""
    data: str
    mimeType: str
    type: str = "image"
    annotations: Optional[Annotations] = None

class AudioContent(BaseModel):
    """Audio provided to or from an LLM."""
    data: str
    mimeType: str
    type: str = "audio"
    annotations: Optional[Annotations] = None

class TextResourceContents(BaseModel):
    text: str
    uri: str
    mimeType: Optional[str] = None

class BlobResourceContents(BaseModel):
    blob: str
    uri: str
    mimeType: Optional[str] = None

class EmbeddedResource(BaseModel):
    """The contents of a resource, embedded into a prompt or tool call result.

    It is up to the client how best to render embedded resources for the benefit
    of the LLM and/or the user."""
    resource: Union[TextResourceContents, BlobResourceContents]
    type: str = "resource"
    annotations: Optional[Annotations] = None

# Type aliases for simple types
RequestId = Union[str, int]
"""A uniquely identifying ID for a request in JSON-RPC."""

ProgressToken = Union[str, int]
"""A progress token, used to associate progress notifications with the original request."""

Cursor = str
"""An opaque token used to represent a cursor for pagination."""

class Implementation(BaseModel):
    """Describes the name and version of an MCP implementation."""
    name: str
    version: str

class ClientCapabilities(BaseModel):
    """Capabilities a client may support. Known capabilities are defined here, in this schema, but this is not a closed set: any client can define its own, additional capabilities."""
    experimental: Optional[Dict[str, Dict[str, Any]]] = None
    roots: Optional[Dict[str, bool]] = None
    sampling: Optional[Dict[str, Any]] = None

class ServerCapabilities(BaseModel):
    """Capabilities that a server may support. Known capabilities are defined here, in this schema, but this is not a closed set: any server can define its own, additional capabilities."""
    completions: Optional[Dict[str, Any]] = None
    experimental: Optional[Dict[str, Dict[str, Any]]] = None
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, bool]] = None
    resources: Optional[Dict[str, bool]] = None
    tools: Optional[Dict[str, bool]] = None

class InitializeRequest(BaseModel):
    """This request is sent from the client to the server when it first connects, asking it to begin initialization."""
    method: str = "initialize"
    params: Dict[str, Any] = Field(...)

class InitializeResult(BaseModel):
    """After receiving an initialize request from the client, the server sends this response."""
    _meta: Optional[Dict[str, Any]] = None
    capabilities: ServerCapabilities
    instructions: Optional[str] = None
    protocolVersion: str
    serverInfo: Implementation

class InitializedNotification(BaseModel):
    """This notification is sent from the client to the server after initialization has finished."""
    method: str = "notifications/initialized"
    params: Optional[Dict[str, Any]] = None

class PingRequest(BaseModel):
    """A ping, issued by either the server or the client, to check that the other party is still alive. The receiver must promptly respond, or else may be disconnected."""
    method: str = "ping"
    params: Optional[Dict[str, Any]] = None

class Result(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class EmptyResult(Result):
    pass

class LoggingLevel(StrEnum):
    """The severity of a log message.

    These map to syslog message severities, as specified in RFC-5424:
    https://datatracker.ietf.org/doc/html/rfc5424#section-6.2.1"""
    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"

class SetLevelRequest(BaseModel):
    """A request from the client to the server, to enable or adjust logging."""
    method: str = "logging/setLevel"
    params: Dict[str, Any] = Field(...)

class LoggingMessageNotification(BaseModel):
    """Notification of a log message passed from server to client. If no logging/setLevel request has been sent from the client, the server MAY decide which messages to send automatically."""
    method: str = "notifications/message"
    params: Dict[str, Any] = Field(...)

class CancelledNotification(BaseModel):
    """This notification can be sent by either side to indicate that it is cancelling a previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request."""
    method: str = "notifications/cancelled"
    params: Dict[str, Any] = Field(...)

class ProgressNotification(BaseModel):
    """An out-of-band notification used to inform the receiver of a progress update for a long-running request."""
    method: str = "notifications/progress"
    params: Dict[str, Any] = Field(...)

class PaginatedRequest(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None

class PaginatedResult(BaseModel):
    _meta: Optional[Dict[str, Any]] = None
    nextCursor: Optional[str] = None

class Resource(BaseModel):
    """A known resource that the server is capable of reading."""
    name: str
    uri: str
    annotations: Optional[Annotations] = None
    description: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[int] = None

class ResourceContents(BaseModel):
    """The contents of a specific resource or sub-resource."""
    uri: str
    mimeType: Optional[str] = None

class ResourceTemplate(BaseModel):
    """A template description for resources available on the server."""
    name: str
    uriTemplate: str
    annotations: Optional[Annotations] = None
    description: Optional[str] = None
    mimeType: Optional[str] = None

class ListResourcesRequest(BaseModel):
    """Sent from the client to request a list of resources the server has."""
    method: str = "resources/list"
    params: Optional[Dict[str, Any]] = None

class ListResourcesResult(BaseModel):
    """The server's response to a resources/list request from the client."""
    _meta: Optional[Dict[str, Any]] = None
    resources: List[Resource]
    nextCursor: Optional[str] = None

class ListResourceTemplatesRequest(BaseModel):
    """Sent from the client to request a list of resource templates the server has."""
    method: str = "resources/templates/list"
    params: Optional[Dict[str, Any]] = None

class ListResourceTemplatesResult(BaseModel):
    """The server's response to a resources/templates/list request from the client."""
    _meta: Optional[Dict[str, Any]] = None
    resourceTemplates: List[ResourceTemplate]
    nextCursor: Optional[str] = None

class ReadResourceRequest(BaseModel):
    """Sent from the client to the server, to read a specific resource URI."""
    method: str = "resources/read"
    params: Dict[str, Any] = Field(...)

class ReadResourceResult(BaseModel):
    """The server's response to a resources/read request from the client."""
    _meta: Optional[Dict[str, Any]] = None
    contents: List[Union[TextResourceContents, BlobResourceContents]]

class SubscribeRequest(BaseModel):
    """Sent from the client to request resources/updated notifications from the server whenever a particular resource changes."""
    method: str = "resources/subscribe"
    params: Dict[str, Any] = Field(...)

class ResourceUpdatedNotification(BaseModel):
    """A notification from the server to the client, informing it that a resource has changed and may need to be read again. This should only be sent if the client previously sent a resources/subscribe request."""
    method: str = "notifications/resources/updated"
    params: Dict[str, Any] = Field(...)

class UnsubscribeRequest(BaseModel):
    """Sent from the client to request cancellation of resources/updated notifications from the server. This should follow a previous resources/subscribe request."""
    method: str = "resources/unsubscribe"
    params: Dict[str, Any] = Field(...)

class ResourceListChangedNotification(BaseModel):
    """An optional notification from the server to the client, informing it that the list of resources it can read from has changed. This may be issued by servers without any previous subscription from the client."""
    method: str = "notifications/resources/list_changed"
    params: Optional[Dict[str, Any]] = None

class PromptArgument(BaseModel):
    """Describes an argument that a prompt can accept."""
    name: str
    description: Optional[str] = None
    required: Optional[bool] = None

class Prompt(BaseModel):
    """A prompt or prompt template that the server offers."""
    name: str
    arguments: Optional[List[PromptArgument]] = None
    description: Optional[str] = None

class ListPromptsRequest(BaseModel):
    """Sent from the client to request a list of prompts and prompt templates the server has."""
    method: str = "prompts/list"
    params: Optional[Dict[str, Any]] = None

class ListPromptsResult(BaseModel):
    """The server's response to a prompts/list request from the client."""
    _meta: Optional[Dict[str, Any]] = None
    prompts: List[Prompt]
    nextCursor: Optional[str] = None

class PromptMessage(BaseModel):
    """Describes a message returned as part of a prompt.

    This is similar to `SamplingMessage`, but also supports the embedding of
    resources from the MCP server."""
    content: Union[TextContent, ImageContent, AudioContent, EmbeddedResource]
    role: Role

class GetPromptRequest(BaseModel):
    """Used by the client to get a prompt provided by the server."""
    method: str = "prompts/get"
    params: Dict[str, Any] = Field(...)

class GetPromptResult(BaseModel):
    """The server's response to a prompts/get request from the client."""
    _meta: Optional[Dict[str, Any]] = None
    messages: List[PromptMessage]
    description: Optional[str] = None

class PromptListChangedNotification(BaseModel):
    """An optional notification from the server to the client, informing it that the list of prompts it offers has changed. This may be issued by servers without any previous subscription from the client."""
    method: str = "notifications/prompts/list_changed"
    params: Optional[Dict[str, Any]] = None

class ToolAnnotations(BaseModel):
    """Additional properties describing a Tool to clients.

    NOTE: all properties in ToolAnnotations are **hints**.
    They are not guaranteed to provide a faithful description of
    tool behavior (including descriptive properties like `title`).

    Clients should never make tool use decisions based on ToolAnnotations
    received from untrusted servers."""
    destructiveHint: Optional[bool] = None
    idempotentHint: Optional[bool] = None
    openWorldHint: Optional[bool] = None
    readOnlyHint: Optional[bool] = None
    title: Optional[str] = None

class Tool(BaseModel):
    """Definition for a tool the client can call."""
    name: str
    inputSchema: Dict[str, Any]
    annotations: Optional[ToolAnnotations] = None
    description: Optional[str] = None

class ListToolsRequest(BaseModel):
    """Sent from the client to request a list of tools the server has."""
    method: str = "tools/list"
    params: Optional[Dict[str, Any]] = None

class ListToolsResult(BaseModel):
    """The server's response to a tools/list request from the client."""
    _meta: Optional[Dict[str, Any]] = None
    tools: List[Tool]
    nextCursor: Optional[str] = None

class CallToolRequest(BaseModel):
    """Used by the client to invoke a tool provided by the server."""
    method: str = "tools/call"
    params: Dict[str, Any] = Field(...)

class CallToolResult(BaseModel):
    """The server's response to a tool call.

    Any errors that originate from the tool SHOULD be reported inside the result
    object, with `isError` set to true, _not_ as an MCP protocol-level error
    response. Otherwise, the LLM would not be able to see that an error occurred
    and self-correct.

    However, any errors in _finding_ the tool, an error indicating that the
    server does not support tool calls, or any other exceptional conditions,
    should be reported as an MCP error response."""
    _meta: Optional[Dict[str, Any]] = None
    content: List[Union[TextContent, ImageContent, AudioContent, EmbeddedResource]]
    isError: Optional[bool] = None

class ToolListChangedNotification(BaseModel):
    """An optional notification from the server to the client, informing it that the list of tools it offers has changed. This may be issued by servers without any previous subscription from the client."""
    method: str = "notifications/tools/list_changed"
    params: Optional[Dict[str, Any]] = None

class ModelHint(BaseModel):
    """Hints to use for model selection.

    Keys not declared here are currently left unspecified by the spec and are up
    to the client to interpret."""
    name: Optional[str] = None

class ModelPreferences(BaseModel):
    """The server's preferences for model selection, requested of the client during sampling.

    Because LLMs can vary along multiple dimensions, choosing the "best" model is
    rarely straightforward.  Different models excel in different areas—some are
    faster but less capable, others are more capable but more expensive, and so
    on. This interface allows servers to express their priorities across multiple
    dimensions to help clients make an appropriate selection for their use case.

    These preferences are always advisory. The client MAY ignore them. It is also
    up to the client to decide how to interpret these preferences and how to
    balance them against other considerations."""
    costPriority: Optional[float] = None
    hints: Optional[List[ModelHint]] = None
    intelligencePriority: Optional[float] = None
    speedPriority: Optional[float] = None

class SamplingMessage(BaseModel):
    """Describes a message issued to or received from an LLM API."""
    content: Union[TextContent, ImageContent, AudioContent]
    role: Role

class CreateMessageRequest(BaseModel):
    """A request from the server to sample an LLM via the client. The client has full discretion over which model to select. The client should also inform the user before beginning sampling, to allow them to inspect the request (human in the loop) and decide whether to approve it."""
    method: str = "sampling/createMessage"
    params: Dict[str, Any] = Field(...)

class CreateMessageResult(BaseModel):
    """The client's response to a sampling/create_message request from the server. The client should inform the user before returning the sampled message, to allow them to inspect the response (human in the loop) and decide whether to allow the server to see it."""
    _meta: Optional[Dict[str, Any]] = None
    content: Union[TextContent, ImageContent, AudioContent]
    model: str
    role: Role
    stopReason: Optional[str] = None

class Root(BaseModel):
    """Represents a root directory or file that the server can operate on."""
    uri: str
    name: Optional[str] = None

class ListRootsRequest(BaseModel):
    """Sent from the server to request a list of root URIs from the client. Roots allow
    servers to ask for specific directories or files to operate on. A common example
    for roots is providing a set of repositories or directories a server should operate
    on.

    This request is typically used when the server needs to understand the file system
    structure or access specific locations that the client has permission to read from."""
    method: str = "roots/list"
    params: Optional[Dict[str, Any]] = None

class ListRootsResult(BaseModel):
    """The client's response to a roots/list request from the server.
    This result contains an array of Root objects, each representing a root directory
    or file that the server can operate on."""
    _meta: Optional[Dict[str, Any]] = None
    roots: List[Root]

class RootsListChangedNotification(BaseModel):
    """A notification from the client to the server, informing it that the list of roots has changed.
    This notification should be sent whenever the client adds, removes, or modifies any root.
    The server should then request an updated list of roots using the ListRootsRequest."""
    method: str = "notifications/roots/list_changed"
    params: Optional[Dict[str, Any]] = None

class PromptReference(BaseModel):
    """Identifies a prompt."""
    name: str
    type: str = "ref/prompt"

class ResourceReference(BaseModel):
    """A reference to a resource or resource template definition."""
    uri: str
    type: str = "ref/resource"

class CompleteRequest(BaseModel):
    """A request from the client to the server, to ask for completion options."""
    method: str = "completion/complete"
    params: Dict[str, Any] = Field(...)

class CompleteResult(BaseModel):
    """The server's response to a completion/complete request"""
    _meta: Optional[Dict[str, Any]] = None
    completion: Dict[str, Any]

class JSONRPCNotification(BaseModel):
    """A notification which does not expect a response."""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None

class JSONRPCRequest(BaseModel):
    """A request that expects a response."""
    id: RequestId
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None

class JSONRPCResponse(BaseModel):
    """A successful (non-error) response to a request."""
    id: RequestId
    jsonrpc: str = "2.0"
    result: Result

class JSONRPCError(BaseModel):
    """A response to a request that indicates an error occurred."""
    id: RequestId
    jsonrpc: str = "2.0"
    error: Dict[str, Any]

class Notification(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None

class Request(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None

# Union types
class ClientNotification(BaseModel):
    pass

class ServerNotification(BaseModel):
    pass

class ClientRequest(BaseModel):
    pass

class ServerRequest(BaseModel):
    pass

class ClientResult(BaseModel):
    pass

class ServerResult(BaseModel):
    pass

class JSONRPCMessage(BaseModel):
    """Refers to any valid JSON-RPC object that can be decoded off the wire, or encoded to be sent."""
    pass

class JSONRPCBatchRequest(BaseModel):
    """A JSON-RPC batch request, as described in https://www.jsonrpc.org/specification#batch."""
    pass

class JSONRPCBatchResponse(BaseModel):
    """A JSON-RPC batch response, as described in https://www.jsonrpc.org/specification#batch."""
    pass
