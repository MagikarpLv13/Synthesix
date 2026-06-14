import csv
import hashlib
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

from exports.zeroneurone import (
    GRAPHML_NAMESPACE,
    build_export_graph,
    export_zeroneurone_bundle,
)


def export_workspace():
    return {
        "investigation": {
            "id": "case-1",
            "title": "Case One",
            "reference": "REF-1",
            "description": "Export test",
            "tags": ["priority"],
            "status": "active",
            "created_at": "2026-06-12T10:00:00+00:00",
        },
        "results": [
            {
                "id": "result-1",
                "canonical_url": "https://example.org/profile",
                "url": "https://example.org/profile",
                "title": "Public profile",
                "notes": "Reviewed profile.",
                "tags": ["profile", "person"],
                "sources": ["Google"],
                "analyst_status": "pertinent",
                "favorite": True,
                "first_observed_at": "2026-06-12T10:01:00+00:00",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
                "latest_observed_at": "2026-06-12T10:02:00+00:00",
                "discovery_search_run_id": "search-1",
            }
        ],
        "searches": [
            {
                "id": "search-1",
                "original_query": "public profile",
                "parsed_query": '"public profile"',
                "filters": {},
                "engines": {"google": True},
                "report_path": "history/report.html",
                "started_at": "2026-06-12T10:00:00+00:00",
            }
        ],
        "entities": [
            {
                "id": "entity-email",
                "result_id": "result-1",
                "entity_type": "email",
                "value_original": "jane@example.org",
                "value_normalized": "jane@example.org",
                "source_field": "description",
                "source_text": "Contact jane@example.org.",
                "confidence": 0.99,
                "status": "validated",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            },
            {
                "id": "entity-handle",
                "result_id": "result-1",
                "entity_type": "handle",
                "value_original": "@unverified",
                "value_normalized": "@unverified",
                "source_field": "notes",
                "source_text": "Possible handle @unverified.",
                "confidence": 0.85,
                "status": "rejected",
                "last_observed_at": "2026-06-12T10:03:00+00:00",
            },
        ],
        "evidence": [
            {
                "id": "capture-1",
                "result_id": "result-1",
                "name": "Profile header",
                "capture_kind": "screenshot",
                "capture_scope": "viewport",
                "status": "completed",
                "source_url": "https://example.org/profile",
                "manifest_path": "data/evidence/capture-1/manifest.json",
                "captured_at": "2026-06-12T10:04:00+00:00",
                "error": "",
                "artifacts": [],
            }
        ],
    }


class ZeroNeuroneExportTestCase(unittest.TestCase):
    def test_default_graph_exports_validated_entities_and_observed_relations(self):
        nodes, edges = build_export_graph(export_workspace())

        labels = {node.label for node in nodes}
        relations = {edge.label for edge in edges}
        self.assertEqual(len(nodes), 4)
        self.assertEqual(len(edges), 4)
        self.assertIn("jane@example.org", labels)
        self.assertNotIn("@unverified", labels)
        self.assertNotIn("Profile header", labels)
        self.assertEqual(
            relations,
            {"CONTAINS", "FOUND_BY", "MENTIONS"},
        )
        self.assertTrue(
            all(
                edge.properties["relation_status"] == "observed"
                for edge in edges
            )
        )

    def test_explicit_full_export_includes_evidence_and_unreviewed_entities(self):
        nodes, edges = build_export_graph(
            export_workspace(),
            include_evidence=True,
            include_unreviewed=True,
        )

        labels = {node.label for node in nodes}
        self.assertIn("@unverified", labels)
        self.assertIn("Profile header", labels)
        self.assertIn("CAPTURED_AS", {edge.label for edge in edges})

    def test_writes_graphml_csv_and_hashed_manifest(self):
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "export"
            exported = export_zeroneurone_bundle(
                export_workspace(),
                output_dir,
                tool_version="test",
            )

            self.assertEqual(exported.node_count, 4)
            self.assertEqual(exported.edge_count, 4)
            root = ElementTree.parse(exported.graphml_path).getroot()
            keys = {
                key.attrib["attr.name"]
                for key in root.findall(f"{{{GRAPHML_NAMESPACE}}}key")
            }
            self.assertTrue(
                {"label", "notes", "tags", "latitude", "longitude"}.issubset(
                    keys
                )
            )
            self.assertEqual(
                len(
                    root.findall(
                        f".//{{{GRAPHML_NAMESPACE}}}node"
                    )
                ),
                4,
            )
            self.assertEqual(
                len(
                    root.findall(
                        f".//{{{GRAPHML_NAMESPACE}}}edge"
                    )
                ),
                4,
            )

            with exported.csv_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                {"type", "label", "de", "vers", "confiance"}.issubset(
                    rows[0]
                ),
                True,
            )
            self.assertEqual(
                {row["type"] for row in rows},
                {"element", "lien"},
            )

            manifest = json.loads(
                exported.manifest_path.read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["schema"], "synthesix-zeroneurone")
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(
                manifest["counts"],
                {"nodes": 4, "edges": 4, "assets": 0},
            )
            for artifact in manifest["artifacts"]:
                path = output_dir / artifact["name"]
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(artifact["sha256"], digest)

    def test_native_dossier_preserves_tags_links_properties_and_assets(self):
        workspace = export_workspace()
        workspace["entities"].append(
            {
                "id": "entity-domain",
                "result_id": "result-1",
                "entity_type": "domain",
                "value_original": "example.org",
                "value_normalized": "example.org",
                "source_field": "url",
                "source_text": "https://example.org/profile",
                "confidence": 0.95,
                "status": "validated",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            artifact_path = evidence_dir / "capture-1" / "capture.png"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_bytes(b"png-data")
            workspace["evidence"][0]["artifacts"] = [
                {
                    "id": "artifact-1",
                    "file_path": artifact_path.relative_to(base_dir).as_posix(),
                    "mime_type": "image/png",
                    "sha256": hashlib.sha256(b"png-data").hexdigest(),
                    "byte_size": len(b"png-data"),
                }
            ]
            exported = export_zeroneurone_bundle(
                workspace,
                base_dir / "export",
                include_evidence=True,
                base_dir=base_dir,
                asset_root=evidence_dir,
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )
            with zipfile.ZipFile(exported.archive_path) as archive:
                archived_names = set(archive.namelist())

        self.assertEqual(dossier["version"], "1.1.0")
        self.assertEqual(exported.asset_count, 1)
        element_ids = {element["id"] for element in dossier["elements"]}
        self.assertTrue(
            all(
                link["fromId"] in element_ids
                and link["toId"] in element_ids
                for link in dossier["links"]
            )
        )
        result = next(
            element
            for element in dossier["elements"]
            if element["label"] == "https://example.org/profile"
        )
        self.assertIn("person", result["tags"])
        self.assertEqual(result["visual"]["icon"], "User")
        properties = {
            item["key"]: item
            for item in result["properties"]
        }
        self.assertEqual(properties["URL"]["type"], "link")
        self.assertEqual(properties["Domaine"]["value"], "example.org")
        self.assertEqual(
            properties["Date d'accès"]["value"],
            "2026-06-12T10:02:00+00:00",
        )
        domain = next(
            element
            for element in dossier["elements"]
            if element["label"] == "example.org"
        )
        domain_properties = {
            item["key"]: item["value"]
            for item in domain["properties"]
        }
        self.assertEqual(domain_properties["Domaine"], "example.org")
        self.assertEqual(
            domain_properties["Date d'accès"],
            "2026-06-12T10:02:00+00:00",
        )
        evidence = next(
            element
            for element in dossier["elements"]
            if element["label"] == "Profile header"
        )
        self.assertEqual(len(evidence["assetIds"]), 1)
        self.assertIn("dossier.json", archived_names)
        self.assertTrue(
            any(name.startswith("assets/") for name in archived_names)
        )

    def test_node_ids_are_stable_between_exports(self):
        first_nodes, _ = build_export_graph(export_workspace())
        second_nodes, _ = build_export_graph(export_workspace())

        self.assertEqual(
            [node.id for node in first_nodes],
            [node.id for node in second_nodes],
        )

    def test_csv_neutralizes_formula_like_text(self):
        workspace = export_workspace()
        workspace["results"][0]["notes"] = "=HYPERLINK(\"https://example.org\")"
        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            with exported.nodes_csv_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as handle:
                rows = list(csv.DictReader(handle))

        result_row = next(
            row
            for row in rows
            if row["label"] == "https://example.org/profile"
        )
        self.assertTrue(result_row["notes"].startswith("'="))


if __name__ == "__main__":
    unittest.main()
