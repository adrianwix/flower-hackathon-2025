Here we go 👇

## Brief summary

You have a **single-tenant**, on-prem schema for a radiology review app that:

* Manages **users (doctors)**, **patients**, and **exams**.
* Stores X-ray **images in PostgreSQL as `bytea`**, with an optional `ground_truth_labels TEXT[]` field for NIH-seeded demo data.
* Tracks **ML predictions** (`image_predicted_label`) per image & pathology & model version.
* Tracks **doctor labels** (`doctor_label`) as human validation of the ML result (AI Act: human in the loop).
* Exposes a **review workflow** via `image.review_status` so you can list “images needing doctor review”.

---

## Full SQL schema

```sql
-- =========================================================
--  Types
-- =========================================================

-- Workflow status for an image in the review process
CREATE TYPE review_status AS ENUM ('pending', 'in_review', 'completed');

-- =========================================================
--  Users (doctors)
-- =========================================================

CREATE TABLE "user" (
    id             BIGSERIAL PRIMARY KEY,
    email          TEXT NOT NULL UNIQUE,
    full_name      TEXT NOT NULL,
    password_hash  TEXT NOT NULL,          -- can be dummy for hackathon
    role           TEXT NOT NULL DEFAULT 'doctor',  -- 'doctor', 'admin'
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
--  Patients
-- =========================================================

CREATE TABLE patient (
    id                  BIGSERIAL PRIMARY KEY,
    external_patient_id TEXT,    -- e.g. original NIH Patient ID for seeded data
    first_name          TEXT,
    last_name           TEXT,
    birth_year          INT,     -- optional / fake for demo
    sex                 TEXT,    -- 'M', 'F', 'O', etc.
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
--  Exams (visits / imaging sessions)
-- =========================================================

CREATE TABLE exam (
    id             BIGSERIAL PRIMARY KEY,
    patient_id     BIGINT NOT NULL REFERENCES patient(id) ON DELETE CASCADE,
    exam_datetime  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason         TEXT,          -- free text, e.g. "Routine check"
    created_by     BIGINT REFERENCES "user"(id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
--  Images (X-rays) - stored as BYTEA, with optional ground truth
-- =========================================================

CREATE TABLE image (
    id                 BIGSERIAL PRIMARY KEY,
    exam_id            BIGINT NOT NULL REFERENCES exam(id) ON DELETE CASCADE,

    -- raw image data
    filename           TEXT NOT NULL,       -- e.g. "00000001_000.png"
    image_bytes        BYTEA NOT NULL,      -- actual X-ray bytes
    mime_type          TEXT NOT NULL DEFAULT 'image/png',

    -- optional metadata (if available)
    view_position      TEXT,                -- e.g. "PA", "AP"

    -- OPTIONAL ground truth labels for seeded NIH images only.
    -- e.g. {'Effusion','Cardiomegaly'} or {'No Finding'}
    -- For user uploads this will usually be NULL.
    ground_truth_labels TEXT[],

    -- workflow
    review_status      review_status NOT NULL DEFAULT 'pending',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
--  Pathology master table (binary or multi-label)
-- =========================================================

CREATE TABLE pathology (
    id           BIGSERIAL PRIMARY KEY,
    code         TEXT NOT NULL UNIQUE,    -- e.g. 'NO_FINDING', 'CARDIOMEGALY'
    display_name TEXT NOT NULL,          -- e.g. "No Finding", "Cardiomegaly"
    description  TEXT
);

-- Example seed (run separately, not part of DDL if you want):
-- INSERT INTO pathology (code, display_name) VALUES
--   ('NO_FINDING', 'No Finding'),
--   ('ANY_PATHOLOGY', 'Any Pathology');
--
-- Later you can add:
--   'ATELECTASIS', 'CARDIOMEGALY', 'EFFUSION', 'INFILTRATION', 'MASS',
--   'NODULE', 'PNEUMONIA', 'PNEUMOTHORAX', 'CONSOLIDATION', 'EDEMA',
--   'EMPHYSEMA', 'FIBROSIS', 'PLEURAL_THICKENING', 'HERNIA', ...

-- =========================================================
--  Model versions (FL rounds / weight snapshots)
-- =========================================================

CREATE TABLE model_version (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT NOT NULL,          -- e.g. "fl_round_5_resnet34"
    description   TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    artifact_path TEXT                    -- path to weights on disk, if needed
);

-- =========================================================
--  Image predicted labels (ML output)
-- =========================================================

CREATE TABLE image_predicted_label (
    id               BIGSERIAL PRIMARY KEY,
    image_id         BIGINT NOT NULL REFERENCES image(id) ON DELETE CASCADE,
    model_version_id BIGINT NOT NULL REFERENCES model_version(id),
    pathology_id     BIGINT NOT NULL REFERENCES pathology(id),

    probability      REAL NOT NULL,       -- model's probability
    predicted_label  BOOLEAN NOT NULL,    -- thresholded yes/no

    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (image_id, model_version_id, pathology_id)
);

-- =========================================================
--  Doctor labels (human validation / override of ML)
-- =========================================================

CREATE TABLE doctor_label (
    id               BIGSERIAL PRIMARY KEY,
    image_id         BIGINT NOT NULL REFERENCES image(id) ON DELETE CASCADE,
    model_version_id BIGINT NOT NULL REFERENCES model_version(id),
    pathology_id     BIGINT NOT NULL REFERENCES pathology(id),

    is_present       BOOLEAN NOT NULL,    -- doctor's decision for this pathology
    comment          TEXT,

    labeled_by       BIGINT NOT NULL REFERENCES "user"(id),
    labeled_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (image_id, model_version_id, pathology_id, labeled_by)
);
```

