-- A Git-tracked object is frozen by commit + path. A later commit that changes
-- its content passes the completion gate only with an explicit revision note.
CREATE TABLE freeze_revisions (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    revision_commit TEXT NOT NULL,
    category TEXT NOT NULL
        CHECK (category IN ('path_migration', 'redundant_checksum_removal', 'substantive')),
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    created_at TEXT NOT NULL,
    UNIQUE(path, revision_commit)
);
CREATE INDEX freeze_revisions_commit_idx ON freeze_revisions(revision_commit);
