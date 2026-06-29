CREATE TYPE difficultylevel AS ENUM ('GCSE', 'AS_LEVEL', 'A_LEVEL', 'UNDERGRADUATE', 'OTHER');
CREATE TYPE rubricversionstatus AS ENUM ('DRAFT', 'APPROVED', 'DEPRECATED');
CREATE TYPE rubricstatus AS ENUM ('DRAFT', 'APPROVED', 'REJECTED');

CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject VARCHAR(100) NOT NULL,
    difficulty difficultylevel NOT NULL,
    text TEXT NOT NULL,
    max_mark INTEGER NOT NULL,
    created_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE master_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_master_answers_question_id ON master_answers(question_id);

CREATE TABLE rubric_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    master_answer_id UUID REFERENCES master_answers(id),
    version INTEGER NOT NULL,
    status rubricversionstatus NOT NULL DEFAULT 'DRAFT',
    approved_by VARCHAR(200),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_rubric_versions_question_id ON rubric_versions(question_id);
CREATE INDEX ix_rubric_versions_status ON rubric_versions(status);

CREATE TABLE rubrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rubric_version_id UUID NOT NULL REFERENCES rubric_versions(id) ON DELETE CASCADE,
    concept VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    keywords TEXT,
    order_index INTEGER NOT NULL DEFAULT 0,
    status rubricstatus NOT NULL DEFAULT 'DRAFT'
);
CREATE INDEX ix_rubrics_rubric_version_id ON rubrics(rubric_version_id);

CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);
INSERT INTO alembic_version VALUES ('0001_initial');