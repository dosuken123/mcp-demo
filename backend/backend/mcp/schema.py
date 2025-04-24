# This file is auto-generated based on https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2025-03-26/schema.json - do not modify manually.

from enum import StrEnum
from typing import Any, Dict, List, Optional, Literal, Union, TypeAlias
from pydantic import BaseModel, Field

# Enums
class Role(StrEnum):
    """The sender or recipient of messages and data in a conversation."""
    ASSISTANT = "assistant"
    USER = "user"

class LoggingLevel(StrEnum):
    """The severity of a log message.

    These map to syslog message severities, as specified in RFC-5424:
    https://datatracker.ietf.org/doc/html/rfc5424#section-6.2.1"""
    ALERT = "alert"
    CRITICAL = "critical"
    DEBUG = "debug"
    EMERGENCY = "emergency"
    ERROR = "error"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"

# Type aliases
RequestId: TypeAlias = Union[str, int]
Cursor: TypeAlias = str
ProgressToken: TypeAlias = Union[str, int]

# Models
class Annotations(BaseModel):
    """Optional annotations for the client. The client can use annotations to inform how objects are used or displayed"""
    audience: Optional[List[Role]] = Field(None, description="Describes who the intended customer of this object or data is.\n\nIt can include multiple entries to indicate content useful for multiple audiences (e.g., `[\"user\", \"assistant\"]`).")
    priority: Optional[float] = Field(None, description="Describes how important this data is for operating the server.\n\nA value of 1 means \"most important,\" and indicates that the data is\neffectively required, while 0 means \"least important,\" and indicates that\nthe data is entirely optional.", ge=0, le=1)

class TextContent(BaseModel):
    """Text provided to or from an LLM."""
    type: Literal["text"] = "text"
    text: str = Field(description="The text content of the message.")
    annotations: Optional[Annotations] = Field(None, description="Optional annotations for the client.")

class ImageContent(BaseModel):
    """An image provided to or from an LLM."""
    type: Literal["image"] = "image"
    data: str = Field(description="The base64-encoded image data.")
    mimeType: str = Field(description="The MIME type of the image. Different providers may support different image types.")
    annotations: Optional[Annotations] = Field(None, description="Optional annotations for the client.")

class AudioContent(BaseModel):
    """Audio provided to or from an LLM."""
    type: Literal["audio"] = "audio"
    data: str = Field(description="The base64-encoded audio data.")
    mimeType: str = Field(description="The MIME type of the audio. Different providers may support different audio types.")
    annotations: Optional[Annotations] = Field(None, description="Optional annotations for the client.")

class TextResourceContents(BaseModel):
    uri: str = Field(description="The URI of this resource.")
    text: str = Field(description="The text of the item. This must only be set if the item can actually be represented as text (not binary data).")
    mimeType: Optional[str] = Field(None, description="The MIME type of this resource, if known.")

class BlobResourceContents(BaseModel):
    uri: str = Field(description="The URI of this resource.")
    blob: str = Field(description="A base64-encoded string representing the binary data of the item.")
    mimeType: Optional[str] = Field(None, description="The MIME type of this resource, if known.")

class EmbeddedResource(BaseModel):
    """The contents of a resource, embedded into a prompt or tool call result.

    It is up to the client how best to render embedded resources for the benefit
    of the LLM and/or the user."""
    type: Literal["resource"] = "resource"
    resource: Union[TextResourceContents, BlobResourceContents]
    annotations: Optional[Annotations] = Field(None, description="Optional annotations for the client.")

class SamplingMessage(BaseModel):
    """Describes a message issued to or received from an LLM API."""
    role: Role
    content: Union[TextContent, ImageContent, AudioContent]

class PromptMessage(BaseModel):
    """Describes a message returned as part of a prompt.

    This is similar to `SamplingMessage`, but also supports the embedding of
    resources from the MCP server."""
    role: Role
    content: Union[TextContent, ImageContent, AudioContent, EmbeddedResource]

class Implementation(BaseModel):
    """Describes the name and version of an MCP implementation."""
    name: str
    version: str

# Capabilities models
class RootsCapabilities(BaseModel):
    listChanged: Optional[bool] = Field(None, description="Whether the client supports notifications for changes to the roots list.")

class SamplingCapabilities(BaseModel):
    pass  # No additional properties defined in the schema

class ClientCapabilities(BaseModel):
    """Capabilities a client may support. Known capabilities are defined here, in this schema, but this is not a closed set: any client can define its own, additional capabilities."""
    roots: Optional[RootsCapabilities] = Field(None, description="Present if the client supports listing roots.")
    sampling: Optional[SamplingCapabilities] = Field(None, description="Present if the client supports sampling from an LLM.")
    experimental: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Experimental, non-standard capabilities that the client supports.")

class PromptsCapabilities(BaseModel):
    listChanged: Optional[bool] = Field(None, description="Whether this server supports notifications for changes to the prompt list.")

class ResourcesCapabilities(BaseModel):
    listChanged: Optional[bool] = Field(None, description="Whether this server supports notifications for changes to the resource list.")
    subscribe: Optional[bool] = Field(None, description="Whether this server supports subscribing to resource updates.")

class ToolsCapabilities(BaseModel):
    listChanged: Optional[bool] = Field(None, description="Whether this server supports notifications for changes to the tool list.")

class LoggingCapabilities(BaseModel):
    pass  # No additional properties defined in the schema

class CompletionsCapabilities(BaseModel):
    pass  # No additional properties defined in the schema

class ServerCapabilities(BaseModel):
    """Capabilities that a server may support. Known capabilities are defined here, in this schema, but this is not a closed set: any server can define its own, additional capabilities."""
    prompts: Optional[PromptsCapabilities] = Field(None, description="Present if the server offers any prompt templates.")
    resources: Optional[ResourcesCapabilities] = Field(None, description="Present if the server offers any resources to read.")
    tools: Optional[ToolsCapabilities] = Field(None, description="Present if the server offers any tools to call.")
    logging: Optional[LoggingCapabilities] = Field(None, description="Present if the server supports sending log messages to the client.")
    completions: Optional[CompletionsCapabilities] = Field(None, description="Present if the server supports argument autocompletion suggestions.")
    experimental: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Experimental, non-standard capabilities that the server supports.")

# Resource models
class Resource(BaseModel):
    """A known resource that the server is capable of reading."""
    name: str = Field(description="A human-readable name for this resource.\n\nThis can be used by clients to populate UI elements.")
    uri: str = Field(description="The URI of this resource.")
    description: Optional[str] = Field(None, description="A description of what this resource represents.\n\nThis can be used by clients to improve the LLM's understanding of available resources. It can be thought of like a \"hint\" to the model.")
    mimeType: Optional[str] = Field(None, description="The MIME type of this resource, if known.")
    size: Optional[int] = Field(None, description="The size of the raw resource content, in bytes (i.e., before base64 encoding or any tokenization), if known.\n\nThis can be used by Hosts to display file sizes and estimate context window usage.")
    annotations: Optional[Annotations] = Field(None, description="Optional annotations for the client.")

class ResourceTemplate(BaseModel):
    """A template description for resources available on the server."""
    name: str = Field(description="A human-readable name for the type of resource this template refers to.\n\nThis can be used by clients to populate UI elements.")
    uriTemplate: str = Field(description="A URI template (according to RFC 6570) that can be used to construct resource URIs.")
    description: Optional[str] = Field(None, description="A description of what this template is for.\n\nThis can be used by clients to improve the LLM's understanding of available resources. It can be thought of like a \"hint\" to the model.")
    mimeType: Optional[str] = Field(None, description="The MIME type for all resources that match this template. This should only be included if all resources matching this template have the same type.")
    annotations: Optional[Annotations] = Field(None, description="Optional annotations for the client.")

class ResourceReference(BaseModel):
    """A reference to a resource or resource template definition."""
    type: Literal["ref/resource"] = "ref/resource"
    uri: str = Field(description="The URI or URI template of the resource.")

class Root(BaseModel):
    """Represents a root directory or file that the server can operate on."""
    uri: str = Field(description="The URI identifying the root. This *must* start with file:// for now.\nThis restriction may be relaxed in future versions of the protocol to allow\nother URI schemes.")
    name: Optional[str] = Field(None, description="An optional name for the root. This can be used to provide a human-readable\nidentifier for the root, which may be useful for display purposes or for\nreferencing the root in other parts of the application.")

# Prompt models
class PromptArgument(BaseModel):
    """Describes an argument that a prompt can accept."""
    name: str = Field(description="The name of the argument.")
    description: Optional[str] = Field(None, description="A human-readable description of the argument.")
    required: Optional[bool] = Field(None, description="Whether this argument must be provided.")

class Prompt(BaseModel):
    """A prompt or prompt template that the server offers."""
    name: str = Field(description="The name of the prompt or prompt template.")
    description: Optional[str] = Field(None, description="An optional description of what this prompt provides")
    arguments: Optional[List[PromptArgument]] = Field(None, description="A list of arguments to use for templating the prompt.")

class PromptReference(BaseModel):
    """Identifies a prompt."""
    type: Literal["ref/prompt"] = "ref/prompt"
    name: str = Field(description="The name of the prompt or prompt template")

# Tool models
class ToolAnnotations(BaseModel):
    """Additional properties describing a Tool to clients.

    NOTE: all properties in ToolAnnotations are **hints**.
    They are not guaranteed to provide a faithful description of
    tool behavior (including descriptive properties like `title`).

    Clients should never make tool use decisions based on ToolAnnotations
    received from untrusted servers."""
    title: Optional[str] = Field(None, description="A human-readable title for the tool.")
    readOnlyHint: Optional[bool] = Field(None, description="If true, the tool does not modify its environment.\n\nDefault: false")
    destructiveHint: Optional[bool] = Field(None, description="If true, the tool may perform destructive updates to its environment.\nIf false, the tool performs only additive updates.\n\n(This property is meaningful only when `readOnlyHint == false`)\n\nDefault: true")
    idempotentHint: Optional[bool] = Field(None, description="If true, calling the tool repeatedly with the same arguments\nwill have no additional effect on the its environment.\n\n(This property is meaningful only when `readOnlyHint == false`)\n\nDefault: false")
    openWorldHint: Optional[bool] = Field(None, description="If true, this tool may interact with an \"open world\" of external\nentities. If false, the tool's domain of interaction is closed.\nFor example, the world of a web search tool is open, whereas that\nof a memory tool is not.\n\nDefault: true")

class Tool(BaseModel):
    """Definition for a tool the client can call."""
    name: str = Field(description="The name of the tool.")
    inputSchema: Dict[str, Any] = Field(description="A JSON Schema object defining the expected parameters for the tool.")
    description: Optional[str] = Field(None, description="A human-readable description of the tool.\n\nThis can be used by clients to improve the LLM's understanding of available tools. It can be thought of like a \"hint\" to the model.")
    annotations: Optional[ToolAnnotations] = Field(None, description="Optional additional tool information.")

# Model preferences models
class ModelHint(BaseModel):
    """Hints to use for model selection.

    Keys not declared here are currently left unspecified by the spec and are up
    to the client to interpret."""
    name: Optional[str] = Field(None, description="A hint for a model name.\n\nThe client SHOULD treat this as a substring of a model name; for example:\n - `claude-3-5-sonnet` should match `claude-3-5-sonnet-20241022`\n - `sonnet` should match `claude-3-5-sonnet-20241022`, `claude-3-sonnet-20240229`, etc.\n - `claude` should match any Claude model\n\nThe client MAY also map the string to a different provider's model name or a different model family, as long as it fills a similar niche; for example:\n - `gemini-1.5-flash` could match `claude-3-haiku-20240307`")

class ModelPreferences(BaseModel):
    """The server's preferences for model selection, requested of the client during sampling.

    Because LLMs can vary along multiple dimensions, choosing the \"best\" model is
    rarely straightforward.  Different models excel in different areas—some are
    faster but less capable, others are more capable but more expensive, and so
    on. This interface allows servers to express their priorities across multiple
    dimensions to help clients make an appropriate selection for their use case.

    These preferences are always advisory. The client MAY ignore them. It is also
    up to the client to decide how to interpret these preferences and how to
    balance them against other considerations."""
    speedPriority: Optional[float] = Field(None, description="How much to prioritize sampling speed (latency) when selecting a model. A\nvalue of 0 means speed is not important, while a value of 1 means speed is\nthe most important factor.", ge=0, le=1)
    costPriority: Optional[float] = Field(None, description="How much to prioritize cost when selecting a model. A value of 0 means cost\nis not important, while a value of 1 means cost is the most important\nfactor.", ge=0, le=1)
    intelligencePriority: Optional[float] = Field(None, description="How much to prioritize intelligence and capabilities when selecting a\nmodel. A value of 0 means intelligence is not important, while a value of 1\nmeans intelligence is the most important factor.", ge=0, le=1)
    hints: Optional[List[ModelHint]] = Field(None, description="Optional hints to use for model selection.\n\nIf multiple hints are specified, the client MUST evaluate them in order\n(such that the first match is taken).\n\nThe client SHOULD prioritize these hints over the numeric priorities, but\nMAY still use the priorities to select from ambiguous matches.")

# Request and result models
class Result(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class EmptyResult(Result):
    pass

class InitializeRequestParams(BaseModel):
    clientInfo: Implementation
    protocolVersion: str = Field(description="The latest version of the Model Context Protocol that the client supports. The client MAY decide to support older versions as well.")
    capabilities: ClientCapabilities

class InitializeRequest(BaseModel):
    """This request is sent from the client to the server when it first connects, asking it to begin initialization."""
    method: Literal["initialize"] = "initialize"
    params: InitializeRequestParams

class InitializeResult(Result):
    """After receiving an initialize request from the client, the server sends this response."""
    serverInfo: Implementation
    protocolVersion: str = Field(description="The version of the Model Context Protocol that the server wants to use. This may not match the version that the client requested. If the client cannot support this version, it MUST disconnect.")
    capabilities: ServerCapabilities
    instructions: Optional[str] = Field(None, description="Instructions describing how to use the server and its features.\n\nThis can be used by clients to improve the LLM's understanding of available tools, resources, etc. It can be thought of like a \"hint\" to the model. For example, this information MAY be added to the system prompt.")

class InitializedNotificationParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class InitializedNotification(BaseModel):
    """This notification is sent from the client to the server after initialization has finished."""
    method: Literal["notifications/initialized"] = "notifications/initialized"
    params: Optional[InitializedNotificationParams] = None

class PingRequestParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class PingRequest(BaseModel):
    """A ping, issued by either the server or the client, to check that the other party is still alive. The receiver must promptly respond, or else may be disconnected."""
    method: Literal["ping"] = "ping"
    params: Optional[PingRequestParams] = None

class CancelledNotificationParams(BaseModel):
    requestId: RequestId = Field(description="The ID of the request to cancel.\n\nThis MUST correspond to the ID of a request previously issued in the same direction.")
    reason: Optional[str] = Field(None, description="An optional string describing the reason for the cancellation. This MAY be logged or presented to the user.")

class CancelledNotification(BaseModel):
    """This notification can be sent by either side to indicate that it is cancelling a previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request."""
    method: Literal["notifications/cancelled"] = "notifications/cancelled"
    params: CancelledNotificationParams

class ProgressNotificationParams(BaseModel):
    progressToken: ProgressToken = Field(description="The progress token which was given in the initial request, used to associate this notification with the request that is proceeding.")
    progress: float = Field(description="The progress thus far. This should increase every time progress is made, even if the total is unknown.")
    total: Optional[float] = Field(None, description="Total number of items to process (or total progress required), if known.")
    message: Optional[str] = Field(None, description="An optional message describing the current progress.")

class ProgressNotification(BaseModel):
    """An out-of-band notification used to inform the receiver of a progress update for a long-running request."""
    method: Literal["notifications/progress"] = "notifications/progress"
    params: ProgressNotificationParams

class ListRootsRequestParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class ListRootsRequest(BaseModel):
    """Sent from the server to request a list of root URIs from the client. Roots allow
    servers to ask for specific directories or files to operate on. A common example
    for roots is providing a set of repositories or directories a server should operate
    on.

    This request is typically used when the server needs to understand the file system
    structure or access specific locations that the client has permission to read from."""
    method: Literal["roots/list"] = "roots/list"
    params: Optional[ListRootsRequestParams] = None

class ListRootsResult(Result):
    """The client's response to a roots/list request from the server.
    This result contains an array of Root objects, each representing a root directory
    or file that the server can operate on."""
    roots: List[Root]

class RootsListChangedNotificationParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class RootsListChangedNotification(BaseModel):
    """A notification from the client to the server, informing it that the list of roots has changed.
    This notification should be sent whenever the client adds, removes, or modifies any root.
    The server should then request an updated list of roots using the ListRootsRequest."""
    method: Literal["notifications/roots/list_changed"] = "notifications/roots/list_changed"
    params: Optional[RootsListChangedNotificationParams] = None

class ListResourcesRequestParams(BaseModel):
    cursor: Optional[str] = Field(None, description="An opaque token representing the current pagination position.\nIf provided, the server should return results starting after this cursor.")

class ListResourcesRequest(BaseModel):
    """Sent from the client to request a list of resources the server has."""
    method: Literal["resources/list"] = "resources/list"
    params: Optional[ListResourcesRequestParams] = None

class ListResourcesResult(Result):
    """The server's response to a resources/list request from the client."""
    resources: List[Resource]
    nextCursor: Optional[str] = Field(None, description="An opaque token representing the pagination position after the last returned result.\nIf present, there may be more results available.")

class ResourceListChangedNotificationParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class ResourceListChangedNotification(BaseModel):
    """An optional notification from the server to the client, informing it that the list of resources it can read from has changed. This may be issued by servers without any previous subscription from the client."""
    method: Literal["notifications/resources/list_changed"] = "notifications/resources/list_changed"
    params: Optional[ResourceListChangedNotificationParams] = None

class ListResourceTemplatesRequestParams(BaseModel):
    cursor: Optional[str] = Field(None, description="An opaque token representing the current pagination position.\nIf provided, the server should return results starting after this cursor.")

class ListResourceTemplatesRequest(BaseModel):
    """Sent from the client to request a list of resource templates the server has."""
    method: Literal["resources/templates/list"] = "resources/templates/list"
    params: Optional[ListResourceTemplatesRequestParams] = None

class ListResourceTemplatesResult(Result):
    """The server's response to a resources/templates/list request from the client."""
    resourceTemplates: List[ResourceTemplate]
    nextCursor: Optional[str] = Field(None, description="An opaque token representing the pagination position after the last returned result.\nIf present, there may be more results available.")

class ReadResourceRequestParams(BaseModel):
    uri: str = Field(description="The URI of the resource to read. The URI can use any protocol; it is up to the server how to interpret it.")

class ReadResourceRequest(BaseModel):
    """Sent from the client to the server, to read a specific resource URI."""
    method: Literal["resources/read"] = "resources/read"
    params: ReadResourceRequestParams

class ReadResourceResult(Result):
    """The server's response to a resources/read request from the client."""
    contents: List[Union[TextResourceContents, BlobResourceContents]]

class SubscribeRequestParams(BaseModel):
    uri: str = Field(description="The URI of the resource to subscribe to. The URI can use any protocol; it is up to the server how to interpret it.")

class SubscribeRequest(BaseModel):
    """Sent from the client to request resources/updated notifications from the server whenever a particular resource changes."""
    method: Literal["resources/subscribe"] = "resources/subscribe"
    params: SubscribeRequestParams

class UnsubscribeRequestParams(BaseModel):
    uri: str = Field(description="The URI of the resource to unsubscribe from.")

class UnsubscribeRequest(BaseModel):
    """Sent from the client to request cancellation of resources/updated notifications from the server. This should follow a previous resources/subscribe request."""
    method: Literal["resources/unsubscribe"] = "resources/unsubscribe"
    params: UnsubscribeRequestParams

class ResourceUpdatedNotificationParams(BaseModel):
    uri: str = Field(description="The URI of the resource that has been updated. This might be a sub-resource of the one that the client actually subscribed to.")

class ResourceUpdatedNotification(BaseModel):
    """A notification from the server to the client, informing it that a resource has changed and may need to be read again. This should only be sent if the client previously sent a resources/subscribe request."""
    method: Literal["notifications/resources/updated"] = "notifications/resources/updated"
    params: ResourceUpdatedNotificationParams

class ListPromptsRequestParams(BaseModel):
    cursor: Optional[str] = Field(None, description="An opaque token representing the current pagination position.\nIf provided, the server should return results starting after this cursor.")

class ListPromptsRequest(BaseModel):
    """Sent from the client to request a list of prompts and prompt templates the server has."""
    method: Literal["prompts/list"] = "prompts/list"
    params: Optional[ListPromptsRequestParams] = None

class ListPromptsResult(Result):
    """The server's response to a prompts/list request from the client."""
    prompts: List[Prompt]
    nextCursor: Optional[str] = Field(None, description="An opaque token representing the pagination position after the last returned result.\nIf present, there may be more results available.")

class PromptListChangedNotificationParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class PromptListChangedNotification(BaseModel):
    """An optional notification from the server to the client, informing it that the list of prompts it offers has changed. This may be issued by servers without any previous subscription from the client."""
    method: Literal["notifications/prompts/list_changed"] = "notifications/prompts/list_changed"
    params: Optional[PromptListChangedNotificationParams] = None

class GetPromptRequestParams(BaseModel):
    name: str = Field(description="The name of the prompt or prompt template.")
    arguments: Optional[Dict[str, str]] = Field(None, description="Arguments to use for templating the prompt.")

class GetPromptRequest(BaseModel):
    """Used by the client to get a prompt provided by the server."""
    method: Literal["prompts/get"] = "prompts/get"
    params: GetPromptRequestParams

class GetPromptResult(Result):
    """The server's response to a prompts/get request from the client."""
    messages: List[PromptMessage]
    description: Optional[str] = Field(None, description="An optional description for the prompt.")

class ListToolsRequestParams(BaseModel):
    cursor: Optional[str] = Field(None, description="An opaque token representing the current pagination position.\nIf provided, the server should return results starting after this cursor.")

class ListToolsRequest(BaseModel):
    """Sent from the client to request a list of tools the server has."""
    method: Literal["tools/list"] = "tools/list"
    params: Optional[ListToolsRequestParams] = None

class ListToolsResult(Result):
    """The server's response to a tools/list request from the client."""
    tools: List[Tool]
    nextCursor: Optional[str] = Field(None, description="An opaque token representing the pagination position after the last returned result.\nIf present, there may be more results available.")

class ToolListChangedNotificationParams(BaseModel):
    _meta: Optional[Dict[str, Any]] = None

class ToolListChangedNotification(BaseModel):
    """An optional notification from the server to the client, informing it that the list of tools it offers has changed. This may be issued by servers without any previous subscription from the client."""
    method: Literal["notifications/tools/list_changed"] = "notifications/tools/list_changed"
    params: Optional[ToolListChangedNotificationParams] = None

class CallToolRequestParams(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = None

class CallToolRequest(BaseModel):
    """Used by the client to invoke a tool provided by the server."""
    method: Literal["tools/call"] = "tools/call"
    params: CallToolRequestParams

class CallToolResult(Result):
    """The server's response to a tool call.

    Any errors that originate from the tool SHOULD be reported inside the result
    object, with `isError` set to true, _not_ as an MCP protocol-level error
    response. Otherwise, the LLM would not be able to see that an error occurred
    and self-correct.

    However, any errors in _finding_ the tool, an error indicating that the
    server does not support tool calls, or any other exceptional conditions,
    should be reported as an MCP error response."""
    content: List[Union[TextContent, ImageContent, AudioContent, EmbeddedResource]]
    isError: Optional[bool] = Field(None, description="Whether the tool call ended in an error.\n\nIf not set, this is assumed to be false (the call was successful).")

class SetLevelRequestParams(BaseModel):
    level: LoggingLevel = Field(description="The level of logging that the client wants to receive from the server. The server should send all logs at this level and higher (i.e., more severe) to the client as notifications/message.")

class SetLevelRequest(BaseModel):
    """A request from the client to the server, to enable or adjust logging."""
    method: Literal["logging/setLevel"] = "logging/setLevel"
    params: SetLevelRequestParams

class LoggingMessageNotificationParams(BaseModel):
    level: LoggingLevel = Field(description="The severity of this log message.")
    data: Any = Field(description="The data to be logged, such as a string message or an object. Any JSON serializable type is allowed here.")
    logger: Optional[str] = Field(None, description="An optional name of the logger issuing this message.")

class LoggingMessageNotification(BaseModel):
    """Notification of a log message passed from server to client. If no logging/setLevel request has been sent from the client, the server MAY decide which messages to send automatically."""
    method: Literal["notifications/message"] = "notifications/message"
    params: LoggingMessageNotificationParams

class CreateMessageRequestParams(BaseModel):
    messages: List[SamplingMessage]
    maxTokens: int = Field(description="The maximum number of tokens to sample, as requested by the server. The client MAY choose to sample fewer tokens than requested.")
    systemPrompt: Optional[str] = Field(None, description="An optional system prompt the server wants to use for sampling. The client MAY modify or omit this prompt.")
    temperature: Optional[float] = None
    stopSequences: Optional[List[str]] = None
    modelPreferences: Optional[ModelPreferences] = Field(None, description="The server's preferences for which model to select. The client MAY ignore these preferences.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata to pass through to the LLM provider. The format of this metadata is provider-specific.")
    includeContext: Optional[Literal["allServers", "none", "thisServer"]] = Field(None, description="A request to include context from one or more MCP servers (including the caller), to be attached to the prompt. The client MAY ignore this request.")

class CreateMessageRequest(BaseModel):
    """A request from the server to sample an LLM via the client. The client has full discretion over which model to select. The client should also inform the user before beginning sampling, to allow them to inspect the request (human in the loop) and decide whether to approve it."""
    method: Literal["sampling/createMessage"] = "sampling/createMessage"
    params: CreateMessageRequestParams

class CreateMessageResult(Result):
    """The client's response to a sampling/create_message request from the server. The client should inform the user before returning the sampled message, to allow them to inspect the response (human in the loop) and decide whether to allow the server to see it."""
    role: Role
    model: str = Field(description="The name of the model that generated the message.")
    content: Union[TextContent, ImageContent, AudioContent]
    stopReason: Optional[str] = Field(None, description="The reason why sampling stopped, if known.")

class CompleteRequestArgumentParams(BaseModel):
    name: str = Field(description="The name of the argument")
    value: str = Field(description="The value of the argument to use for completion matching.")

class CompleteRequestParams(BaseModel):
    ref: Union[PromptReference, ResourceReference]
    argument: CompleteRequestArgumentParams = Field(description="The argument's information")

class CompleteRequest(BaseModel):
    """A request from the client to the server, to ask for completion options."""
    method: Literal["completion/complete"] = "completion/complete"
    params: CompleteRequestParams

class CompletionValues(BaseModel):
    values: List[str] = Field(description="An array of completion values. Must not exceed 100 items.")
    total: Optional[int] = Field(None, description="The total number of completion options available. This can exceed the number of values actually sent in the response.")
    hasMore: Optional[bool] = Field(None, description="Indicates whether there are additional completion options beyond those provided in the current response, even if the exact total is unknown.")

class CompleteResult(Result):
    """The server's response to a completion/complete request"""
    completion: CompletionValues

# JSON-RPC message models
class JSONRPCNotification(BaseModel):
    """A notification which does not expect a response."""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None

class JSONRPCRequest(BaseModel):
    """A request that expects a response."""
    jsonrpc: Literal["2.0"] = "2.0"
    id: RequestId
    method: str
    params: Optional[Dict[str, Any]] = None

class JSONRPCResponse(BaseModel):
    """A successful (non-error) response to a request."""
    jsonrpc: Literal["2.0"] = "2.0"
    id: RequestId
    result: Result

class JSONRPCError(BaseModel):
    """A response to a request that indicates an error occurred."""
    jsonrpc: Literal["2.0"] = "2.0"
    id: RequestId
    error: Dict[str, Any]

JSONRPCBatchRequest: TypeAlias = List[Union[JSONRPCRequest, JSONRPCNotification]]
JSONRPCBatchResponse: TypeAlias = List[Union[JSONRPCResponse, JSONRPCError]]
JSONRPCMessage: TypeAlias = Union[JSONRPCRequest, JSONRPCNotification, List[Union[JSONRPCRequest, JSONRPCNotification]], JSONRPCResponse, JSONRPCError, List[Union[JSONRPCResponse, JSONRPCError]]]

# Union types for notifications and requests
ClientNotification: TypeAlias = Union[CancelledNotification, InitializedNotification, ProgressNotification, RootsListChangedNotification]
ClientRequest: TypeAlias = Union[InitializeRequest, PingRequest, ListResourcesRequest, ListResourceTemplatesRequest, ReadResourceRequest, SubscribeRequest, UnsubscribeRequest, ListPromptsRequest, GetPromptRequest, ListToolsRequest, CallToolRequest, SetLevelRequest, CompleteRequest]
ClientResult: TypeAlias = Union[Result, CreateMessageResult, ListRootsResult]
ServerNotification: TypeAlias = Union[CancelledNotification, ProgressNotification, ResourceListChangedNotification, ResourceUpdatedNotification, PromptListChangedNotification, ToolListChangedNotification, LoggingMessageNotification]
ServerRequest: TypeAlias = Union[PingRequest, CreateMessageRequest, ListRootsRequest]
ServerResult: TypeAlias = Union[Result, InitializeResult, ListResourcesResult, ListResourceTemplatesResult, ReadResourceResult, ListPromptsResult, GetPromptResult, ListToolsResult, CallToolResult, CompleteResult]
