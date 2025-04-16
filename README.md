# OAuth2.1 auth flow demo with FastAPI backend and Vue.js frontend

This repository demonstrates how OAuth2.1 auth flow works in a minimal code example.
It uses FastAPI python server as backend and Vue.js application as frontend.

The backend server behaves as authorization and resource server.

This auth flow supports PKCE (generating code challenge with SHA256) as it's required in OAuth 2.1.

Here is the overview of the auth flow:

1. A user visits the web site. If authorization is not done yet, it's redirected to the authorization server (`GET /authorize` endpoint).
1. The user logins to the authorization server (`POST /login` endpoint). If it's successful, it's redirected to the callback URL in the frontend (`http://localhost:5173/callback`).
1. Frontend requests to `POST /token` endpoint to generate an access token (JWT).
1. Frontend requests to a protected resource endpoint (e.g. `GET /users/me/`)

You can use it as a reference when introducing [a MCP server with the authorization protocol](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization#2-2-example%3A-authorization-code-grant).

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
