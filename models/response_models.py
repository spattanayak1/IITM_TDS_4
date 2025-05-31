
from pydantic import BaseModel
from typing import List


class LinkResponse(BaseModel):
    url: str
    text: str


class AnswerResponse(BaseModel):
    answer: str
    links: List[LinkResponse]