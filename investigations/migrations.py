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
    (
        5,
        """
        ALTER TABLE search_result_observations
            ADD COLUMN score_breakdown_json TEXT NOT NULL DEFAULT '[]';
        """,
    ),
    (
        6,
        """
        CREATE TABLE local_search_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_key TEXT NOT NULL UNIQUE,
            result_id TEXT NOT NULL REFERENCES results(id) ON DELETE CASCADE,
            investigation_id TEXT REFERENCES investigations(id) ON DELETE CASCADE,
            investigation_title TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '',
            sources TEXT NOT NULL DEFAULT '',
            analyst_status TEXT NOT NULL DEFAULT '',
            domain TEXT NOT NULL DEFAULT '',
            first_observed_at TEXT NOT NULL DEFAULT '',
            last_observed_at TEXT NOT NULL DEFAULT '',
            is_saved INTEGER NOT NULL DEFAULT 0 CHECK (is_saved IN (0, 1)),
            evidence_count INTEGER NOT NULL DEFAULT 0
        );

        CREATE VIRTUAL TABLE local_search_fts USING fts5(
            title,
            description,
            url,
            notes,
            tags,
            content='local_search_documents',
            content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        );

        CREATE TRIGGER local_search_documents_ai
        AFTER INSERT ON local_search_documents BEGIN
            INSERT INTO local_search_fts(
                rowid, title, description, url, notes, tags
            )
            VALUES (
                new.id, new.title, new.description, new.url, new.notes, new.tags
            );
        END;

        CREATE TRIGGER local_search_documents_ad
        AFTER DELETE ON local_search_documents BEGIN
            INSERT INTO local_search_fts(
                local_search_fts, rowid, title, description, url, notes, tags
            )
            VALUES (
                'delete', old.id, old.title, old.description, old.url,
                old.notes, old.tags
            );
        END;

        CREATE TRIGGER local_search_documents_au
        AFTER UPDATE ON local_search_documents BEGIN
            INSERT INTO local_search_fts(
                local_search_fts, rowid, title, description, url, notes, tags
            )
            VALUES (
                'delete', old.id, old.title, old.description, old.url,
                old.notes, old.tags
            );
            INSERT INTO local_search_fts(
                rowid, title, description, url, notes, tags
            )
            VALUES (
                new.id, new.title, new.description, new.url, new.notes, new.tags
            );
        END;

        CREATE INDEX idx_local_search_documents_result
            ON local_search_documents(result_id);
        CREATE INDEX idx_local_search_documents_investigation
            ON local_search_documents(investigation_id, last_observed_at DESC);
        CREATE INDEX idx_local_search_documents_filters
            ON local_search_documents(
                analyst_status,
                domain,
                last_observed_at DESC
            );
        """,
    ),
    (
        7,
        """
        ALTER TABLE evidence_captures
            ADD COLUMN capture_kind TEXT NOT NULL DEFAULT 'screenshot'
            CHECK (capture_kind IN ('screenshot', 'page_archive'));

        CREATE TABLE page_monitors (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL
                REFERENCES investigations(id) ON DELETE CASCADE,
            result_id TEXT NOT NULL
                REFERENCES results(id) ON DELETE CASCADE,
            baseline_capture_id TEXT
                REFERENCES evidence_captures(id) ON DELETE SET NULL,
            last_capture_id TEXT
                REFERENCES evidence_captures(id) ON DELETE SET NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(investigation_id, result_id)
        );

        CREATE TABLE page_comparisons (
            id TEXT PRIMARY KEY,
            monitor_id TEXT NOT NULL
                REFERENCES page_monitors(id) ON DELETE CASCADE,
            previous_capture_id TEXT
                REFERENCES evidence_captures(id) ON DELETE SET NULL,
            current_capture_id TEXT NOT NULL
                REFERENCES evidence_captures(id) ON DELETE CASCADE,
            status TEXT NOT NULL
                CHECK (
                    status IN (
                        'unchanged',
                        'minor_change',
                        'changed',
                        'inconclusive'
                    )
                ),
            similarity REAL,
            previous_sha256 TEXT NOT NULL DEFAULT '',
            current_sha256 TEXT NOT NULL DEFAULT '',
            report_path TEXT,
            generated_at TEXT NOT NULL,
            UNIQUE(current_capture_id)
        );

        CREATE INDEX idx_page_monitors_investigation
            ON page_monitors(investigation_id, updated_at DESC);
        CREATE INDEX idx_page_comparisons_monitor
            ON page_comparisons(monitor_id, generated_at DESC);
        CREATE INDEX idx_evidence_captures_kind
            ON evidence_captures(result_id, capture_kind, captured_at DESC);
        """,
    ),
    (
        8,
        """
        CREATE TABLE extracted_entities (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL,
            result_id TEXT NOT NULL,
            entity_type TEXT NOT NULL
                CHECK (
                    entity_type IN (
                        'email',
                        'phone',
                        'url',
                        'domain',
                        'ipv4',
                        'ipv6',
                        'handle',
                        'identifier',
                        'coordinates'
                    )
                ),
            value_original TEXT NOT NULL,
            value_normalized TEXT NOT NULL,
            source_field TEXT NOT NULL
                CHECK (
                    source_field IN (
                        'url',
                        'title',
                        'description',
                        'notes'
                    )
                ),
            source_text TEXT NOT NULL DEFAULT '',
            confidence REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'proposed'
                CHECK (status IN ('proposed', 'validated', 'rejected')),
            first_observed_at TEXT NOT NULL,
            last_observed_at TEXT NOT NULL,
            reviewed_at TEXT,
            FOREIGN KEY (investigation_id, result_id)
                REFERENCES investigation_results(investigation_id, result_id)
                ON DELETE CASCADE,
            UNIQUE(
                investigation_id,
                result_id,
                entity_type,
                value_normalized
            )
        );

        CREATE INDEX idx_extracted_entities_investigation
            ON extracted_entities(
                investigation_id,
                status,
                entity_type,
                last_observed_at DESC
            );
        CREATE INDEX idx_extracted_entities_result
            ON extracted_entities(result_id, entity_type);
        """,
    ),
    (
        9,
        """
        CREATE TABLE investigation_exports (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL
                REFERENCES investigations(id) ON DELETE CASCADE,
            export_type TEXT NOT NULL DEFAULT 'zeroneurone'
                CHECK (export_type IN ('zeroneurone')),
            graphml_path TEXT NOT NULL,
            csv_path TEXT NOT NULL,
            nodes_csv_path TEXT NOT NULL,
            edges_csv_path TEXT NOT NULL,
            manifest_path TEXT NOT NULL,
            include_evidence INTEGER NOT NULL DEFAULT 0
                CHECK (include_evidence IN (0, 1)),
            include_unreviewed INTEGER NOT NULL DEFAULT 0
                CHECK (include_unreviewed IN (0, 1)),
            node_count INTEGER NOT NULL DEFAULT 0,
            edge_count INTEGER NOT NULL DEFAULT 0,
            generated_at TEXT NOT NULL
        );

        CREATE INDEX idx_investigation_exports_generated
            ON investigation_exports(investigation_id, generated_at DESC);
        """,
    ),
    (
        10,
        """
        ALTER TABLE investigation_exports
            ADD COLUMN archive_path TEXT NOT NULL DEFAULT '';
        ALTER TABLE investigation_exports
            ADD COLUMN dossier_path TEXT NOT NULL DEFAULT '';
        ALTER TABLE investigation_exports
            ADD COLUMN asset_count INTEGER NOT NULL DEFAULT 0;
        """,
    ),
)
