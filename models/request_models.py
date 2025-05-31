from typing import Optional
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image


class LinkResponse(BaseModel):
    url: str
    text: str


class AnswerResponse(BaseModel):
    answer: str
    links: list[LinkResponse]