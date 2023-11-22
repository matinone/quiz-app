from fastapi import APIRouter

from app.api.endpoints import question, quiz

api_router = APIRouter()
api_router.include_router(quiz.router)
api_router.include_router(question.router)
