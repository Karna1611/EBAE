import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.rubric import (
    RubricVersionRead, RubricUpdate, RubricGenerateRequest, RubricApproveRequest
)
from app.services.rubric_service import RubricService
from app.services.question_service import QuestionService
from app.services.master_answer_service import MasterAnswerService

router = APIRouter()


@router.post(
    "/generate",
    response_model=RubricVersionRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate_rubrics(
    data: RubricGenerateRequest, db: AsyncSession = Depends(get_db)
):
    """Step 03 — AI generates rubric concepts from master answer. Returns DRAFT version."""
    question = await QuestionService.get(db, data.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    from app.models.master_answer import MasterAnswer
    from sqlalchemy import select
    result = await db.execute(
        select(MasterAnswer).where(MasterAnswer.id == data.master_answer_id)
    )
    master_answer = result.scalar_one_or_none()
    if not master_answer:
        raise HTTPException(status_code=404, detail="Master answer not found")

    try:
        rv = await RubricService.generate_with_ai(db, question, master_answer)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return rv


@router.get("/versions/{version_id}", response_model=RubricVersionRead)
async def get_rubric_version(
    version_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    rv = await RubricService.get_version(db, version_id)
    if not rv:
        raise HTTPException(status_code=404, detail="Rubric version not found")
    return rv


@router.get("/question/{question_id}", response_model=list[RubricVersionRead])
async def list_rubric_versions(
    question_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await RubricService.list_versions(db, question_id)


@router.get("/question/{question_id}/active", response_model=RubricVersionRead)
async def get_active_rubric_version(
    question_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Returns the current APPROVED rubric version — used at submission time."""
    rv = await RubricService.get_active_version(db, question_id)
    if not rv:
        raise HTTPException(status_code=404, detail="No approved rubric version found")
    return rv


@router.post(
    "/versions/{version_id}/approve",
    response_model=RubricVersionRead,
)
async def approve_rubric_version(
    version_id: uuid.UUID,
    data: RubricApproveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Step 04 — Human approves a DRAFT rubric version. Transitions to APPROVED."""
    try:
        rv = await RubricService.approve_version(db, version_id, data.approved_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not rv:
        raise HTTPException(status_code=404, detail="Rubric version not found")
    return rv


@router.patch("/{rubric_id}", response_model=dict)
async def update_rubric(
    rubric_id: uuid.UUID, data: RubricUpdate, db: AsyncSession = Depends(get_db)
):
    """Edit an individual rubric (concept, description, weight) before approval."""
    rubric = await RubricService.update_rubric(db, rubric_id, data)
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return {"id": str(rubric.id), "concept": rubric.concept, "status": rubric.status}


@router.delete("/{rubric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rubric(rubric_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await RubricService.delete_rubric(db, rubric_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rubric not found")
