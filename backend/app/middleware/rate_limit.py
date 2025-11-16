from fastapi import Request, HTTPException
from collections import defaultdict
import time

# Simple in-memory rate limiting
# In production, use Redis or similar
rate_limit_store = defaultdict(list)

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time.time()

            # Clean old requests
            rate_limit_store[client_ip] = [
                req_time for req_time in rate_limit_store[client_ip]
                if current_time - req_time < window_seconds
            ]

            # Check rate limit
            if len(rate_limit_store[client_ip]) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )

            # Add current request
            rate_limit_store[client_ip].append(current_time)

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
