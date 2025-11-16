from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..core.security import decode_access_token

security = HTTPBearer()

async def get_current_user(request: Request):
    """Middleware to get current user from JWT token."""
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")
