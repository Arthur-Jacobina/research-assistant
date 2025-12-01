from fastapi import APIRouter
from api.chat.routes import router as chat_router
from api.ocr.routes import router as ocr_router
from api.paper.routes import router as paper_router

router = APIRouter(prefix="/api/v1")

router.include_router(chat_router)
router.include_router(ocr_router)
router.include_router(paper_router)

@router.get("/")
async def root():
    return {"message": "ok"}

