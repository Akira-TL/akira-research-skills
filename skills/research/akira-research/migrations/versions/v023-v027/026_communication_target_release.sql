ALTER TABLE communication_products ADD COLUMN canonical_source_path TEXT;

CREATE TABLE communication_journals (
    code TEXT PRIMARY KEY COLLATE NOCASE,
    name TEXT NOT NULL,
    name_key TEXT NOT NULL UNIQUE,
    official_source TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE communication_target_workspaces (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES communication_products(id) ON DELETE CASCADE,
    journal_code TEXT NOT NULL REFERENCES communication_journals(code),
    workspace_path TEXT NOT NULL,
    manifest_path TEXT NOT NULL,
    source_commit TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(product_id, journal_code),
    UNIQUE(product_id, workspace_path)
);
CREATE INDEX communication_target_workspaces_product_idx
    ON communication_target_workspaces(product_id, journal_code);

CREATE TABLE communication_target_files (
    id INTEGER PRIMARY KEY,
    target_id INTEGER NOT NULL REFERENCES communication_target_workspaces(id) ON DELETE CASCADE,
    kind TEXT NOT NULL
        CHECK (kind IN ('manifest', 'config', 'build_source', 'template', 'qa_evidence')),
    path TEXT NOT NULL,
    content_oid TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(target_id, path)
);
CREATE INDEX communication_target_files_target_idx
    ON communication_target_files(target_id, kind);
