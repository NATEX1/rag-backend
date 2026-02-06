"""Response schemas for answer-related endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional


class AnswerResponse(BaseModel):
    """Schema for returning an answer to the user."""

    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The generated answer")
    sources: List[str] = Field(
        default_factory=list, description="Source documents used"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "When does the college accept new students?",
                    "answer": "The college accepts new students during March-May every year.",
                    "sources": ["Student Handbook 2567", "Admission Guidelines"],
                    "confidence": 0.85,
                }
            ]
        }
    }
