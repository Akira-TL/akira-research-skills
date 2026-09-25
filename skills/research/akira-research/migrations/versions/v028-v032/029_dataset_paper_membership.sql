CREATE TABLE dataset_papers (
    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    PRIMARY KEY(dataset_id, paper_id)
);
CREATE INDEX dataset_papers_paper_idx ON dataset_papers(paper_id);
