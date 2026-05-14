"""Pydantic schemas for request and response bodies."""

from __future__ import annotations

from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class LinkCreate(BaseModel):
    url: AnyHttpUrl = Field(..., description="Target URL to shorten.")


class LinkCreated(BaseModel):
    short_id: str
    url: str


class LinkDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_id: str
    url: str
    hits: int
    created_at: datetime


class Health(BaseModel):
    status: str
