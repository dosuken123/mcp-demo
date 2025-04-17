# Example: Remote Model Context Protocol (MCP) Server without SDKs

This repository demonstrates the minimal example of MCP client and **remote** server implementations.
It follows [Model Context Protocol spec](https://modelcontextprotocol.io/introduction)
**without** relying on official or 3rd party MCP SDKs, so that you can examine the low-level details of
MCP flow, including authentication and authorization via OAuth2.1.
This is mainly for enterprise software/server that can't use MCP SDKs as-is due to the existing server stack and business logic.

This demo uses [HTTP/SSE transport](https://modelcontextprotocol.io/docs/concepts/transports#server-sent-events-sse) for the **remote** MCP Server implementation.
This demo does **NOT** use the [stdio transport](https://modelcontextprotocol.io/docs/concepts/transports#standard-input%2Foutput-stdio) which is designed for the "local" MCP server.
There are several reasons why it's preferred to go after a remote MCP Server rather than a local MCP Server, for example:

- Backward compatibility: You have to hard-code the API caller to your data server in the local MCP server. When you change the API spec of your data server, the local MCP Server could stop working because the API requests are incompatible. Unifying the MCP server and your data server minimizes this risk.
- Extensibility & Maintanability: When the local MCP Server needs a specific context data from your data server, you have to implement a corresponding public API at first. Unifying the MCP server and your data server reduces this friction.
- Classification: Local MCP Server requires the API of your data server to be public. For the highly classified servers, it could be a deal breaker.
- Telemetry: Track which MCP Client consumes which API/data of your data server. You might not be able to track this if you let local MCP Server directly access to the public API of your data server, because servers can't differentiate the requester type (e.g. Is it an automation in CI or MCP tool calling?).

While this demo is written in Python as backend server and Vue.js as frontend server,
the implemented logic can be translated/adopted into the other programming language
where the SDKs might not support yet.

## Overview

This demo is based on the latest MCP spec described in https://modelcontextprotocol.io/specification/2025-03-26.

- It supports OAuth2.1 flow according to https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization#2-2-example%3A-authorization-code-grant. This auth flow supports PKCE (generating code challenge with SHA256) as it's required in OAuth 2.1.
- The frontend component represents **MCP Host** and **MCP Client** in the [MCP glossaries](https://modelcontextprotocol.io/introduction). In [OAuth terms](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/), it represents **Client**.
- The backend component represents **MCP Server** and **Local Data Source** in the [MCP glossaries](https://modelcontextprotocol.io/introduction). In [OAuth terms](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/), it represents **Resource server** and **Authorization server**. And the dummy user in the in-memory database is called **Resource owner**.

Here is the auth flow:

1. A user visits the web site. If authorization is not done yet, it's redirected to the authorization server (`GET /authorize` endpoint).
1. The user logins to the authorization server (`POST /login` endpoint). If it's successful, it's redirected to the callback URL in the frontend (`http://localhost:5173/callback`).
1. Frontend requests to `POST /token` endpoint to generate an access token (JWT).
1. Frontend requests to a protected resource endpoint (e.g. `GET /users/me/`)

## How to run

- Frontend: See [this doc](./frontend/README.md).
- Backend: See [this doc](./backend/README.md).
