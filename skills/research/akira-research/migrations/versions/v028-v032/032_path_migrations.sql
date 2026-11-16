-- Whole-directory moves inside the Git repository. Prefixes are relative to
-- the Git top-level ('' for the top-level itself, otherwise 'dir/'). Frozen
-- objects recorded before a move are looked up in older commits by mapping
-- their current path under new_prefix back to old_prefix.
CREATE TABLE path_migrations (
    id INTEGER PRIMARY KEY,
    migration_commit TEXT NOT NULL,
    old_prefix TEXT NOT NULL,
    new_prefix TEXT NOT NULL,
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    created_at TEXT NOT NULL,
    CHECK (old_prefix <> new_prefix),
    UNIQUE(migration_commit, old_prefix)
);
