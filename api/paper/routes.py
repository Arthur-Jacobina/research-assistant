from fastapi import APIRouter

from api.paper.services import handle_get_paper, handle_parse_latex


router = APIRouter(prefix='/paper', tags=['paper'])

router.post('/add')(handle_parse_latex)
router.post('/get')(handle_get_paper)

