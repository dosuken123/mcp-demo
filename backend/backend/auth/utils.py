from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Annotated, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
import jwt
from jwt.exceptions import InvalidTokenError
import secrets
import hashlib
import base64
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# OAuth client settings
# In a real application, this would be stored in a database
OAUTH_CLIENTS = {
    "my-mcp-client": {
        "client_id": "my-mcp-client",
        "client_name": "My MCP Client",
        "redirect_uris": [
            "http://localhost:5173/callback",  # Webview HTTP Server (Vite on browser)
            "http://127.0.0.1:41648/callback",  # Webview HTTP Server (Fastify in language server)
        ],
        "allowed_scopes": ["read", "write"],
    }
}


# Store for authorization codes and PKCE challenges
# In a real app, this would be in a database with TTL
auth_code_store = (
    {}
)  # format: {"code": {"client_id": "...", "user": "...", "code_challenge": "...", "redirect_uri": "...", "scope": "...", "expires_at": datetime}}

# Store for refresh tokens
# In a real app, this would be in a database
refresh_token_store = (
    {}
)  # format: {"token": {"user_id": "...", "client_id": "...", "scope": "..."}}


db_in_memory = {
    "users": [
        {
            "id": 1,
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        }
    ],
    "blog_posts": [
        {
            "id": 1,
            "user_id": 1,  # FK to users
            "content": "Yesterday was a good day",
        }
    ],
}

# Change tokenUrl to point to OAuth token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class TokenData(BaseModel):
    username: str | None = None
    scopes: List[str] = []


class OAuth2Error(BaseModel):
    error: str
    error_description: Optional[str] = None


def get_user(username: str):
    for user_dict in db_in_memory["users"]:
        if user_dict["username"] == username:
            return UserInDB(**user_dict)
    return None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    if os.environ.get("BYPASS_AUTH"):
        return get_user(username="johndoe")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def generate_auth_code():
    """Generate a secure random authorization code"""
    return secrets.token_urlsafe(32)


def generate_refresh_token():
    """Generate a secure random refresh token"""
    return secrets.token_urlsafe(48)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_code_challenge(
    code_verifier: str, code_challenge: str, method: str = "S256"
) -> bool:
    """Verify the PKCE code challenge against the code verifier"""
    if method == "S256":
        code_challenge_computed = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )
        return code_challenge == code_challenge_computed
    elif method == "plain":
        return code_verifier == code_challenge
    else:
        return False


def verify_client(client_id: str, redirect_uri: str):
    """Verify that the client ID and redirect URI are valid"""
    if client_id not in OAUTH_CLIENTS:
        return False

    client = OAUTH_CLIENTS[client_id]
    if redirect_uri not in client["redirect_uris"]:
        return False

    return True


def parse_scope(scope_string: str) -> List[str]:
    """Parse space-separated scope string into list"""
    if not scope_string:
        return []
    return scope_string.strip().split()
