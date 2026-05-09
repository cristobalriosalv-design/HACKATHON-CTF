"""File upload validation utilities."""

from fastapi import HTTPException, UploadFile

# Upload size limits in bytes
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_THUMBNAIL_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB


async def get_file_size(file: UploadFile) -> int:
    """Get file size by seeking to end."""
    # Seek to end of file using the underlying file object
    file.file.seek(0, 2)  # Seek to end (whence=2)
    size = file.file.tell()  # Get current position (which is the file size)
    file.file.seek(0)  # Reset to beginning
    return size


async def validate_video_size(file: UploadFile) -> None:
    """Validate video file doesn't exceed max size."""
    size = await get_file_size(file)
    if size > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Video file exceeds {MAX_VIDEO_SIZE // (1024*1024)}MB limit. Size: {size // (1024*1024)}MB",
        )


async def validate_thumbnail_size(file: UploadFile) -> None:
    """Validate thumbnail file doesn't exceed max size."""
    size = await get_file_size(file)
    if size > MAX_THUMBNAIL_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Thumbnail exceeds {MAX_THUMBNAIL_SIZE // (1024*1024)}MB limit. Size: {size // (1024*1024)}MB",
        )


async def validate_avatar_size(file: UploadFile) -> None:
    """Validate avatar file doesn't exceed max size."""
    size = await get_file_size(file)
    if size > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Avatar exceeds {MAX_AVATAR_SIZE // (1024*1024)}MB limit. Size: {size // (1024*1024)}MB",
        )
