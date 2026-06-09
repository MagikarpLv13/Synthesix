MIGRATIONS = (
    (
        1,
        """
        CREATE TABLE app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE investigations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            reference TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            tags_json TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'archived')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        );

        CREATE TABLE search_runs (
            id TEXT PRIMARY KEY,
            investigation_id TEXT REFERENCES investigations(id) ON DELETE SET NULL,
            original_query TEXT NOT NULL DEFAULT '',
            parsed_query TEXT NOT NULL DEFAULT '',
            filters_json TEXT NOT NULL DEFAULT '{}',
            engines_json TEXT NOT NULL DEFAULT '{}',
            requested_results INTEGER NOT NULL DEFAULT 0,
            result_count INTEGER NOT NULL DEFAULT 0,
            total_time REAL NOT NULL DEFAULT 0,
            report_path TEXT,
            status TEXT NOT NULL
                CHECK (status IN ('completed', 'failed', 'legacy')),
            engine_errors_json TEXT NOT NULL DEFAULT '{}',
            started_at TEXT NOT NULL,
            completed_at TEXT,
            legacy_source_key TEXT UNIQUE
        );

        CREATE TABLE results (
            id TEXT PRIMARY KEY,
            canonical_url TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            first_observed_at TEXT NOT NULL,
            last_observed_at TEXT NOT NULL
        );

        CREATE TABLE search_result_observations (
            search_run_id TEXT NOT NULL REFERENCES search_runs(id) ON DELETE CASCADE,
            result_id TEXT NOT NULL REFERENCES results(id) ON DELETE CASCADE,
            source_json TEXT NOT NULL DEFAULT '[]',
            title TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            relevance_score REAL NOT NULL DEFAULT 0,
            observed_at TEXT NOT NULL,
            PRIMARY KEY (search_run_id, result_id)
        );

        CREATE TABLE investigation_results (
            investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
            result_id TEXT NOT NULL REFERENCES results(id) ON DELETE CASCADE,
            analyst_status TEXT NOT NULL DEFAULT 'a_verifier'
                CHECK (analyst_status IN ('a_verifier', 'pertinent', 'ecarte', 'confirme')),
            favorite INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0, 1)),
            notes TEXT NOT NULL DEFAULT '',
            tags_json TEXT NOT NULL DEFAULT '[]',
            added_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (investigation_id, result_id)
        );

        CREATE INDEX idx_investigations_status_updated
            ON investigations(status, updated_at DESC);
        CREATE INDEX idx_search_runs_investigation_started
            ON search_runs(investigation_id, started_at DESC);
        CREATE INDEX idx_results_last_observed
            ON results(last_observed_at DESC);
        CREATE INDEX idx_observations_result
            ON search_result_observations(result_id, observed_at DESC);
        CREATE INDEX idx_investigation_results_status
            ON investigation_results(investigation_id, analyst_status, favorite);
        """,
    ),
    (
        2,
        """
        ALTER TABLE investigation_results
            ADD COLUMN is_saved INTEGER NOT NULL DEFAULT 0
            CHECK (is_saved IN (0, 1));
        ALTER TABLE investigation_results
            ADD COLUMN discovery_method TEXT NOT NULL DEFAULT '';
        ALTER TABLE investigation_results
            ADD COLUMN discovery_search_run_id TEXT
            REFERENCES search_runs(id) ON DELETE SET NULL;
        ALTER TABLE investigation_results
            ADD COLUMN discovery_query TEXT NOT NULL DEFAULT '';
        ALTER TABLE investigation_results
            ADD COLUMN discovery_sources_json TEXT NOT NULL DEFAULT '[]';
        ALTER TABLE investigation_results
            ADD COLUMN discovery_report_path TEXT;
        ALTER TABLE investigation_results
            ADD COLUMN discovery_observed_at TEXT;
        ALTER TABLE investigation_results
            ADD COLUMN discovery_referrer TEXT NOT NULL DEFAULT '';

        CREATE INDEX idx_investigation_results_saved
            ON investigation_results(
                investigation_id,
                is_saved,
                analyst_status,
                favorite
            );
        """,
    ),
    (
        3,
        """
        CREATE TABLE evidence_captures (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL
                REFERENCES investigations(id) ON DELETE CASCADE,
            result_id TEXT NOT NULL
                REFERENCES results(id) ON DELETE CASCADE,
            source_url TEXT NOT NULL,
            page_title TEXT NOT NULL DEFAULT '',
            capture_scope TEXT NOT NULL
                CHECK (capture_scope IN ('viewport', 'region')),
            selection_json TEXT NOT NULL DEFAULT '{}',
            manifest_path TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'completed'
                CHECK (status IN ('completed', 'partial', 'failed')),
            error TEXT NOT NULL DEFAULT '',
            tool_version TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE evidence_artifacts (
            id TEXT PRIMARY KEY,
            capture_id TEXT NOT NULL
                REFERENCES evidence_captures(id) ON DELETE CASCADE,
            artifact_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            mime_type TEXT NOT NULL DEFAULT 'application/octet-stream',
            sha256 TEXT NOT NULL,
            byte_size INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(capture_id, artifact_type)
        );

        CREATE INDEX idx_evidence_captures_investigation
            ON evidence_captures(investigation_id, captured_at DESC);
        CREATE INDEX idx_evidence_captures_result
            ON evidence_captures(result_id, captured_at DESC);
        CREATE INDEX idx_evidence_artifacts_capture
            ON evidence_artifacts(capture_id);
        """,
    ),
    (
        4,
        """
        ALTER TABLE evidence_captures
            ADD COLUMN name TEXT NOT NULL DEFAULT '';
        """,
    ),
)
