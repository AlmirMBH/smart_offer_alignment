from fastapi import APIRouter
from fastapi.responses import FileResponse
from constants import FRONTEND_DIR


router = APIRouter()


@router.get("/")
def route_home_page() -> FileResponse:
    return FileResponse(
        FRONTEND_DIR / "index.html",
        headers={"Cache-Control": "no-cache"},
    )
