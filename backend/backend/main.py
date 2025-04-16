from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, List, Dict, Any
import secrets
import hashlib
import base64

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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
        "redirect_uris": ["http://localhost:5173/callback"],
        "allowed_scopes": ["read", "write"]
    }
}

# Store for authorization codes and PKCE challenges
# In a real app, this would be in a database with TTL
auth_code_store = {}  # format: {"code": {"client_id": "...", "user": "...", "code_challenge": "...", "redirect_uri": "...", "scope": "...", "expires_at": datetime}}

# Store for refresh tokens
# In a real app, this would be in a database
refresh_token_store = {}  # format: {"token": {"user_id": "...", "client_id": "...", "scope": "..."}}

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # "secret"
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class TokenData(BaseModel):
    username: str | None = None
    scopes: List[str] = []


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class OAuth2Error(BaseModel):
    error: str
    error_description: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Change tokenUrl to point to OAuth token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/token")

app = FastAPI()

# Create templates directory for login page
templates = Jinja2Templates(directory="templates")

# In a real app, you would have template files on disk
# For this example, we'll inject a simple login template directly
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MCP Server Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4285F4;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        .error {
            color: red;
            margin-bottom: 15px;
        }
        .scopes {
            margin-top: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h2>{{ client_name }} is requesting access to your account on MCP server.</h2>
    
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    
    <form method="post" action="/oauth/login">
        <input type="hidden" name="client_id" value="{{ client_id }}">
        <input type="hidden" name="redirect_uri" value="{{ redirect_uri }}">
        <input type="hidden" name="response_type" value="{{ response_type }}">
        <input type="hidden" name="state" value="{{ state }}">
        <input type="hidden" name="scope" value="{{ scope }}">
        <input type="hidden" name="code_challenge" value="{{ code_challenge }}">
        <input type="hidden" name="code_challenge_method" value="{{ code_challenge_method }}">
        
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" value="johndoe" required>
        </div>

        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" value="secret" required>
        </div>
        
        {% if scope %}
        <div class="scopes">
            <p><strong>{{ client_name }} is requesting the following permissions:</strong></p>
            <ul>
                {% for s in scope.split(' ') %}
                <li>{{ s }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <button type="submit">Login & Authorize</button>
    </form>
</body>
</html>
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
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


def verify_code_challenge(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
    """Verify the PKCE code challenge against the code verifier"""
    if method == "S256":
        code_challenge_computed = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_challenge == code_challenge_computed
    elif method == "plain":
        return code_verifier == code_challenge
    else:
        return False


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


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


@app.get("/oauth/authorize", response_class=HTMLResponse)
async def authorize(
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
            status_code=302
        )
    
    if not verify_client(client_id, redirect_uri):
        return HTMLResponse(
            content="Invalid client ID or redirect URI",
            status_code=400
        )
    
    if not code_challenge and code_challenge_method != "none":
        return RedirectResponse(
            f"{redirect_uri}?error=invalid_request&error_description=code_challenge_required&state={state}",
            status_code=302
        )
    
    # Get client name for display
    client_name = OAUTH_CLIENTS[client_id]["client_name"]
    
    # Render login template
    return HTMLResponse(content=templates.get_template_string(LOGIN_TEMPLATE).render(
        client_id=client_id,
        client_name=client_name,
        redirect_uri=redirect_uri,
        response_type=response_type,
        state=state or "",
        scope=scope,
        code_challenge=code_challenge or "",
        code_challenge_method=code_challenge_method,
        error=None
    ))


@app.post("/oauth/login", response_class=RedirectResponse)
async def login(
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
        return HTMLResponse(content=templates.get_template_string(LOGIN_TEMPLATE).render(
            client_id=client_id,
            client_name=client_name,
            redirect_uri=redirect_uri,
            response_type=response_type,
            state=state or "",
            scope=scope,
            code_challenge=code_challenge or "",
            code_challenge_method=code_challenge_method,
            error="Invalid username or password"
        ))
    
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
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)  # Code expires in 10 minutes
    }
    
    # Redirect back to client with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"
    
    return RedirectResponse(redirect_url, status_code=302)


@app.post("/oauth/token", response_model=Token)
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
                    error_description="Missing required parameters for authorization_code grant"
                ).dict()
            )
        
        # Check if code exists and is valid
        if code not in auth_code_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="Invalid authorization code"
                ).dict()
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
                    error_description="Authorization code expired"
                ).dict()
            )
        
        # Validate client_id and redirect_uri
        if (code_data["client_id"] != client_id or
            code_data["redirect_uri"] != redirect_uri):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="client_id or redirect_uri does not match authorization request"
                ).dict()
            )
        
        # Verify PKCE code challenge
        if code_data["code_challenge"]:
            if not verify_code_challenge(
                code_verifier, 
                code_data["code_challenge"],
                code_data["code_challenge_method"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=OAuth2Error(
                        error="invalid_grant",
                        error_description="Code verifier does not match code challenge"
                    ).dict()
                )
        
        # Get user information
        username = code_data["user"]
        user = get_user(fake_users_db, username)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        scopes = parse_scope(code_data["scope"])
        
        access_token = create_access_token(
            data={
                "sub": user.username,
                "scopes": scopes
            },
            expires_delta=access_token_expires
        )
        
        # Generate refresh token
        refresh_token_value = generate_refresh_token()
        
        # Store refresh token
        refresh_token_store[refresh_token_value] = {
            "user_id": user.username,
            "client_id": client_id,
            "scope": code_data["scope"]
        }
        
        # Remove used authorization code
        del auth_code_store[code]
        
        # Return tokens
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": refresh_token_value,
            "scope": code_data["scope"]
        }
        
    elif grant_type == "refresh_token":
        # Validate refresh token grant
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_request",
                    error_description="Missing refresh_token parameter"
                ).dict()
            )
        
        # Check if refresh token exists
        if refresh_token not in refresh_token_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="Invalid refresh token"
                ).dict()
            )
        
        # Get stored data for the refresh token
        token_data = refresh_token_store[refresh_token]
        
        # Validate client_id
        if token_data["client_id"] != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OAuth2Error(
                    error="invalid_grant",
                    error_description="Refresh token was not issued to this client"
                ).dict()
            )
        
        # Get user information
        username = token_data["user_id"]
        user = get_user(fake_users_db, username)
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        scopes = parse_scope(token_data["scope"])
        
        access_token = create_access_token(
            data={
                "sub": user.username,
                "scopes": scopes
            },
            expires_delta=access_token_expires
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
            "scope": token_data["scope"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=OAuth2Error(
                error="unsupported_grant_type",
                error_description=f"Unsupported grant type: {grant_type}"
            ).dict()
        )


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


# Helper function for Jinja2Templates to get template strings when no actual file exists
def get_template_string(self, template_name):
    """Custom method to get template from string"""
    from jinja2 import Template
    if template_name == LOGIN_TEMPLATE:
        return Template(LOGIN_TEMPLATE)
    raise ValueError(f"Template not found: {template_name}")

# Add the custom method to the templates instance
templates.get_template_string = get_template_string.__get__(templates)

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
