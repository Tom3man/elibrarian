from pydantic import BaseModel


class BookCandidate(BaseModel):
    title: str | None
    author: str | None
    year: str | None
    publisher: str | None
    isbn10: str | None
    isbn13: str | None
