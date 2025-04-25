from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from typing import Annotated, Optional, List, Dict, Any
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates

from backend.auth.utils import (
    verify_client,
    OAUTH_CLIENTS,
    authenticate_user,
    fake_users_db,
    generate_auth_code,
    auth_code_store,
    Token,
    OAuth2Error,
    verify_code_challenge,
    get_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    parse_scope,
    create_access_token,
    generate_refresh_token,
    refresh_token_store,
)

router = APIRouter()

# Create templates directory for login page
templates = Jinja2Templates(directory="backend/templates")


@router.get("/oauth/authorize", response_class=HTMLResponse)
async def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: Optional[str] = None,
    scope: Optional[str] = "",
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = "S256",
):
    """OAuth 2.1 authorization endpoint"""
    # Validate request parameters
    if response_type != "code":
        return RedirectResponse(
            f"{redirect_uri}?error=unsupported_response_type&state={state}",
            status_code=302,
        )

    if not verify_client(client_id, redirect_uri):
        return HTMLResponse(
            content="Invalid client ID or redirect URI", status_code=400
        )

    if not code_challenge and code_challenge_method != "none":
        return RedirectResponse(
            f"{redirect_uri}?error=invalid_request&error_description=code_challenge_required&state={state}",
            status_code=302,
        )

    # Get client name for display
    client_name = OAUTH_CLIENTS[client_id]["client_name"]

    return templates.TemplateResponse(
        request=request,
        name="login.html.jinja",
        context={
            "client_id": client_id,
            "client_name": client_name,
            "redirect_uri": redirect_uri,
            "response_type": response_type,
            "state": state or "",
            "scope": scope,
            "code_challenge": code_challenge or "",
            "code_challenge_method": code_challenge_method,
            "error": None,
        },
    )


@router.post("/oauth/login", response_class=RedirectResponse)
async def login(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    response_type: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    state: Optional[str] = Form(None),
    scope: Optional[str] = Form(""),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form("S256"),
):
    """Handle login form submission and create authorization code"""
    # Authenticate user
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        # Re-render login form with error
        client_name = OAUTH_CLIENTS[client_id]["client_name"]

        return templates.TemplateResponse(
            request=request,
            name="login.html.jinja",
            context={
                "client_id": client_id,
                "client_name": client_name,
                "redirect_uri": redirect_uri,
                "response_type": response_type,
                "state": state or "",
                "scope": scope,
                "code_challenge": code_challenge or "",
                "code_challenge_method": code_challenge_method,
                "error": "Invalid username or password",
            },
        )

    # Generate authorization code
    auth_code = generate_auth_code()

    # Store authorization code with associated data
    auth_code_store[auth_code] = {
        "client_id": client_id,
        "user": user.username,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "expires_at": datetime.now(timezone.utc)
        + timedelta(minutes=10),  # Code expires in 10 minutes
    }

    # Redirect back to client with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(redirect_url, status_code=302)


@router.post("/oauth/token", response_model=Token)
async def token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
):
    """OAuth 2.1 token endpoint supporting authorization_code and refresh_token grant types"""
    if grant_type == "authorization_code":
        # Validate authorization code grant
        if not code or not redirect_uri or not code_verifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_request",
                    error_description="Missing required parameters for authorization_code grant",
                ).dict(),
            )

        # Check if code exists and is valid
        if code not in auth_code_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="Invalid authorization code",
                ).dict(),
            )

        # Get stored data for the code
        code_data = auth_code_store[code]

        # Check if code has expired
        if datetime.now(timezone.utc) > code_data["expires_at"]:
            # Remove expired code
            del auth_code_store[code]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="Authorization code expired",
                ).dict(),
            )

        # Validate client_id and redirect_uri
        if (
            code_data["client_id"] != client_id
            or code_data["redirect_uri"] != redirect_uri
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="client_id or redirect_uri does not match authorization request",
                ).dict(),
            )

        # Verify PKCE code challenge
        if code_data["code_challenge"]:
            if not verify_code_challenge(
                code_verifier,
                code_data["code_challenge"],
                code_data["code_challenge_method"],
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=OAuth2Error(
                        error="invalid_grant",
                        error_description="Code verifier does not match code challenge",
                    ).dict(),
                )

        # Get user information
        username = code_data["user"]
        user = get_user(fake_users_db, username)

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        scopes = parse_scope(code_data["scope"])

        access_token = create_access_token(
            data={"sub": user.username, "scopes": scopes},
            expires_delta=access_token_expires,
        )

        # Generate refresh token
        refresh_token_value = generate_refresh_token()

        # Store refresh token
        refresh_token_store[refresh_token_value] = {
            "user_id": user.username,
            "client_id": client_id,
            "scope": code_data["scope"],
        }

        # Remove used authorization code
        del auth_code_store[code]

        # Return tokens
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": refresh_token_value,
            "scope": code_data["scope"],
        }

    elif grant_type == "refresh_token":
        # Validate refresh token grant
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_request",
                    error_description="Missing refresh_token parameter",
                ).dict(),
            )

        # Check if refresh token exists
        if refresh_token not in refresh_token_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant", error_description="Invalid refresh token"
                ).dict(),
            )

        # Get stored data for the refresh token
        token_data = refresh_token_store[refresh_token]

        # Validate client_id
        if token_data["client_id"] != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="Refresh token was not issued to this client",
                ).dict(),
            )

        # Get user information
        username = token_data["user_id"]
        user = get_user(fake_users_db, username)

        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        scopes = parse_scope(token_data["scope"])

        access_token = create_access_token(
            data={"sub": user.username, "scopes": scopes},
            expires_delta=access_token_expires,
        )

        # Optionally rotate refresh token (best practice for security)
        new_refresh_token = generate_refresh_token()
        refresh_token_store[new_refresh_token] = token_data

        # Remove old refresh token
        del refresh_token_store[refresh_token]

        # Return tokens
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": new_refresh_token,
            "scope": token_data["scope"],
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=OAuth2Error(
                error="unsupported_grant_type",
                error_description=f"Unsupported grant type: {grant_type}",
            ).dict(),
        )
