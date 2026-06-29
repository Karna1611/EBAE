from fastapi import APIRouter
from app.api.v1.endpoints import questions, master_answers, rubrics, submissions, review, analytics

api_router = APIRouter()
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(master_answers.router, prefix="/questions", tags=["master-answers"])
api_router.include_router(rubrics.router, prefix="/rubrics", tags=["rubrics"])
api_router.include_router(submissions.router, prefix="/questions", tags=["submissions"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])