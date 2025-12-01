from fastapi import APIRouter

from api.chat.services import handle_chat_message


router = APIRouter(prefix='/chat', tags=['chat'])

router.post('')(handle_chat_message)

