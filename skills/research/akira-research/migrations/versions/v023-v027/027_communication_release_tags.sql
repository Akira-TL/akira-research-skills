CREATE TABLE communication_release_tags (
    id INTEGER PRIMARY KEY,
    target_id INTEGER NOT NULL REFERENCES communication_target_workspaces(id) ON DELETE CASCADE,
    tag_name TEXT NOT NULL UNIQUE,
    version_number INTEGER NOT NULL CHECK (version_number >= 1),
    revision_number INTEGER NOT NULL CHECK (revision_number >= 0),
    tag_kind TEXT NOT NULL CHECK (tag_kind IN ('checkpoint', 'release')),
    release_date TEXT,
    baseline_approval_source TEXT
        CHECK (baseline_approval_source IS NULL OR baseline_approval_source IN ('user', 'project_decision')),
    baseline_approval TEXT,
    release_evidence_source TEXT
        CHECK (release_evidence_source IS NULL OR release_evidence_source IN ('user_confirmation', 'public_source')),
    release_evidence TEXT,
    commit_oid TEXT NOT NULL,
    tag_object_oid TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(target_id, version_number, revision_number, tag_kind),
    CHECK (
        (tag_kind = 'checkpoint' AND release_date IS NULL AND release_evidence_source IS NULL AND release_evidence IS NULL)
        OR
        (tag_kind = 'release' AND release_date IS NOT NULL AND release_evidence_source IS NOT NULL AND release_evidence IS NOT NULL)
    )
);
CREATE INDEX communication_release_tags_target_idx
    ON communication_release_tags(target_id, version_number, revision_number, tag_kind);
