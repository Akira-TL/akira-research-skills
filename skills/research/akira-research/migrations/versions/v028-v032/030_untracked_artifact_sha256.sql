-- Freeze rule: Git-tracked artifacts are frozen by commit + path and carry no
-- file checksum. Artifacts outside Git (external storage, model weights,
-- checkpoints, ignored outputs) may record one SHA256 of their content.
ALTER TABLE dataset_artifacts ADD COLUMN sha256 TEXT;
ALTER TABLE study_artifacts ADD COLUMN sha256 TEXT;
ALTER TABLE analysis_artifacts ADD COLUMN sha256 TEXT;

-- Carry over checksums that older projects stored in the free-text version
-- field of untracked artifacts. The version text itself stays unchanged.
UPDATE dataset_artifacts
SET sha256 = lower(substr(trim(version), 8))
WHERE git_tracking = 'not_required'
  AND lower(substr(trim(version), 1, 7)) = 'sha256:'
  AND length(trim(version)) = 71
  AND lower(substr(trim(version), 8)) NOT GLOB '*[^0-9a-f]*';
UPDATE dataset_artifacts
SET sha256 = lower(trim(version))
WHERE git_tracking = 'not_required'
  AND sha256 IS NULL
  AND length(trim(version)) = 64
  AND lower(trim(version)) NOT GLOB '*[^0-9a-f]*';
UPDATE study_artifacts
SET sha256 = lower(substr(trim(version), 8))
WHERE git_tracking = 'not_required'
  AND lower(substr(trim(version), 1, 7)) = 'sha256:'
  AND length(trim(version)) = 71
  AND lower(substr(trim(version), 8)) NOT GLOB '*[^0-9a-f]*';
UPDATE study_artifacts
SET sha256 = lower(trim(version))
WHERE git_tracking = 'not_required'
  AND sha256 IS NULL
  AND length(trim(version)) = 64
  AND lower(trim(version)) NOT GLOB '*[^0-9a-f]*';
