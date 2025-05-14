from pydantic import BaseModel
from typing import List
from typing import Optional


class chatHistory(BaseModel):
    role: str
    content: str
    intent: str

class Context(BaseModel):
    question: str
    responsetype: str # adding answer type (single, multiple, short or long) to context
    possible_responses: List[str]
    user_comment: str
    additional_knowledge: str
    question_explaination: str
    chatHistory: List[chatHistory]

class AsmtChatResponseSingle(BaseModel):
    content: str
    intent: Optional[str] = None
    role: str

class AsmtChatResponse(BaseModel):
    response: List[AsmtChatResponseSingle]