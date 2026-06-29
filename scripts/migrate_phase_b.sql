-- Phase B tables

CREATE TYPE submissionstatus AS ENUM ('PENDING', 'PROCESSING', 'COMPLETE', 'FAILED', 'REVIEW');
CREATE TYPE evaluationlabel AS ENUM ('PRESENT', 'PARTIAL', 'ABSENT', 'CONTRADICTORY');
CREATE TYPE evaluationmethod AS ENUM ('NLI_ONLY', 'LLM_JUDGE', 'HUMAN_OVERRIDE');
CREATE TYPE reviewstatus AS ENUM ('PENDING', 'RESOLVED');
CREATE TYPE reviewreason AS ENUM ('LOW_CONFIDENCE', 'NLI_LLM_CONFLICT', 'CONTRADICTORY_LABEL', 'STUDENT_APPEAL');

CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    rubric_version_id UUID NOT NULL REFERENCES rubric_versions(id),
    student_name VARCHAR(200) NOT NULL,
    student_id VARCHAR(100),
    raw_answer TEXT NOT NULL,
    preprocessed_answer TEXT,
    status submissionstatus NOT NULL DEFAULT 'PENDING',
    final_score FLOAT,
    max_score FLOAT,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
CREATE INDEX ix_submissions_question_id ON submissions(question_id);
CREATE INDEX ix_submissions_status ON submissions(status);

CREATE TABLE rubric_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    rubric_id UUID NOT NULL REFERENCES rubrics(id),
    evidence_text TEXT,
    nli_entailment FLOAT,
    nli_neutral FLOAT,
    nli_contradiction FLOAT,
    nli_confidence FLOAT,
    nli_label evaluationlabel,
    llm_label evaluationlabel,
    llm_reasoning TEXT,
    llm_confidence FLOAT,
    final_label evaluationlabel NOT NULL DEFAULT 'ABSENT',
    method_used evaluationmethod NOT NULL DEFAULT 'NLI_ONLY',
    score_awarded FLOAT NOT NULL DEFAULT 0.0,
    flagged_for_review BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_rubric_evaluations_submission_id ON rubric_evaluations(submission_id);

CREATE TABLE review_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    evaluation_id UUID NOT NULL REFERENCES rubric_evaluations(id) ON DELETE CASCADE,
    reason reviewreason NOT NULL,
    status reviewstatus NOT NULL DEFAULT 'PENDING',
    reviewer VARCHAR(200),
    override_label VARCHAR(50),
    reviewer_note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
CREATE INDEX ix_review_queue_status ON review_queue(status);
