from __future__ import annotations

from pydantic import BaseModel, Field


class ApiItem(BaseModel):
    id: str
    api: str = Field(description="API display name")
    api_link: str
    description: str
    auth: str | None = None
    https: str | bool | None = None
    cors: str | None = None
    category: str | None = None


class SearchResult(BaseModel):
    id: str
    name: str
    score: float
    snippet: str
