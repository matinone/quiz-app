from fastapi import APIRouter

from app.api.endpoints import quiz

api_router = APIRouter()
api_router.include_router(quiz.router)
