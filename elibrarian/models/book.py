from pydantic import BaseModel, Field


class OpenLibraryBook(BaseModel):
    title: str
    author: str
    publish_year: int | None = None

    publishers: list[str] = Field(default_factory=list)

    isbn10: list[str] = Field(default_factory=list)
    isbn13: list[str] = Field(default_factory=list)

    cover_id: int | None = None
