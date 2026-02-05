"""Response schemas for document-related endpoints."""

from pydantic import BaseModel, Field
from typing import Optional


class DocumentUploadResponse(BaseModel):
    """Schema for document upload results."""

    success: bool = Field(..., description="Whether the upload succeeded")
    message: str = Field(..., description="Status message")
    filename: Optional[str] = Field(
        default=None, description="Name of the uploaded file"
    )
    chunks_created: Optional[int] = Field(
        default=None, description="Number of text chunks created"
    )
