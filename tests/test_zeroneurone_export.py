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
    PROPERTY_TYPE_OVERRIDES_KEY,
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

    def test_default_graph_attaches_page_scoped_properties_to_source_node(self):
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
                "attributes": {"property_scope": "page"},
                "property_key": "Domaine",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, _ = build_export_graph(workspace)

        source = next(node for node in nodes if node.id == "result-result-1")
        self.assertEqual(source.properties["Domaine"], "example.org")
        self.assertNotIn("example.org", {node.label for node in nodes})

    def test_curated_graph_keeps_page_scoped_properties_on_source_node(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
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
                "attributes": {"property_scope": "page"},
                "property_key": "Domaine",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, edges = build_export_graph(workspace)

        source = next(node for node in nodes if node.id == "result-result-1")
        person = next(node for node in nodes if node.id == "curated-entity-person-1")
        self.assertEqual(source.properties["Domaine"], "example.org")
        self.assertNotIn("Domaine", person.properties)
        self.assertIn("Site web", source.tags)
        self.assertIn("Trouvé sur", {edge.label for edge in edges})

    def test_curated_graph_surfaces_page_property_attached_to_entity(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-first-seen",
                "result_id": "result-1",
                "investigation_entity_id": "person-1",
                "entity_type": "other",
                "value_original": "2024-08-23",
                "value_normalized": "2024-08-23",
                "source_field": "manual",
                "confidence": 1.0,
                "status": "validated",
                "attributes": {
                    "property_scope": "page",
                    "property_type": "date",
                },
                "custom_label": "Première publication",
                "property_key": "Première publication",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, _ = build_export_graph(workspace)

        person = next(
            node for node in nodes if node.id == "curated-entity-person-1"
        )
        # Explicitly attaching a page fact to an entity (the "rattacher à une
        # entité" control) surfaces it on that entity, not just the page.
        self.assertEqual(
            person.properties["Première publication"], "2024-08-23"
        )
        self.assertEqual(
            person.properties[PROPERTY_TYPE_OVERRIDES_KEY]["Première publication"],
            "date",
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
            self.assertEqual(manifest["schema_version"], 4)
            self.assertEqual(
                manifest["compatibility"]["source_version_observed"],
                "2.41.9",
            )
            self.assertEqual(
                manifest["compatibility"]["tagset_count"],
                26,
            )
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
        self.assertIn("Personne", result["tags"])
        self.assertNotIn("person", result["tags"])
        self.assertLess(
            result["tags"].index("Personne"),
            result["tags"].index("Site web"),
        )
        self.assertEqual(result["visual"]["icon"], "User")
        self.assertEqual(result["visual"]["shape"], "circle")
        self.assertEqual(result["visual"]["color"], "#3b82f6")
        settings = dossier["dossier"]["settings"]
        suggested_properties = {
            item["key"]: item["type"]
            for item in settings["suggestedProperties"]
        }
        self.assertEqual(suggested_properties["Date de naissance"], "date")
        self.assertEqual(suggested_properties["URL"], "link")
        self.assertIn(
            {"key": "Date de naissance", "type": "date"},
            settings["tagPropertyAssociations"]["Personne"],
        )
        self.assertIn(
            {"key": "URL", "type": "link"},
            settings["tagPropertyAssociations"]["Site web"],
        )
        investigation = next(
            element
            for element in dossier["elements"]
            if element["tags"][0] == "Investigation"
        )
        self.assertEqual(investigation["label"], "Case One")
        self.assertEqual(investigation["position"], {"x": 0.0, "y": 0.0})
        self.assertEqual(investigation["visual"]["shape"], "hexagon")
        self.assertEqual(investigation["visual"]["size"], "large")
        self.assertEqual(investigation["visual"]["icon"], "Network")
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
        self.assertNotIn(
            "example.org",
            {element["label"] for element in dossier["elements"]},
        )
        email = next(
            element
            for element in dossier["elements"]
            if element["label"] == "jane@example.org"
        )
        email_properties = {
            item["key"]: item["value"]
            for item in email["properties"]
        }
        self.assertEqual(email["tags"][0], "Email")
        self.assertEqual(email["visual"]["icon"], "Mail")
        self.assertEqual(
            email_properties["Adresse"],
            "jane@example.org",
        )
        self.assertNotIn("Attributes", email_properties)
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
        self.assertNotIn("Type Synthesix", properties)

    def test_curated_entity_omits_internal_and_source_count_properties(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace, Path(temp_dir) / "export"
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        person = next(
            element
            for element in dossier["elements"]
            if element["label"] == "Jane Doe"
        )
        keys = {item["key"] for item in person["properties"]}
        self.assertNotIn("Type Synthesix", keys)
        self.assertNotIn("Sources liées", keys)

    def test_include_page_archives_option_controls_document_assets(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            capture_dir = evidence_dir / "capture-1"
            capture_dir.mkdir(parents=True)
            (capture_dir / "page.html").write_bytes(b"<html></html>")
            (capture_dir / "capture.png").write_bytes(b"png-data")
            workspace["evidence"][0]["artifacts"] = [
                {
                    "id": "artifact-html",
                    "artifact_type": "html",
                    "file_path": (capture_dir / "page.html")
                    .relative_to(base_dir)
                    .as_posix(),
                    "mime_type": "text/html",
                    "sha256": hashlib.sha256(b"<html></html>").hexdigest(),
                    "byte_size": len(b"<html></html>"),
                },
                {
                    "id": "artifact-png",
                    "artifact_type": "png",
                    "file_path": (capture_dir / "capture.png")
                    .relative_to(base_dir)
                    .as_posix(),
                    "mime_type": "image/png",
                    "sha256": hashlib.sha256(b"png-data").hexdigest(),
                    "byte_size": len(b"png-data"),
                },
            ]

            default_export = export_zeroneurone_bundle(
                workspace,
                base_dir / "export-default",
                include_evidence=True,
                base_dir=base_dir,
                asset_root=evidence_dir,
            )
            full_export = export_zeroneurone_bundle(
                workspace,
                base_dir / "export-full",
                include_evidence=True,
                include_page_archives=True,
                base_dir=base_dir,
                asset_root=evidence_dir,
            )

        # HTML/MHTML/text archives are bulky and excluded by default; the
        # screenshot is always kept.
        self.assertEqual(default_export.asset_count, 1)
        self.assertEqual(full_export.asset_count, 2)

    def test_curated_entities_replace_source_and_fact_nodes(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "company-1",
                "label": "ACME SAS",
                "notes": "Selected company",
                "tags": ["Entreprise"],
                "properties": {"Forme juridique": "SAS"},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-siret",
                "result_id": "result-1",
                "entity_type": "siret",
                "value_original": "732 829 320 00074",
                "value_normalized": "73282932000074",
                "source_field": "description",
                "source_text": "SIRET 732 829 320 00074",
                "confidence": 0.99,
                "status": "validated",
                "investigation_entity_id": "company-1",
                "property_key": "SIRET",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, edges = build_export_graph(
            workspace,
            include_evidence=True,
        )

        # No project root node and no separate evidence node: entities stand on
        # their own, the source URL is its own node.
        self.assertEqual(
            {node.label for node in nodes},
            {"ACME SAS", "https://example.org/profile"},
        )
        self.assertEqual({edge.label for edge in edges}, {"Trouvé sur"})
        company = next(node for node in nodes if node.label == "ACME SAS")
        self.assertEqual(company.tags[0], "Entreprise")
        self.assertEqual(company.properties["SIRET"], "732 829 320 00074")
        self.assertEqual(company.properties["Forme juridique"], "SAS")
        self.assertNotIn("Sources", company.properties)
        source = next(
            node for node in nodes
            if node.label == "https://example.org/profile"
        )
        self.assertIn("Site web", source.tags)
        found_on = next(edge for edge in edges if edge.label == "Trouvé sur")
        self.assertEqual(found_on.source_label, "ACME SAS")
        self.assertEqual(found_on.target_label, "https://example.org/profile")

    def test_curated_image_evidence_merges_onto_its_page_node(self):
        # A screenshot that isn't cited by any specific property no longer
        # gets its own "Illustré par" node beside the page — it merges onto
        # the page ("Site web") node it was captured from, one node per
        # page instead of two that only duplicated each other.
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            artifact_path = evidence_dir / "capture-1" / "capture.png"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_bytes(b"png-data")
            workspace["evidence"][0]["result_id"] = "result-1"
            workspace["evidence"][0]["source_url"] = (
                "https://example.org/profile"
            )
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

        self.assertEqual(exported.asset_count, 1)
        labels = {element["label"] for element in dossier["elements"]}
        # No project-root node, and no standalone "Profile header" evidence
        # node either — just the entity and the page it was found on.
        self.assertNotIn("Case One", labels)
        self.assertNotIn("Profile header", labels)
        self.assertEqual(
            labels, {"Jane Doe", "https://example.org/profile"}
        )
        person = next(
            element
            for element in dossier["elements"]
            if element["label"] == "Jane Doe"
        )
        page = next(
            element
            for element in dossier["elements"]
            if element["label"] == "https://example.org/profile"
        )
        # The evidence file is attached to the page, not the entity.
        self.assertEqual(person["assetIds"], [])
        self.assertEqual(len(page["assetIds"]), 1)
        link = next(
            link
            for link in dossier["links"]
            if link["fromId"] == person["id"] and link["toId"] == page["id"]
        )
        self.assertEqual(link["label"], "Trouvé sur")
        prop_keys = {item["key"] for item in person["properties"]}
        self.assertNotIn("ID Synthesix", prop_keys)
        self.assertNotIn("Manifeste Synthesix", prop_keys)

    def test_fact_cited_screenshot_surfaces_on_the_page_node(self):
        # A property value attached via "attach evidence to property"
        # (attributes.source_capture_id) must surface its screenshot even
        # when the capture's page was never added to the entity's
        # linked_result_ids — that page-level list only covers a coarser,
        # separate "found on this page" relationship. The screenshot itself
        # merges onto the page node rather than becoming its own node.
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            capture_dir = evidence_dir / "capture-plate"
            capture_dir.mkdir(parents=True)
            artifact_path = capture_dir / "capture.png"
            artifact_path.write_bytes(b"plate-data")
            workspace["evidence"].append(
                {
                    "id": "capture-plate",
                    "result_id": "result-1",
                    "name": "WW-246-FA",
                    "capture_kind": "screenshot",
                    "capture_scope": "viewport",
                    "status": "completed",
                    "source_url": "https://example.org/profile",
                    "manifest_path": "data/evidence/capture-plate/manifest.json",
                    "captured_at": "2026-06-12T10:06:00+00:00",
                    "error": "",
                    "artifacts": [
                        {
                            "id": "artifact-plate",
                            "file_path": artifact_path.relative_to(
                                base_dir
                            ).as_posix(),
                            "mime_type": "image/png",
                            "sha256": hashlib.sha256(b"plate-data").hexdigest(),
                            "byte_size": len(b"plate-data"),
                        }
                    ],
                }
            )
            workspace["entities"].append(
                {
                    "id": "entity-plate",
                    "result_id": "result-1",
                    "investigation_entity_id": "person-1",
                    "entity_type": "other",
                    "value_original": "WW-246-FA",
                    "value_normalized": "WW-246-FA",
                    "source_field": "manual",
                    "confidence": 1.0,
                    "status": "validated",
                    "attributes": {"source_capture_id": "capture-plate"},
                    "property_key": "Capture voiture",
                    "last_observed_at": "2026-06-12T10:06:00+00:00",
                }
            )
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

        by_label = {element["label"]: element for element in dossier["elements"]}
        person = by_label["Jane Doe"]
        # No standalone "WW-246-FA" evidence node: the screenshot merges onto
        # the page it was captured from.
        self.assertNotIn("WW-246-FA", by_label)
        page = by_label["https://example.org/profile"]
        self.assertEqual(len(page["assetIds"]), 1)
        link = next(
            link
            for link in dossier["links"]
            if link["fromId"] == person["id"] and link["toId"] == page["id"]
        )
        self.assertEqual(link["label"], "Capture voiture")
        # The generic "Trouvé sur" edge is skipped in favour of the more
        # specific property-labelled one above (no duplicate parallel edge).
        self.assertNotIn(
            "Trouvé sur",
            {
                l["label"]
                for l in dossier["links"]
                if l["fromId"] == person["id"] and l["toId"] == page["id"]
            },
        )
        # Still readable as plain text too: the property itself is untouched.
        prop = {item["key"]: item["value"] for item in person["properties"]}
        self.assertEqual(prop["Capture voiture"], "WW-246-FA")

    def test_page_surfaces_with_its_notes_when_only_linked_through_a_fact(self):
        # Reported gap: an entity attached to a page only through an
        # extracted fact (investigation_entity_id), with linked_result_ids
        # left empty, shows the page under "Entités utilisant cette page" in
        # the Synthesix rail (_page_linked_entities_markup checks both
        # mechanisms) but the curated export only looked at
        # linked_result_ids — so the page's own "Site web" node, and the
        # analyst notes it carries, never made it into the ZeroNeurone
        # dossier.
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-plate",
                "result_id": "result-1",
                "investigation_entity_id": "person-1",
                "entity_type": "other",
                "value_original": "KTT-RW98",
                "value_normalized": "KTT-RW98",
                "source_field": "manual",
                "confidence": 1.0,
                "status": "validated",
                "attributes": {},
                "property_key": "Plaque",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, edges = build_export_graph(workspace)

        source = next(node for node in nodes if node.id == "result-result-1")
        self.assertEqual(source.notes, "Reviewed profile.")
        self.assertIn("Site web", source.tags)
        found_on = next(edge for edge in edges if edge.label == "Trouvé sur")
        self.assertEqual(found_on.source_label, "Jane Doe")
        self.assertEqual(found_on.target_label, "https://example.org/profile")

    def test_curated_layout_merges_several_screenshots_onto_one_page_node(self):
        # Several screenshots captured from the same page (e.g. 8 different
        # license plates spotted on one profile) used to fan out as 8
        # separate "Illustré par" nodes beside the entity. They now merge
        # onto the single page node as multiple assets — one node, not one
        # per screenshot.
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            workspace["evidence"] = []
            for index in range(6):
                capture_dir = evidence_dir / f"capture-{index}"
                capture_dir.mkdir(parents=True)
                artifact_path = capture_dir / "capture.png"
                artifact_path.write_bytes(f"png-{index}".encode())
                workspace["evidence"].append(
                    {
                        "id": f"capture-{index}",
                        "result_id": "result-1",
                        "name": f"Capture {index}",
                        "capture_kind": "screenshot",
                        "capture_scope": "viewport",
                        "status": "completed",
                        "source_url": "https://example.org/profile",
                        "manifest_path": f"data/evidence/capture-{index}/manifest.json",
                        "captured_at": "2026-06-12T10:04:00+00:00",
                        "error": "",
                        "artifacts": [
                            {
                                "id": f"artifact-{index}",
                                "file_path": artifact_path.relative_to(
                                    base_dir
                                ).as_posix(),
                                "mime_type": "image/png",
                                "sha256": hashlib.sha256(
                                    f"png-{index}".encode()
                                ).hexdigest(),
                                "byte_size": len(f"png-{index}".encode()),
                            }
                        ],
                    }
                )
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

        self.assertEqual(exported.asset_count, 6)
        by_label = {element["label"]: element for element in dossier["elements"]}
        for index in range(6):
            self.assertNotIn(f"Capture {index}", by_label)
        person = by_label["Jane Doe"]
        page = by_label["https://example.org/profile"]
        self.assertEqual(len(page["assetIds"]), 6)
        # Still beside the entity, not dumped into a far-away "leftover"
        # column: same neighbourhood on the x axis.
        self.assertGreater(page["position"]["x"], person["position"]["x"])
        self.assertLess(page["position"]["x"] - person["position"]["x"], 620.0)

    def test_curated_layout_places_sources_beside_entities(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        by_label = {element["label"]: element for element in dossier["elements"]}
        person = by_label["Jane Doe"]
        source = by_label["https://example.org/profile"]
        # Entity on the left, its source URL aligned to the right on the row.
        self.assertEqual(person["position"]["x"], 0.0)
        self.assertGreater(source["position"]["x"], person["position"]["x"])
        self.assertEqual(source["position"]["y"], person["position"]["y"])

    def test_curated_layout_groups_related_entities_and_avoids_one_column(self):
        workspace = export_workspace()
        # Four unrelated entities plus one relation edge (Jean -> Société A):
        # the old layout stacked everyone in a single column, so the "PDG de"
        # edge would cut across every unrelated entity in between. The new
        # layout should at least spread entities across more than one column.
        workspace["graph_entities"] = [
            {
                "id": "a",
                "label": "Jean",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
                "relations": [
                    {
                        "id": "r1",
                        "target_entity_id": "b",
                        "target_label": "Société A",
                        "label": "PDG de",
                    }
                ],
            },
            {
                "id": "b",
                "label": "Société A",
                "tags": ["Entreprise"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            },
            {
                "id": "c",
                "label": "Autre entité 1",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            },
            {
                "id": "d",
                "label": "Autre entité 2",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            },
        ]
        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace, Path(temp_dir) / "export"
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        by_label = {element["label"]: element for element in dossier["elements"]}
        xs = {
            by_label[label]["position"]["x"]
            for label in ("Jean", "Société A", "Autre entité 1", "Autre entité 2")
        }
        self.assertGreater(len(xs), 1)
        # Related entities (linked by "PDG de") land on the same row.
        self.assertEqual(
            by_label["Jean"]["position"]["y"],
            by_label["Société A"]["position"]["y"],
        )

    def test_date_property_value_normalized_to_iso(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "p1",
                "label": "Jane",
                "tags": ["Personne"],
                "properties": {"Date de naissance": "19/10/2003"},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace, Path(temp_dir) / "export"
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        person = next(
            element
            for element in dossier["elements"]
            if element["label"] == "Jane"
        )
        prop = next(
            item
            for item in person["properties"]
            if item["key"] == "Date de naissance"
        )
        self.assertEqual(prop["type"], "date")
        self.assertEqual(prop["value"], "2003-10-19")

    def test_unparseable_date_stays_as_property(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "person-1",
                "label": "Jane Doe",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-bday",
                "result_id": "result-1",
                "entity_type": "date",
                "value_original": "5 mars 1983",
                "value_normalized": "5 mars 1983",
                "status": "validated",
                "investigation_entity_id": "person-1",
                "property_key": "Date de naissance",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, _ = build_export_graph(workspace)

        person = next(node for node in nodes if node.label == "Jane Doe")
        # A date that cannot become a timeline event must not vanish.
        self.assertEqual(
            person.properties["Date de naissance"], "5 mars 1983"
        )

    def test_entity_relations_become_labelled_edges(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "a",
                "label": "Jean",
                "tags": ["Personne"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
                "relations": [
                    {
                        "id": "r1",
                        "target_entity_id": "b",
                        "target_label": "Société A",
                        "label": "PDG de",
                    }
                ],
            },
            {
                "id": "b",
                "label": "Société A",
                "tags": ["Entreprise"],
                "properties": {},
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            },
        ]

        _, edges = build_export_graph(workspace)

        edge = next(edge for edge in edges if edge.label == "PDG de")
        self.assertEqual(edge.source_label, "Jean")
        self.assertEqual(edge.target_label, "Société A")

    def test_date_candidates_default_to_event_elements(self):
        workspace = export_workspace()
        workspace["entities"].append(
            {
                "id": "entity-date",
                "result_id": "result-1",
                "entity_type": "date",
                "value_original": "15/06/2026",
                "value_normalized": "2026-06-15",
                "source_field": "description",
                "source_text": "Événement le 15/06/2026",
                "confidence": 0.95,
                "attributes": {"interpretations": ["2026-06-15"]},
                "status": "validated",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, _ = build_export_graph(workspace)

        date_node = next(node for node in nodes if node.label == "15/06/2026")
        self.assertEqual(date_node.tags[0], "Événement")
        self.assertEqual(date_node.properties["Date/heure"], "2026-06-15")
        self.assertEqual(len(date_node.events), 1)
        self.assertEqual(
            date_node.events[0]["date"],
            "2026-06-15T00:00:00Z",
        )
        self.assertEqual(
            date_node.events[0]["dateEnd"],
            "2026-06-15T00:00:00Z",
        )

        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        native_date = next(
            element
            for element in dossier["elements"]
            if element["label"] == "15/06/2026"
        )
        self.assertEqual(native_date["events"], list(date_node.events))

    def test_date_property_becomes_event_on_curated_entity(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "company-1",
                "label": "ACME SAS",
                "tags": ["Entreprise"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-date",
                "result_id": "result-1",
                "entity_type": "date",
                "custom_label": "Création",
                "value_original": "15/06/2026",
                "value_normalized": "2026-06-15",
                "source_field": "description",
                "source_text": "Créée le 15/06/2026",
                "confidence": 0.95,
                "attributes": {"interpretations": ["2026-06-15"]},
                "status": "validated",
                "investigation_entity_id": "company-1",
                "property_key": "Date de création",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, _ = build_export_graph(workspace)

        company = next(node for node in nodes if node.label == "ACME SAS")
        self.assertEqual(len(company.events), 1)
        self.assertEqual(company.events[0]["label"], "Création")
        self.assertEqual(
            company.events[0]["source"],
            "https://example.org/profile",
        )
        self.assertNotIn("Date de création", company.properties)

    def test_coordinate_property_becomes_native_curated_location(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "company-1",
                "label": "ACME SAS",
                "tags": ["Entreprise"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-coordinates",
                "result_id": "result-1",
                "entity_type": "other",
                "suggested_type": "other",
                "tags": ["Coordonnées"],
                "value_original": "48.8566, 2.3522",
                "value_normalized": "48.856600,2.352200",
                "source_field": "description",
                "source_text": "Siège : 48.8566, 2.3522",
                "confidence": 0.9,
                "attributes": {
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                },
                "status": "validated",
                "investigation_entity_id": "company-1",
                "property_key": "Coordonnées",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        nodes, _ = build_export_graph(workspace)

        company = next(node for node in nodes if node.label == "ACME SAS")
        self.assertEqual(company.latitude, 48.8566)
        self.assertEqual(company.longitude, 2.3522)
        self.assertNotIn("Coordonnées", company.properties)

        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        native_company = next(
            element
            for element in dossier["elements"]
            if element["label"] == "ACME SAS"
        )
        self.assertEqual(
            native_company["geo"],
            {
                "type": "point",
                "lat": 48.8566,
                "lng": 2.3522,
            },
        )

    def test_extracted_property_type_overrides_export_heuristic(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "company-1",
                "label": "ACME SAS",
                "tags": ["Entreprise"],
                "properties": {},
                "linked_result_ids": ["result-1"],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]
        workspace["entities"].append(
            {
                "id": "entity-score",
                "result_id": "result-1",
                "entity_type": "other",
                "value_original": "42",
                "value_normalized": "42",
                "source_field": "description",
                "source_text": "Score 42",
                "confidence": 0.9,
                "attributes": {"property_type": "number"},
                "status": "validated",
                "investigation_entity_id": "company-1",
                "property_key": "Score maison",
                "last_observed_at": "2026-06-12T10:02:00+00:00",
            }
        )

        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        company = next(
            element
            for element in dossier["elements"]
            if element["label"] == "ACME SAS"
        )
        score = next(
            item for item in company["properties"] if item["key"] == "Score maison"
        )
        self.assertEqual(score["type"], "number")
        self.assertNotIn(
            "_synthesix_property_types",
            {item["key"] for item in company["properties"]},
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

    def test_company_alias_uses_enterprise_tagset(self):
        workspace = export_workspace()
        workspace["results"][0]["tags"] = ["Company", "Offshore"]

        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        result = next(
            element
            for element in dossier["elements"]
            if element["label"] == "https://example.org/profile"
        )
        self.assertEqual(
            result["tags"][:3],
            ["Entreprise", "Offshore", "Site web"],
        )
        self.assertEqual(result["visual"]["icon"], "Building2")
        self.assertEqual(result["visual"]["shape"], "square")
        self.assertEqual(result["visual"]["color"], "#8b5cf6")

    def test_native_entity_properties_match_tagset_fields(self):
        workspace = export_workspace()
        workspace["entities"].extend(
            [
                {
                    "id": "entity-address",
                    "result_id": "result-1",
                    "entity_type": "address",
                    "value_original": "10 rue de la Paix, 75002 Paris",
                    "value_normalized": "10 rue de la paix 75002 paris",
                    "source_field": "archive_text:capture-1",
                    "source_text": "Siège: 10 rue de la Paix, 75002 Paris.",
                    "confidence": 0.82,
                    "confidence_reasons": ["Postal code and locality"],
                    "attributes": {
                        "postal_code": "75002",
                        "locality": "Paris",
                        "country": "FR",
                    },
                    "status": "validated",
                    "last_observed_at": "2026-06-12T10:02:00+00:00",
                },
                {
                    "id": "entity-siret",
                    "result_id": "result-1",
                    "entity_type": "siret",
                    "tags": ["Company", "custom entity tag"],
                    "value_original": "732 829 320 00074",
                    "value_normalized": "73282932000074",
                    "source_field": "description",
                    "source_text": "SIRET 732 829 320 00074",
                    "confidence": 0.99,
                    "attributes": {"siren": "732829320"},
                    "status": "validated",
                    "last_observed_at": "2026-06-12T10:02:00+00:00",
                },
            ]
        )

        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        address = next(
            element
            for element in dossier["elements"]
            if element["label"] == "10 rue de la Paix, 75002 Paris"
        )
        address_properties = {
            item["key"]: item["value"]
            for item in address["properties"]
        }
        self.assertEqual(address["tags"][0], "Lieu")
        self.assertEqual(address["visual"]["icon"], "MapPin")
        self.assertEqual(address_properties["Code postal"], "75002")
        self.assertEqual(address_properties["Ville"], "Paris")
        self.assertEqual(address_properties["Pays"], "FR")

        siret = next(
            element
            for element in dossier["elements"]
            if element["label"] == "732 829 320 00074"
        )
        siret_properties = {
            item["key"]: item["value"]
            for item in siret["properties"]
        }
        self.assertEqual(siret_properties["SIRET"], "73282932000074")
        self.assertEqual(siret_properties["SIREN"], "732829320")
        self.assertEqual(
            siret["tags"][:2],
            ["Entreprise", "custom entity tag"],
        )
        self.assertEqual(siret["visual"]["icon"], "Building2")

    def test_native_dossier_includes_lawyer_default_property_settings(self):
        workspace = export_workspace()
        workspace["graph_entities"] = [
            {
                "id": "lawyer-1",
                "label": "Me Dupont",
                "notes": "",
                "tags": ["Avocat"],
                "properties": {
                    "Barreau": "",
                    "Spécialité": "",
                    "Cabinet": "",
                    "Date d'inscription": "",
                },
                "linked_result_ids": [],
                "updated_at": "2026-06-12T10:05:00+00:00",
            }
        ]

        with TemporaryDirectory() as temp_dir:
            exported = export_zeroneurone_bundle(
                workspace,
                Path(temp_dir) / "export",
            )
            dossier = json.loads(
                exported.dossier_path.read_text(encoding="utf-8")
            )

        settings = dossier["dossier"]["settings"]
        self.assertIn("Avocat", settings["existingTags"])
        self.assertEqual(
            settings["tagPropertyAssociations"]["Avocat"],
            [
                {"key": "Barreau", "type": "text"},
                {"key": "Spécialité", "type": "text"},
                {"key": "Cabinet", "type": "text"},
                {"key": "Date d'inscription", "type": "date"},
            ],
        )
        lawyer = next(
            element
            for element in dossier["elements"]
            if element["label"] == "Me Dupont"
        )
        lawyer_properties = {
            item["key"]: item["value"]
            for item in lawyer["properties"]
        }
        self.assertNotIn("Barreau", lawyer_properties)
        self.assertNotIn("Spécialité", lawyer_properties)
        self.assertNotIn("Cabinet", lawyer_properties)
        self.assertNotIn("Date d'inscription", lawyer_properties)


if __name__ == "__main__":
    unittest.main()
