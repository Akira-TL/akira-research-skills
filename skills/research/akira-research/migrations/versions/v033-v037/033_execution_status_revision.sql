-- Add the execution_status_update revision category: post-freeze commits that
-- only change execution-layer status, implementation commit ids or review
-- records of a frozen object, never its scientific content.
CREATE TABLE freeze_revisions_v33 (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    revision_commit TEXT NOT NULL,
    category TEXT NOT NULL
        CHECK (
            category IN (
                'path_migration',
                'redundant_checksum_removal',
                'execution_status_update',
                'substantive'
            )
        ),
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    created_at TEXT NOT NULL,
    UNIQUE(path, revision_commit)
);
INSERT INTO freeze_revisions_v33(id, path, revision_commit, category, reason, created_at)
SELECT id, path, revision_commit, category, reason, created_at FROM freeze_revisions;
DROP TABLE freeze_revisions;
ALTER TABLE freeze_revisions_v33 RENAME TO freeze_revisions;
CREATE INDEX freeze_revisions_commit_idx ON freeze_revisions(revision_commit);
