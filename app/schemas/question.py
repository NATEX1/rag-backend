"""Request schemas for question-related endpoints."""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Schema for receiving a question from the user."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The question to ask the RAG system",
        json_schema_extra={
            "examples": ["What are the admission requirements?"]
        },
    )
