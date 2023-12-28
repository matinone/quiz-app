from fastapi import APIRouter

from app.api.endpoints import login, question, quiz

api_router = APIRouter()
api_router.include_router(quiz.router)
api_router.include_router(question.router)
api_router.include_router(login.router)
