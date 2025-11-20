from agent.chat_adapter import chat_interaction
from fastapi import Request

from api.models import ChatRequest, ChatResponse

async def handle_chat_message(request: Request, chat_request: ChatRequest) -> ChatResponse:
    session_id = request.headers.get("X-Session-ID", "default-session")
    user_id = request.headers.get("X-User-ID", "default-user")
    response_text = chat_interaction(chat_request.message, user_id, session_id)
    return ChatResponse(response=response_text)
