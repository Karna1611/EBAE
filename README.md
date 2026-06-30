# EBAE — Evidence Based Assessment Engine

AI-assisted student answer marking. Teachers create questions and model answers, Claude decomposes them into atomic rubric concepts, teachers approve, and student answers are automatically evaluated using NLI classification + Claude-as-judge — producing a score and personalised feedback.

---

## Status

| Phase | Description | Status |
|-------|-------------|--------|
| A | Question setup, master answers, rubric generation & approval | Complete |
| B | Student evaluation pipeline, review queue, analytics, frontend | Complete |
| C | Real DeBERTa-v3 NLI model, pgvector semantic search, GPU inference | Planned |
| D | JWT auth, multi-tenancy, student accounts | Planned |
| E | Cloud deployment, CI/CD, WebSocket pipeline status, CSV/PDF export | Planned |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Pydantic v2 + SQLAlchemy (async) |
| Database | PostgreSQL 16 + pgvector |
| Queue | Celery + Redis |
| AI | Claude API (`claude-sonnet-4-6`) — rubric generation, LLM judge, feedback |
| NLI | Mock keyword classifier (Phase B) → DeBERTa-v3 (Phase C) |
| Frontend | React + Vite |
| Infrastructure | Docker Compose (4 containers) |

---

## Getting started

### Prerequisites
- Docker Desktop
- Node.js 18+
- An Anthropic API key

### 1. Configure environment

```bash
cp .env.example .env
# Set ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Start all services

```bash
docker compose up -d
```

This starts four containers: `ebae_db` (PostgreSQL 16), `ebae_redis`, `ebae_api` (FastAPI on port 8000), `ebae_worker` (Celery).

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

### Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## API endpoints

### Phase A — Question setup

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/questions/` | Create question |
| GET | `/api/v1/questions/` | List questions |
| GET | `/api/v1/questions/{id}` | Get question |
| POST | `/api/v1/questions/{id}/master-answer` | Add / update master answer |
| GET | `/api/v1/questions/{id}/master-answer` | Get active master answer |
| POST | `/api/v1/rubrics/generate` | AI-generate rubric DRAFT from master answer |
| POST | `/api/v1/rubrics/versions/{id}/approve` | Approve rubric version |
| GET | `/api/v1/rubrics/question/{id}/active` | Get active (APPROVED) rubric set |

### Phase B — Evaluation pipeline

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/questions/{id}/submit` | Submit single student answer, run full pipeline |
| POST | `/api/v1/questions/{id}/bulk-submit` | Upload CSV of student answers, evaluate all |
| GET | `/api/v1/review/` | List all review queue items (pending + resolved) |
| POST | `/api/v1/review/{id}/resolve` | Teacher override for a flagged evaluation |
| GET | `/api/v1/analytics/question/{id}` | Score distributions, rubric miss rates, LLM escalation rate |

---

## Evaluation pipeline (Steps 07–16)

```
Student answer
    │
    ▼
07  Preprocessing       — clean, normalise, segment
08  Evidence retrieval  — keyword overlap extraction per rubric
09  Evidence scoring    — rank passages by relevance
    │
    ├─ for each rubric ──────────────────────────────────────┐
    │                                                        │
    ▼                                                        │
10  NLI classification  — fast first-pass confidence score  │
    │                                                        │
    ├── confidence ≥ 0.85 ──► NLI label (no Claude call)   │
    │                                                        │
    └── confidence < 0.85 ──► Step 11                       │
                                │                            │
                                ▼                            │
11                  LLM judge  — Claude evaluates            │
                    (3x retry with backoff on timeout)       │
                                │                            │
                                ▼                            │
12  Confidence scoring + conflict detection ◄────────────────┘
    │
    ├── flagged? ──► Step 13 (review queue)
    │
    ▼
14  Mark allocation     — PRESENT=100%, PARTIAL=50%, ABSENT/CONTRADICTORY=0%
15  Feedback generation — Claude writes personalised feedback
16  Result storage      — full audit trail
```

---

## Bulk upload CSV format

```csv
student_name,student_id,answer
Rahul Sharma,STU001,"Full answer text here — wrap in quotes if it contains commas"
Priya Nair,STU002,Short answers without commas do not need quotes
Arjun Mehta,,Student ID is optional — leave blank if not needed
```

Download a pre-filled template from the Student Portal → Bulk upload tab.

---

## Frontend views

| View | Description |
|------|-------------|
| Questions | Create questions, write master answers, generate and approve rubrics with AI |
| Student portal | Submit single answers or bulk-upload a CSV; view score, rubric breakdown, and AI feedback |
| Review queue | Flagged evaluations with student name and rubric concept; teacher override with label + note |
| Analytics | Score distributions, per-rubric label breakdown, LLM escalation rate |

---

## Project structure

```
ebae/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── db/
│   │   ├── models/              # questions, master_answers, rubric_versions,
│   │   │                        # rubrics, submissions, rubric_evaluations, review_queue
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── evaluation_pipeline.py
│   │   │   ├── llm_judge_service.py   # Claude judge with retry + backoff
│   │   │   ├── nli_service.py         # Mock NLI (Phase B) / DeBERTa-v3 (Phase C)
│   │   │   ├── feedback_service.py
│   │   │   ├── rubric_service.py
│   │   │   ├── review_service.py
│   │   │   └── preprocessing.py
│   │   ├── api/v1/endpoints/
│   │   └── tasks/               # Celery tasks
│   └── alembic/
├── frontend/
│   └── src/
│       └── App.jsx              # Single-file React app
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Cost notes

Each submission costs roughly **$0.01–0.02** using `claude-sonnet-4-6` (~6–7 Claude calls per submission: one judge call per rubric + one feedback call). The mock NLI currently escalates ~20% of rubrics to the LLM judge; the real DeBERTa-v3 model (Phase C) will reduce this further.

Always confirm `model="claude-sonnet-4-6"` is set in:
- `app/services/rubric_service.py`
- `app/services/llm_judge_service.py`
- `app/services/feedback_service.py`
- `app/tasks/rubric_tasks.py`
