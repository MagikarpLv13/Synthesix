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

    def test_curated_evidence_attaches_as_entity_files(self):
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
        # No standalone evidence node and no project-root node.
        self.assertNotIn("Profile header", labels)
        self.assertNotIn("Case One", labels)
        person = next(
            element
            for element in dossier["elements"]
            if element["label"] == "Jane Doe"
        )
        # The evidence file is attached to the entity it supports.
        self.assertEqual(len(person["assetIds"]), 1)
        prop_keys = {item["key"] for item in person["properties"]}
        self.assertNotIn("ID Synthesix", prop_keys)
        self.assertNotIn("Manifeste Synthesix", prop_keys)

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
