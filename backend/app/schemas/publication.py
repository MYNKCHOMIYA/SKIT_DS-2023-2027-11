from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PublicationBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the publication")
    publication_type: str = Field(..., description="Journal, Conference, Book, etc.")
    publisher: Optional[str] = None
    publication_year: int
    doi: Optional[str] = None
    citations: int = 0
    # Add to PublicationBase (and make sure they are in PublicationUpdate as Optional)
    authors: Optional[str] = None
    journal: Optional[str] = None
    issn: Optional[str] = None
    indexed_in: Optional[str] = None
    pdf_url: Optional[str] = None


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    publication_type: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    citations: Optional[int] = None
    # Add to PublicationBase (and make sure they are in PublicationUpdate as Optional)
    authors: Optional[str] = None
    journal: Optional[str] = None
    issn: Optional[str] = None
    indexed_in: Optional[str] = None
    pdf_url: Optional[str] = None


class PublicationResponse(PublicationBase):
    id: str
    faculty_id: str

    model_config = ConfigDict(from_attributes=True)
