from fastapi import APIRouter
from src.routers.model import Context, AsmtChatResponse
from src.models.ChatGPT import get_intent_response

router = APIRouter()

@router.post("/response", response_model=AsmtChatResponse)
async def get_intent_and_response(context: Context):
    if context.chatHistory is not None:
        chat = context.chatHistory
    else:
        chat = []
    response = get_intent_response(context.question, context.question_explaination, context.possible_responses, context.responsetype, context.user_comment,
                                   context.additional_knowledge, chat)

    return response