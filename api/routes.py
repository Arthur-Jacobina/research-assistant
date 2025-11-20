from fastapi import APIRouter
from api.services import handle_chat_message

router = APIRouter(prefix="/api/v1")

router.post("/chat")(handle_chat_message)

@router.get("/")
async def root():
    return {"message": "ok"}

