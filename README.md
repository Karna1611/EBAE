# EBAE — Evidence Based Assessment Engine

AI-assisted student answer marking using rubric decomposition, NLI classification, and LLM-as-a-Judge scoring.

## Stack
- **Backend:** FastAPI + Pydantic v2 + SQLAlchemy + Alembic
- **Database:** PostgreSQL 16 + pgvector
- **Queue:** Celery + Redis
- **AI:** Claude API (rubric gen + LLM judge) + DeBERTa-v3 NLI (Phase B)
- **Frontend:** React + TypeScript (Phase B)

## Getting started

### 1. Prerequisites
- Docker + Docker Compose
- Python 3.11+
- An Anthropic API key

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start infrastructure
```bash
docker compose up db redis -d
```

### 4. Run migrations
```bash
cd backend
pip install -r requirements.txt
SYNC_DATABASE_URL=postgresql+psycopg2://ebae:ebae_pass@localhost:5432/ebae_db alembic upgrade head
```

### 5. Start the API
```bash
uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 6. Start Celery worker (optional for async rubric gen)
```bash
celery -A app.tasks.worker worker --loglevel=info
```

---

## Phase A — Endpoints

| Method | Path | Step | Description |
|--------|------|------|-------------|
| POST | `/api/v1/questions/` | 01 | Create question |
| GET | `/api/v1/questions/` | — | List questions |
| POST | `/api/v1/questions/{id}/master-answer` | 02 | Add master answer |
| POST | `/api/v1/rubrics/generate` | 03 | AI-generate rubric DRAFT |
| PATCH | `/api/v1/rubrics/{rubric_id}` | 04 | Edit individual rubric |
| DELETE | `/api/v1/rubrics/{rubric_id}` | 04 | Delete a rubric |
| POST | `/api/v1/rubrics/versions/{id}/approve` | 04 | Approve rubric version |
| GET | `/api/v1/rubrics/question/{id}/active` | 05 | Get active (APPROVED) rubric set |

---

## Project structure

```
ebae/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/config.py       # Settings (pydantic-settings)
│   │   ├── db/                  # SQLAlchemy engine + session
│   │   ├── models/              # ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic
│   │   ├── api/v1/endpoints/    # Route handlers
│   │   └── tasks/               # Celery tasks
│   └── alembic/                 # DB migrations
├── docker-compose.yml
├── .env.example
└── README.md
```
