# Minimal example of Model Context Protocol (MCP) client and server implementations

This repository demonstrates the minimal example of MCP client and server implementations.
It follows [Model Context Protocol spec](https://modelcontextprotocol.io/introduction)
**without** relying on official or 3rd party MCP SDKs, so that you can examine the low-level details of
MCP flow, including authentication and authorization via OAuth2.1.
This is mainly for enterprise software/server that can't use MCP SDKs as it-is due to the existing server stack and business logic.

While this demo is written in Python as backend server and Vue.js as frontend server,
the implemented logic can be translated/adopted into the other programming language
where the open-source libraries might not support yet.

## Details

- It supports how OAuth2.1 flow as it's described in https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization#2-2-example%3A-authorization-code-grant.
  - This auth flow supports PKCE (generating code challenge with SHA256) as it's required in OAuth 2.1.
  - The backend server behaves as authorization and resource server.

  - Here is the overview of the auth flow:
    1. A user visits the web site. If authorization is not done yet, it's redirected to the authorization server (`GET /authorize` endpoint).
    1. The user logins to the authorization server (`POST /login` endpoint). If it's successful, it's redirected to the callback URL in the frontend (`http://localhost:5173/callback`).
    1. Frontend requests to `POST /token` endpoint to generate an access token (JWT).
    1. Frontend requests to a protected resource endpoint (e.g. `GET /users/me/`)

## Changelog of MCP spec

This demo adheres the latest protocol spec listed below.

- https://modelcontextprotocol.io/specification/2025-03-26
- https://modelcontextprotocol.io/specification/2024-11-05

## How to run

Run frontend:

```
cd frontend
npm run dev
```

Run backend:

```
cd backend
poetry run fastapi dev backend/main.py --host localhost
```
