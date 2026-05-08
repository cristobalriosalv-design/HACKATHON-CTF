"""HTTP cache headers utilities."""

import hashlib
from datetime import datetime, timedelta

from fastapi import Request, Response


def generate_etag(data: str) -> str:
    """Generate ETag from string data using MD5 hash."""
    return f'"{hashlib.md5(data.encode()).hexdigest()}"'


def add_cache_headers(
    response: Response, max_age: int, etag: str | None = None
) -> None:
    """Add cache-control and ETag headers to response.
    
    Args:
        response: FastAPI Response object
        max_age: Cache duration in seconds
        etag: Optional ETag value (for conditional requests)
    """
    response.headers["Cache-Control"] = f"public, max-age={max_age}"
    response.headers["Vary"] = "Accept-Encoding"
    
    if etag:
        response.headers["ETag"] = etag
    
    # Add Last-Modified header
    last_modified = datetime.utcnow() - timedelta(seconds=max_age)
    response.headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")


def check_etag_match(request: Request, etag: str) -> bool:
    """Check if request's If-None-Match header matches the ETag.
    
    Returns True if they match (should return 304 Not Modified)
    """
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match:
        # Split by comma for multiple ETags
        etags = [tag.strip() for tag in if_none_match.split(",")]
        return etag in etags or "*" in if_none_match
    return False


def check_last_modified(request: Request, last_modified: datetime) -> bool:
    """Check if request's If-Modified-Since header indicates resource hasn't changed.
    
    Returns True if resource hasn't been modified (should return 304)
    """
    if_modified_since = request.headers.get("If-Modified-Since")
    if if_modified_since:
        try:
            since = datetime.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S GMT")
            return last_modified <= since
        except ValueError:
            return False
    return False
