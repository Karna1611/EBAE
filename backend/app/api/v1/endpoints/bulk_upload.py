"""
Bulk student answer upload endpoint.
Accepts a CSV file with columns: student_name, student_id (optional), answer
Runs the full evaluation pipeline for each row.
"""
import csv
import io
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.question_service import QuestionService
from app.services.submission_service import SubmissionService
from app.schemas.submission import SubmissionCreate

router = APIRouter()

REQUIRED_COLUMNS = {"student_name", "answer"}
MAX_ROWS = 50  # Safety limit per upload


@router.post("/questions/{question_id}/bulk-submit")
async def bulk_submit_answers(
    question_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV of student answers for a single question.
    Runs the full evaluation pipeline for each row.

    CSV format:
      student_name, student_id (optional), answer
    """
    # Validate question exists and has approved rubrics
    question = await QuestionService.get(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    # Read CSV
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # utf-8-sig handles Excel BOM
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))

    # Validate columns
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    fieldnames = {f.strip().lower() for f in reader.fieldnames}
    missing = REQUIRED_COLUMNS - fieldnames
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV missing required columns: {', '.join(missing)}. Required: student_name, answer",
        )

    # Process rows
    rows = list(reader)
    if len(rows) == 0:
        raise HTTPException(status_code=400, detail="CSV has no data rows")
    if len(rows) > MAX_ROWS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_ROWS} rows per upload")

    results = []
    errors = []

    for i, row in enumerate(rows, start=1):
        # Clean row keys
        row = {k.strip().lower(): v.strip() for k, v in row.items()}

        student_name = row.get("student_name", "").strip()
        student_id = row.get("student_id", "").strip() or None
        answer = row.get("answer", "").strip()

        if not student_name:
            errors.append({"row": i, "error": "student_name is empty"})
            continue
        if not answer or len(answer) < 5:
            errors.append({"row": i, "student_name": student_name, "error": "answer is too short"})
            continue

        try:
            data = SubmissionCreate(
                student_name=student_name,
                student_id=student_id,
                answer=answer,
            )
            submission = await SubmissionService.create_and_evaluate(db, question_id, data)
            results.append({
                "row": i,
                "student_name": student_name,
                "student_id": student_id,
                "submission_id": str(submission.id),
                "score": submission.final_score,
                "max_score": submission.max_score,
                "percentage": round((submission.final_score or 0) / (submission.max_score or 1) * 100, 1),
                "status": submission.status.value,
            })
        except ValueError as e:
            errors.append({"row": i, "student_name": student_name, "error": str(e)})
        except Exception as e:
            errors.append({"row": i, "student_name": student_name, "error": f"Evaluation failed: {str(e)}"})

    return {
        "question_id": str(question_id),
        "question_text": question.text,
        "total_rows": len(rows),
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
