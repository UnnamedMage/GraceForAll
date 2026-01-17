from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime
import uuid
from .exceptions import AppCodeError


class SlideStyle(BaseModel):
    family: str = "Georgia"
    color: str = "black"
    factor: float = Field(default=1.0, ge=1, le=5)
    italic: bool = False
    bold: bool = False
    v_align: Literal["vcenter", "top", "bottom"] = "vcenter"
    h_align: Literal["hcenter", "right", "left"] = "hcenter"
    in_animation: str = "fade"
    out_animation: str = "fade"
    bg_path: Optional[str] = None


class Song(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    lyrics: list
    slide_style: SlideStyle

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str):
        if not v.strip():
            raise AppCodeError("song.empty_title")
        return v

    @field_validator("lyrics")
    @classmethod
    def validate_lyrics(cls, v: list):
        if not v:
            raise AppCodeError("song.empty_lyrics")
        if not all(isinstance(line, str) for line in v):
            raise AppCodeError("song.invalid_lyrics_type")
        return v


class Bible(BaseModel):
    version: str
    language: str


class Verse(BaseModel):
    version: str
    citation: str
    text: str


class Schedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    items: list[dict]

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        if v is None:
            return str(uuid.uuid4())
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if not v.strip():
            raise AppCodeError("schedule.empty_name")
        return v

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list):
        if not v or v == []:
            raise AppCodeError("schedule.empty_items")
        return v
