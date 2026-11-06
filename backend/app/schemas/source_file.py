from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SourceFileCreate(BaseModel):
    filename: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_\-.]+\.(c|cpp|h|hpp)$",
        description="Filename ending in .c, .cpp, .h, or .hpp",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=1_048_576,  # 1 MB
        description="Raw C/C++ source code text",
    )


class SourceFileUpdate(BaseModel):
    filename: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9_\-.]+\.(c|cpp|h|hpp)$")
    content: Optional[str] = Field(None, min_length=1, max_length=1_048_576)


class SourceFileResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    content_hash: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceFileDetailResponse(SourceFileResponse):
    content: str

