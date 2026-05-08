"""
Cursor-based pagination utility for efficient database queries.

This module provides cursor-based pagination which is O(log n) with proper indices,
compared to OFFSET-based pagination which is O(n).
"""

import base64
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class CursorPaginationParams:
    """Parameters for cursor-based pagination."""

    cursor: str | None = None
    limit: int = 24

    def __post_init__(self) -> None:
        """Validate pagination parameters."""
        if not isinstance(self.limit, int) or self.limit < 1 or self.limit > 100:
            raise ValueError("limit must be between 1 and 100")


@dataclass
class CursorPageResponse(Generic[T]):
    """Response object for cursor-paginated data."""

    items: list[T]
    next_cursor: str | None = None


def encode_cursor(item_id: int, timestamp: datetime) -> str:
    """
    Encode a cursor from an item ID and creation timestamp.

    Args:
        item_id: The unique identifier of the last item.
        timestamp: The creation timestamp of the last item (from SQLAlchemy datetime).

    Returns:
        A base64-encoded cursor string.
    """
    # Ensure timestamp is timezone-naive ISO format
    if hasattr(timestamp, "isoformat"):
        timestamp_str = timestamp.isoformat()
    else:
        timestamp_str = str(timestamp)

    cursor_data = {"id": item_id, "ts": timestamp_str}
    json_str = json.dumps(cursor_data)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded


def decode_cursor(cursor: str) -> tuple[int, datetime]:
    """
    Decode a cursor into item ID and creation timestamp.

    Args:
        cursor: A base64-encoded cursor string.

    Returns:
        A tuple of (item_id, timestamp).

    Raises:
        ValueError: If cursor is invalid or malformed.
    """
    try:
        json_str = base64.b64decode(cursor).decode()
        cursor_data = json.loads(json_str)
        item_id = cursor_data["id"]
        timestamp_str = cursor_data["ts"]
        # Parse ISO format timestamp
        timestamp = datetime.fromisoformat(timestamp_str)
        return item_id, timestamp
    except (ValueError, KeyError, json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Invalid cursor format: {e}") from e


__all__ = [
    "CursorPaginationParams",
    "CursorPageResponse",
    "encode_cursor",
    "decode_cursor",
]
