from pydantic import BaseModel
from typing import List


class Flashcard(BaseModel):
    id: str
    backend_id: int
    question: str
    options: List[str]
    correct_index: int


class AnswerRequest(BaseModel):
    backend_id: int
    user_answer: int


class AnswerResult(BaseModel):
    correct: bool
    correct_index: int
    message: str
