"""Generic pagination DTOs shared across all schema types."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    """Common query parameters for offset-based pagination."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)


class Page(BaseModel, Generic[T]):
    """A single page of results plus total-count metadata."""

    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
