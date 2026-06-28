from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid4, uuid5
from xml.etree import ElementTree

from exports.zeroneurone_tagsets import (
    ZERONEURONE_TAGSETS,
    canonical_zeroneurone_tag,
    zeroneurone_property_type,
    zeroneurone_tagset_suggested_properties,
    zeroneurone_tagset_visual,
)


EXPORT_SCHEMA_NAME = "synthesix-zeroneurone"
EXPORT_SCHEMA_VERSION = 4
ZERONEURONE_DOSSIER_VERSION = "1.1.0"
ZERONEURONE_IMPORT_DOCUMENTATION = (
    "https://doc.zeroneurone.com/fr/import-export/import/"
)
GRAPHML_NAMESPACE = "http://graphml.graphdrawing.org/xmlns"


@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str
    notes: str = ""
    tags: tuple[str, ...] = ()
    confidence: float | None = None
    source: str = ""
    date: str = ""
    latitude: float | None = None
    longitude: float | None = None
    events: tuple[Mapping[str, object], ...] = ()
    properties: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    id: str
    source_id: str
    target_id: str
    label: str
    source_label: str
    target_label: str
    notes: str = ""
    tags: tuple[str, ...] = ("observed",)
    confidence: float | None = None
    date: str = ""
    properties: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ZeroNeuroneExport:
    output_dir: Path
    archive_path: Path
    dossier_path: Path
    graphml_path: Path
    csv_path: Path
    nodes_csv_path: Path
    edges_csv_path: Path
    manifest_path: Path
    node_count: int
    edge_count: int
    asset_count: int
    generated_at: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _stable_id(kind: str, *parts: object) -> str:
    value = ":".join(str(part) for part in parts)
    return f"{kind}-{uuid5(NAMESPACE_URL, f'synthesix:{kind}:{value}')}"


def _native_uuid(kind: str, *parts: object) -> str:
    value = ":".join(str(part) for part in parts)
    return str(uuid5(NAMESPACE_URL, f"synthesix:{kind}:{value}"))


def _date_only(value: object) -> str:
    return str(value or "").strip()[:10]


def _domain_from_url(value: object) -> str:
    try:
        return str(urlsplit(str(value or "")).hostname or "").casefold()
    except ValueError:
        return ""


def _tags(*values: object) -> tuple[str, ...]:
    result = []
    seen = set()
    for value in values:
        candidates = value if isinstance(value, (list, tuple, set)) else (value,)
        for candidate in candidates:
            text = str(candidate or "").strip()
            text = canonical_zeroneurone_tag(text)
            key = text.casefold()
            if not text or key in seen:
                continue
            seen.add(key)
            result.append(text)
    return tuple(result)


def _is_coordinate_entity(entity: Mapping) -> bool:
    if str(entity.get("entity_type", "") or "") == "coordinates":
        return True
    if str(entity.get("suggested_type", "") or "") == "coordinates":
        return True
    tags = entity.get("tags", ())
    if isinstance(tags, str):
        tags = tags.split(",")
    elif not isinstance(tags, (list, tuple, set)):
        tags = ()
    return any(
        str(tag or "").strip().casefold()
        in {"coordonnées", "coordinates"}
        for tag in tags
    )


def _coordinates(entity: Mapping) -> tuple[float | None, float | None]:
    if not _is_coordinate_entity(entity):
        return None, None
    attributes = entity.get("attributes", {})
    if not isinstance(attributes, Mapping):
        attributes = {}
    try:
        latitude = float(attributes.get("latitude"))
        longitude = float(attributes.get("longitude"))
    except (TypeError, ValueError):
        value = str(
            entity.get("value_normalized")
            or entity.get("value_original")
            or ""
        )
        try:
            latitude_text, longitude_text = value.replace(";", ",").split(
                ",",
                1,
            )
            latitude = float(latitude_text)
            longitude = float(longitude_text)
        except (TypeError, ValueError):
            return None, None
    if (
        not math.isfinite(latitude)
        or not math.isfinite(longitude)
        or not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
    ):
        return None, None
    return latitude, longitude


def _best_coordinate_fact(
    facts: Iterable[Mapping],
) -> Mapping | None:
    selected = None
    selected_confidence = -1.0
    for fact in facts:
        latitude, longitude = _coordinates(fact)
        if latitude is None or longitude is None:
            continue
        try:
            confidence = float(fact.get("confidence", 0) or 0)
        except (TypeError, ValueError):
            confidence = 0.0
        if selected is None or confidence > selected_confidence:
            selected = fact
            selected_confidence = confidence
    return selected


def _entity_node_id(investigation_id: str, entity: Mapping) -> str:
    entity_id = str(entity.get("id", "") or "")
    if entity_id:
        return _stable_id("entity", investigation_id, entity_id)
    return _stable_id(
        "entity",
        investigation_id,
        entity.get("suggested_type") or entity.get("entity_type", ""),
        entity.get("value_normalized", ""),
    )


def _entity_tags(entity_type: str) -> tuple[str, ...]:
    return {
        "email": ("Email",),
        "phone": ("Téléphone",),
        "url": ("Site web",),
        "domain": ("Site web",),
        "handle": ("Compte en ligne",),
        "ipv4": ("Site web",),
        "ipv6": ("Site web",),
        "coordinates": ("Lieu",),
        "identifier": ("Identifiant",),
        "address": ("Lieu",),
        "vat_number": ("Numéro de TVA",),
        "siret": ("SIRET",),
        "siren": ("SIREN",),
        "date": ("Événement",),
        "person": ("Personne",),
        "organization": ("Entreprise",),
        "place": ("Lieu",),
        "event": ("Événement",),
        "product": ("Produit ou service",),
        "other": ("Entité",),
    }.get(entity_type, ("Entité",))


def _entity_tagset_properties(entity: Mapping) -> dict[str, object]:
    entity_type = str(entity.get("entity_type", "") or "")
    value = str(entity.get("value_normalized", "") or "")
    original = str(entity.get("value_original", "") or value)
    attributes = entity.get("attributes", {})
    if not isinstance(attributes, Mapping):
        attributes = {}

    properties: dict[str, object] = {}
    if entity_type == "email":
        properties["Adresse"] = original
    elif entity_type == "phone":
        properties["Numéro"] = original
    elif entity_type == "url":
        properties["URL"] = value
        properties["Domaine"] = _domain_from_url(value)
    elif entity_type == "domain":
        properties["Domaine"] = value
    elif entity_type == "handle":
        properties["Username"] = original
    elif entity_type == "address":
        properties["Adresse"] = original
        properties["Code postal"] = attributes.get("postal_code", "")
        properties["Ville"] = attributes.get("locality", "")
        properties["Pays"] = attributes.get("country", "")
    elif entity_type == "siren":
        properties["SIREN"] = value
    elif entity_type == "siret":
        properties["SIRET"] = value
        properties["SIREN"] = attributes.get("siren", value[:9])
    elif entity_type == "vat_number":
        properties["Numéro de TVA"] = value
        properties["SIREN"] = attributes.get("siren", "")
        properties["Pays"] = attributes.get("country", "")
    elif entity_type == "date":
        interpretations = attributes.get("interpretations", [])
        properties["Date/heure"] = (
            interpretations[0]
            if isinstance(interpretations, list) and len(interpretations) == 1
            else original
        )
        properties["Date ambiguë"] = bool(attributes.get("ambiguous", False))
    elif entity_type == "coordinates":
        properties["Latitude"] = attributes.get("latitude", "")
        properties["Longitude"] = attributes.get("longitude", "")
    return {
        key: value
        for key, value in properties.items()
        if value not in ("", None)
    }


def _default_property_key(entity: Mapping) -> str:
    return {
        "email": "Email",
        "phone": "Téléphone",
        "url": "URL",
        "domain": "Domaine",
        "handle": "Compte en ligne",
        "ipv4": "IP",
        "ipv6": "IP",
        "coordinates": "Coordonnées",
        "identifier": "Identifiant",
        "address": "Adresse",
        "vat_number": "Numéro de TVA",
        "siret": "SIRET",
        "siren": "SIREN",
        "date": "Date/heure",
        "person": "Personne",
        "organization": "Entreprise",
        "place": "Lieu",
        "event": "Événement",
        "product": "Produit ou service",
        "other": "Information",
    }.get(str(entity.get("entity_type", "") or ""), "Information")


def _native_event_date(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return f"{text}T00:00:00Z"
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return ""
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _entity_events(
    entity: Mapping,
    *,
    source: str = "",
) -> tuple[Mapping[str, object], ...]:
    if str(entity.get("entity_type", "") or "") != "date":
        return ()
    attributes = entity.get("attributes", {})
    if not isinstance(attributes, Mapping):
        attributes = {}
    interpretations = attributes.get("interpretations", [])
    candidates = (
        interpretations
        if isinstance(interpretations, list) and interpretations
        else [
            entity.get("value_normalized")
            or entity.get("value_original")
        ]
    )
    result = []
    seen = set()
    for candidate in candidates:
        event_date = _native_event_date(candidate)
        if not event_date or event_date in seen:
            continue
        seen.add(event_date)
        entity_id = str(entity.get("id", "") or event_date)
        properties = []
        if len(candidates) > 1:
            properties.append(
                {
                    "key": "Interprétation ambiguë",
                    "value": True,
                    "type": "boolean",
                }
            )
        result.append(
            {
                "id": _native_uuid("event", entity_id, event_date),
                "date": event_date,
                "dateEnd": event_date,
                "label": str(
                    entity.get("custom_label")
                    or entity.get("property_key")
                    or "Événement détecté"
                ),
                "description": str(
                    entity.get("source_text", "") or ""
                ),
                "properties": properties,
                "source": source
                or str(entity.get("source_field", "") or ""),
            }
        )
    return tuple(result)


def _first_entity_event_date(entity: Mapping) -> str:
    events = _entity_events(entity)
    if not events:
        return ""
    return str(events[0].get("date", "") or "")


def _append_property(
    properties: dict[str, object],
    key: str,
    value: object,
) -> None:
    property_key = str(key or "").strip()
    property_value = str(value or "").strip()
    if not property_key or not property_value:
        return
    current = str(properties.get(property_key, "") or "")
    values = [item.strip() for item in current.split(";") if item.strip()]
    if property_value not in values:
        values.append(property_value)
    properties[property_key] = "; ".join(values)


def _is_page_scoped_property(entity: Mapping) -> bool:
    attributes = entity.get("attributes", {})
    if not isinstance(attributes, Mapping):
        return False
    return str(attributes.get("property_scope", "") or "") == "page"


def _page_scoped_properties_by_result(
    workspace: Mapping,
    *,
    include_unreviewed: bool = False,
) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for entity in workspace.get("entities", []):
        if not _is_page_scoped_property(entity):
            continue
        if not include_unreviewed and entity.get("status") != "validated":
            continue
        result_id = str(entity.get("result_id", "") or "")
        if not result_id:
            continue
        key = (
            str(entity.get("custom_label", "") or "").strip()
            or str(entity.get("property_key", "") or "").strip()
            or _default_property_key(entity)
        )
        value = entity.get("value_original") or entity.get("value_normalized")
        if key and str(value or "").strip():
            _append_property(grouped.setdefault(result_id, {}), key, value)
    return grouped


def _build_curated_graph(
    workspace: Mapping,
    investigation_node: GraphNode,
    *,
    include_evidence: bool,
) -> tuple[tuple[GraphNode, ...], tuple[GraphEdge, ...]]:
    investigation = workspace.get("investigation", {})
    investigation_id = str(investigation.get("id", "") or "")
    results = {
        str(result.get("id", "") or ""): result
        for result in workspace.get("results", [])
        if str(result.get("id", "") or "")
    }
    facts_by_entity: dict[str, list[Mapping]] = {}
    for entity in workspace.get("entities", []):
        if _is_page_scoped_property(entity):
            continue
        parent_id = str(
            entity.get("investigation_entity_id", "") or ""
        )
        if parent_id and entity.get("status") != "rejected":
            facts_by_entity.setdefault(parent_id, []).append(entity)

    # The investigation/project node is intentionally omitted: entities stand on
    # their own and are linked to their source URLs, not hung off a root.
    nodes: dict[str, GraphNode] = {}
    edges: dict[str, GraphEdge] = {}
    entity_nodes: dict[str, GraphNode] = {}
    linked_entities_by_result: dict[str, list[GraphNode]] = {}
    page_properties_by_result = _page_scoped_properties_by_result(
        workspace,
        include_unreviewed=True,
    )

    for entity in workspace.get("graph_entities", []):
        entity_id = str(entity.get("id", "") or "")
        if not entity_id:
            continue
        linked_result_ids = [
            str(result_id)
            for result_id in entity.get("linked_result_ids", [])
            if str(result_id) in results
        ]
        source_urls = [
            str(results[result_id].get("url", "") or "")
            for result_id in linked_result_ids
            if str(results[result_id].get("url", "") or "")
        ]
        properties: dict[str, object] = {
            "synthesix_id": entity_id,
            "synthesix_type": "curated_entity",
            "linked_source_count": len(linked_result_ids),
        }
        property_type_overrides: dict[str, str] = {}
        manual_properties = entity.get("properties", {})
        if isinstance(manual_properties, Mapping):
            for key, value in manual_properties.items():
                _append_property(properties, str(key), value)
        entity_facts = facts_by_entity.get(entity_id, [])
        coordinate_fact = _best_coordinate_fact(entity_facts)
        latitude, longitude = (
            _coordinates(coordinate_fact)
            if coordinate_fact is not None
            else (None, None)
        )
        for fact in entity_facts:
            # A date becomes a timeline event only when it parses; otherwise keep
            # it as a normal property so it never silently disappears.
            if str(fact.get("entity_type", "") or "") == "date" and _entity_events(
                fact
            ):
                continue
            if fact is coordinate_fact:
                continue
            key = str(fact.get("property_key", "") or "")
            property_key = key or _default_property_key(fact)
            _append_property(
                properties,
                property_key,
                fact.get("value_original")
                or fact.get("value_normalized"),
            )
            attributes = fact.get("attributes", {})
            if isinstance(attributes, Mapping):
                property_type = str(
                    attributes.get("property_type", "") or ""
                ).strip()
                if property_type in PROPERTY_TYPES:
                    property_type_overrides[property_key] = property_type
        # Source URLs are exported as their own "Trouvé sur" entities below,
        # not folded into a Sources property.
        if property_type_overrides:
            properties[PROPERTY_TYPE_OVERRIDES_KEY] = property_type_overrides

        node = GraphNode(
            id=f"curated-entity-{entity_id}",
            label=str(entity.get("label") or entity_id),
            notes=str(entity.get("notes", "") or ""),
            tags=_tags(entity.get("tags", []), "Entité"),
            source=", ".join(dict.fromkeys(source_urls)),
            date=_date_only(entity.get("updated_at")),
            latitude=latitude,
            longitude=longitude,
            events=tuple(
                event
                for fact in entity_facts
                for event in _entity_events(
                    fact,
                    source=(
                        str(
                            results.get(
                                str(fact.get("result_id", "") or ""),
                                {},
                            ).get("url", "")
                            or ""
                        )
                    ),
                )
            ),
            properties=properties,
        )
        nodes[node.id] = node
        entity_nodes[entity_id] = node
        for result_id in linked_result_ids:
            linked_entities_by_result.setdefault(result_id, []).append(node)

    # Evidence is no longer exported as separate nodes: the capture artifacts are
    # attached as files on the entities they support (see _copy_native_assets).

    # Each source URL becomes its own "Site web" entity, linked from the entities
    # it sources via a "Trouvé sur" relationship.
    source_result_ids = set(linked_entities_by_result) | set(
        page_properties_by_result
    )
    for result_id in sorted(source_result_ids):
        result = results.get(result_id)
        if result is None:
            continue
        source_node = GraphNode(
            id=f"result-{result_id}",
            label=str(result.get("url") or result.get("title") or result_id),
            notes=str(result.get("notes", "") or ""),
            tags=_tags(
                result.get("tags", []),
                "Site web",
                result.get("analyst_status", ""),
            ),
            source=", ".join(
                str(source)
                for source in result.get("sources", [])
                if str(source).strip()
            ),
            date=_date_only(result.get("latest_observed_at")),
            properties={
                "synthesix_id": result_id,
                "synthesix_type": "result",
                "url": str(result.get("url", "") or ""),
                "canonical_url": str(result.get("canonical_url", "") or ""),
                "domain": _domain_from_url(
                    result.get("canonical_url") or result.get("url")
                ),
                "title": str(result.get("title", "") or ""),
                **page_properties_by_result.get(result_id, {}),
            },
        )
        nodes[source_node.id] = source_node
        for entity_node in linked_entities_by_result.get(result_id, []):
            found_on = _edge(
                entity_node,
                source_node,
                "Trouvé sur",
                date=source_node.date,
            )
            edges[found_on.id] = found_on

    return tuple(nodes.values()), tuple(edges.values())


def _edge(
    source: GraphNode,
    target: GraphNode,
    label: str,
    *,
    date: str = "",
    notes: str = "",
    confidence: float | None = None,
) -> GraphEdge:
    return GraphEdge(
        id=_stable_id("edge", source.id, label, target.id),
        source_id=source.id,
        target_id=target.id,
        label=label,
        source_label=source.label,
        target_label=target.label,
        notes=notes,
        confidence=confidence,
        date=date,
        properties={"relation_status": "observed"},
    )


def build_export_graph(
    workspace: Mapping,
    *,
    include_evidence: bool = False,
    include_unreviewed: bool = False,
) -> tuple[tuple[GraphNode, ...], tuple[GraphEdge, ...]]:
    investigation = workspace.get("investigation", {})
    investigation_id = str(investigation.get("id", "") or "")
    investigation_node = GraphNode(
        id=f"investigation-{investigation_id}",
        label=str(investigation.get("title") or investigation_id),
        notes=str(investigation.get("description", "") or ""),
        tags=_tags("Investigation", investigation.get("tags", [])),
        date=_date_only(investigation.get("created_at")),
        properties={
            "synthesix_id": investigation_id,
            "synthesix_type": "investigation",
            "reference": str(investigation.get("reference", "") or ""),
            "status": str(investigation.get("status", "") or ""),
        },
    )
    nodes: dict[str, GraphNode] = {investigation_node.id: investigation_node}
    edges: dict[str, GraphEdge] = {}
    if workspace.get("graph_entities"):
        return _build_curated_graph(
            workspace,
            investigation_node,
            include_evidence=include_evidence,
        )
    searches = {
        str(search.get("id", "") or ""): search
        for search in workspace.get("searches", [])
        if str(search.get("id", "") or "")
    }
    page_properties_by_result = _page_scoped_properties_by_result(
        workspace,
        include_unreviewed=include_unreviewed,
    )

    result_nodes: dict[str, GraphNode] = {}
    for result in workspace.get("results", []):
        result_id = str(result.get("id", "") or "")
        if not result_id:
            continue
        properties = {
            "synthesix_id": result_id,
            "synthesix_type": "result",
            "url": str(result.get("url", "") or ""),
            "canonical_url": str(result.get("canonical_url", "") or ""),
            "domain": _domain_from_url(
                result.get("canonical_url") or result.get("url")
            ),
            "title": str(result.get("title", "") or ""),
            "analyst_status": str(
                result.get("analyst_status", "") or ""
            ),
            "favorite": bool(result.get("favorite", False)),
            "first_observed_at": str(
                result.get("first_observed_at", "") or ""
            ),
            "last_observed_at": str(
                result.get("last_observed_at", "") or ""
            ),
            "accessed_at": str(
                result.get("latest_observed_at")
                or result.get("last_observed_at")
                or ""
            ),
        }
        for key, value in page_properties_by_result.get(result_id, {}).items():
            _append_property(properties, key, value)
        result_node = GraphNode(
            id=f"result-{result_id}",
            label=str(
                result.get("url")
                or result.get("title")
                or result_id
            ),
            notes=str(result.get("notes", "") or ""),
            tags=_tags(
                result.get("tags", []),
                "Site web",
                result.get("analyst_status", ""),
            ),
            source=", ".join(
                str(source)
                for source in result.get("sources", [])
                if str(source).strip()
            ),
            date=_date_only(result.get("latest_observed_at")),
            properties=properties,
        )
        nodes[result_node.id] = result_node
        result_nodes[result_id] = result_node
        contains = _edge(
            investigation_node,
            result_node,
            "CONTAINS",
            date=result_node.date,
        )
        edges[contains.id] = contains

        search_id = str(result.get("discovery_search_run_id", "") or "")
        search = searches.get(search_id)
        if search is not None:
            query = (
                search.get("original_query")
                or search.get("parsed_query")
                or search_id
            )
            search_node = GraphNode(
                id=f"search-{search_id}",
                label=f"Search: {query}",
                notes=json.dumps(
                    search.get("filters", {}),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                tags=_tags("Recherche"),
                source=", ".join(
                    str(name).title()
                    for name, enabled in search.get("engines", {}).items()
                    if enabled
                ),
                date=_date_only(search.get("started_at")),
                properties={
                    "synthesix_id": search_id,
                    "synthesix_type": "search",
                    "query": str(query),
                    "report_path": str(search.get("report_path", "") or ""),
                },
            )
            nodes[search_node.id] = search_node
            search_contains = _edge(
                investigation_node,
                search_node,
                "CONTAINS",
                date=search_node.date,
            )
            edges[search_contains.id] = search_contains
            found_by = _edge(
                result_node,
                search_node,
                "FOUND_BY",
                date=result_node.date,
            )
            edges[found_by.id] = found_by

    included_entities = [
        entity
        for entity in workspace.get("entities", [])
        if include_unreviewed or entity.get("status") == "validated"
    ]
    entity_nodes: dict[str, GraphNode] = {}
    for entity in included_entities:
        if _is_page_scoped_property(entity):
            continue
        result_id = str(entity.get("result_id", "") or "")
        result_node = result_nodes.get(result_id)
        if result_node is None:
            continue
        entity_type = str(entity.get("entity_type", "") or "")
        if entity_type in {"url", "domain"}:
            continue
        entity_node_id = _entity_node_id(investigation_id, entity)
        latitude, longitude = _coordinates(entity)
        current = entity_nodes.get(entity_node_id)
        statuses = _tags(
            current.properties.get("review_statuses", "").split(";")
            if current is not None
            else (),
            entity.get("status", ""),
        )
        entity_node = GraphNode(
            id=entity_node_id,
            label=str(
                entity.get("custom_label")
                or entity.get("value_original")
                or entity.get("value_normalized")
                or entity_node_id
            ),
            notes=str(entity.get("source_text", "") or ""),
            tags=_tags(
                entity.get("tags", []),
                _entity_tags(entity_type),
                statuses,
            ),
            confidence=max(
                float(entity.get("confidence", 0) or 0),
                current.confidence or 0 if current is not None else 0,
            ),
            source=str(entity.get("source_field", "") or ""),
            date=(
                _first_entity_event_date(entity)
                if entity_type == "date"
                else _date_only(entity.get("last_observed_at"))
            ),
            latitude=latitude,
            longitude=longitude,
            events=_entity_events(entity),
            properties={
                "synthesix_id": str(entity.get("id", "") or ""),
                "synthesix_type": "entity",
                "entity_type": str(entity.get("entity_type", "") or ""),
                "suggested_type": str(
                    entity.get("suggested_type")
                    or entity.get("entity_type", "")
                    or ""
                ),
                "custom_label": str(entity.get("custom_label", "") or ""),
                "normalized_value": str(
                    entity.get("value_normalized", "") or ""
                ),
                "confidence_reasons": json.dumps(
                    entity.get("confidence_reasons", []),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "attributes": json.dumps(
                    entity.get("attributes", {}),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "review_statuses": ";".join(statuses),
                "url": (
                    str(entity.get("value_normalized", "") or "")
                    if entity.get("entity_type") == "url"
                    else ""
                ),
                "domain": (
                    _domain_from_url(entity.get("value_normalized"))
                    if entity.get("entity_type") == "url"
                    else (
                        str(entity.get("value_normalized", "") or "")
                        if entity.get("entity_type") == "domain"
                        else ""
                    )
                ),
                "accessed_at": str(
                    entity.get("last_observed_at", "") or ""
                ),
                **_entity_tagset_properties(entity),
            },
        )
        entity_nodes[entity_node_id] = entity_node
        nodes[entity_node_id] = entity_node
        mentions = _edge(
            result_node,
            entity_node,
            "MENTIONS",
            date=_date_only(entity.get("last_observed_at")),
            notes=str(entity.get("source_text", "") or ""),
            confidence=float(entity.get("confidence", 0) or 0),
        )
        edges[mentions.id] = mentions

    if include_evidence:
        for capture in workspace.get("evidence", []):
            result_node = result_nodes.get(
                str(capture.get("result_id", "") or "")
            )
            capture_id = str(capture.get("id", "") or "")
            if result_node is None or not capture_id:
                continue
            evidence_node = GraphNode(
                id=f"evidence-{capture_id}",
                label=str(
                    capture.get("name")
                    or capture.get("capture_kind")
                    or capture_id
                ),
                notes=str(capture.get("error", "") or ""),
                tags=_tags(
                    "Preuve",
                    capture.get("capture_kind", ""),
                    capture.get("status", ""),
                ),
                source=str(capture.get("source_url", "") or ""),
                date=_date_only(capture.get("captured_at")),
                properties={
                    "synthesix_id": capture_id,
                    "synthesix_type": "evidence",
                    "manifest_path": str(
                        capture.get("manifest_path", "") or ""
                    ),
                    "capture_scope": str(
                        capture.get("capture_scope", "") or ""
                    ),
                },
            )
            nodes[evidence_node.id] = evidence_node
            captured_as = _edge(
                result_node,
                evidence_node,
                "CAPTURED_AS",
                date=evidence_node.date,
            )
            edges[captured_as.id] = captured_as

    return tuple(nodes.values()), tuple(edges.values())


def _graphml_key_definitions(
    root: ElementTree.Element,
) -> dict[tuple[str, str], str]:
    definitions = {
        ("node", "label"): "string",
        ("node", "notes"): "string",
        ("node", "tags"): "string",
        ("node", "confidence"): "double",
        ("node", "source"): "string",
        ("node", "date"): "string",
        ("node", "latitude"): "double",
        ("node", "longitude"): "double",
        ("node", "properties"): "string",
        ("edge", "label"): "string",
        ("edge", "notes"): "string",
        ("edge", "tags"): "string",
        ("edge", "confidence"): "double",
        ("edge", "date"): "string",
        ("edge", "properties"): "string",
    }
    keys = {}
    for (scope, name), data_type in definitions.items():
        key_id = f"{scope[0]}_{name}"
        ElementTree.SubElement(
            root,
            f"{{{GRAPHML_NAMESPACE}}}key",
            {
                "id": key_id,
                "for": scope,
                "attr.name": name,
                "attr.type": data_type,
            },
        )
        keys[(scope, name)] = key_id
    return keys


def _add_graphml_data(
    parent: ElementTree.Element,
    key_id: str,
    value: object,
) -> None:
    data = ElementTree.SubElement(
        parent,
        f"{{{GRAPHML_NAMESPACE}}}data",
        {"key": key_id},
    )
    data.text = str(value)


def _serializable_properties(properties: Mapping[str, object]) -> dict[str, object]:
    return {
        str(key): value
        for key, value in properties.items()
        if key != PROPERTY_TYPE_OVERRIDES_KEY
        and key not in HIDDEN_NATIVE_PROPERTIES
    }


def _write_graphml(
    path: Path,
    nodes: Iterable[GraphNode],
    edges: Iterable[GraphEdge],
) -> None:
    ElementTree.register_namespace("", GRAPHML_NAMESPACE)
    root = ElementTree.Element(f"{{{GRAPHML_NAMESPACE}}}graphml")
    keys = _graphml_key_definitions(root)
    graph = ElementTree.SubElement(
        root,
        f"{{{GRAPHML_NAMESPACE}}}graph",
        {"id": "synthesix", "edgedefault": "directed"},
    )
    for node in nodes:
        element = ElementTree.SubElement(
            graph,
            f"{{{GRAPHML_NAMESPACE}}}node",
            {"id": node.id},
        )
        values = {
            "label": node.label,
            "notes": node.notes,
            "tags": ";".join(node.tags),
            "source": node.source,
            "date": node.date,
            "properties": json.dumps(
                _serializable_properties(node.properties),
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        if node.confidence is not None:
            values["confidence"] = node.confidence
        if node.latitude is not None:
            values["latitude"] = node.latitude
        if node.longitude is not None:
            values["longitude"] = node.longitude
        for name, value in values.items():
            if value not in {"", None}:
                _add_graphml_data(element, keys[("node", name)], value)

    for edge in edges:
        element = ElementTree.SubElement(
            graph,
            f"{{{GRAPHML_NAMESPACE}}}edge",
            {
                "id": edge.id,
                "source": edge.source_id,
                "target": edge.target_id,
            },
        )
        values = {
            "label": edge.label,
            "notes": edge.notes,
            "tags": ";".join(edge.tags),
            "date": edge.date,
            "properties": json.dumps(
                _serializable_properties(edge.properties),
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        if edge.confidence is not None:
            values["confidence"] = edge.confidence
        for name, value in values.items():
            if value not in {"", None}:
                _add_graphml_data(element, keys[("edge", name)], value)

    ElementTree.ElementTree(root).write(
        path,
        encoding="utf-8",
        xml_declaration=True,
    )


def _write_csv_files(
    output_dir: Path,
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
) -> tuple[Path, Path, Path]:
    nodes_path = output_dir / "nodes.csv"
    edges_path = output_dir / "edges.csv"
    import_path = output_dir / "zeroneurone.csv"

    with nodes_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "label",
                "notes",
                "tags",
                "confidence",
                "source",
                "date",
                "latitude",
                "longitude",
                "properties",
            ],
        )
        writer.writeheader()
        for node in nodes:
            writer.writerow(
                _safe_csv_row({
                    "id": node.id,
                    "label": node.label,
                    "notes": node.notes,
                    "tags": ";".join(node.tags),
                    "confidence": (
                        round(node.confidence * 100, 2)
                        if node.confidence is not None
                        else ""
                    ),
                    "source": node.source,
                    "date": node.date,
                    "latitude": node.latitude
                    if node.latitude is not None
                    else "",
                    "longitude": node.longitude
                    if node.longitude is not None
                    else "",
                    "properties": json.dumps(
                        _serializable_properties(node.properties),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                })
            )

    with edges_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "source_id",
                "target_id",
                "label",
                "source_label",
                "target_label",
                "notes",
                "tags",
                "confidence",
                "date",
                "properties",
            ],
        )
        writer.writeheader()
        for edge in edges:
            writer.writerow(
                _safe_csv_row({
                    "id": edge.id,
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "label": edge.label,
                    "source_label": edge.source_label,
                    "target_label": edge.target_label,
                    "notes": edge.notes,
                    "tags": ";".join(edge.tags),
                    "confidence": (
                        round(edge.confidence * 100, 2)
                        if edge.confidence is not None
                        else ""
                    ),
                    "date": edge.date,
                    "properties": json.dumps(
                        _serializable_properties(edge.properties),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                })
            )

    fieldnames = [
        "type",
        "id",
        "label",
        "de",
        "vers",
        "notes",
        "tags",
        "confiance",
        "source",
        "date",
        "latitude",
        "longitude",
        "synthesix_properties",
    ]
    with import_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for node in nodes:
            writer.writerow(
                _safe_csv_row({
                    "type": "element",
                    "id": node.id,
                    "label": node.label,
                    "de": "",
                    "vers": "",
                    "notes": node.notes,
                    "tags": ";".join(node.tags),
                    "confiance": (
                        round(node.confidence * 100, 2)
                        if node.confidence is not None
                        else ""
                    ),
                    "source": node.source,
                    "date": node.date,
                    "latitude": node.latitude
                    if node.latitude is not None
                    else "",
                    "longitude": node.longitude
                    if node.longitude is not None
                    else "",
                    "synthesix_properties": json.dumps(
                        _serializable_properties(node.properties),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                })
            )
        for edge in edges:
            writer.writerow(
                _safe_csv_row({
                    "type": "lien",
                    "id": edge.id,
                    "label": edge.label,
                    "de": edge.source_label,
                    "vers": edge.target_label,
                    "notes": edge.notes,
                    "tags": ";".join(edge.tags),
                    "confiance": (
                        round(edge.confidence * 100, 2)
                        if edge.confidence is not None
                        else ""
                    ),
                    "source": "",
                    "date": edge.date,
                    "latitude": "",
                    "longitude": "",
                    "synthesix_properties": json.dumps(
                        {
                            **_serializable_properties(edge.properties),
                            "source_id": edge.source_id,
                            "target_id": edge.target_id,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                })
            )

    return import_path, nodes_path, edges_path


NATIVE_PROPERTY_NAMES = {
    "synthesix_id": "ID Synthesix",
    "synthesix_type": "Type Synthesix",
    "reference": "Référence",
    "status": "Statut",
    "url": "URL",
    "canonical_url": "URL canonique",
    "domain": "Domaine",
    "title": "Titre",
    "analyst_status": "Statut analyste",
    "favorite": "Favori",
    "first_observed_at": "Première observation",
    "last_observed_at": "Dernière observation",
    "accessed_at": "Date d'accès",
    "query": "Requête",
    "report_path": "Rapport Synthesix",
    "entity_type": "Type d'entité",
    "suggested_type": "Type suggéré",
    "custom_label": "Libellé analyste",
    "normalized_value": "Valeur normalisée",
    "confidence_reasons": "Raisons de confiance",
    "review_statuses": "Statuts de revue",
    "manifest_path": "Manifeste Synthesix",
    "capture_scope": "Périmètre de capture",
    "linked_source_count": "Sources liées",
}
NATIVE_LINK_PROPERTIES = {
    "relation_status": "Statut de la relation",
}
# Kept on the graph nodes for internal wiring (asset attachment) but never
# surfaced as displayed properties in the export.
HIDDEN_NATIVE_PROPERTIES = {"synthesix_id", "manifest_path"}
PROPERTY_TYPE_OVERRIDES_KEY = "_synthesix_property_types"
PROPERTY_TYPES = {
    "text",
    "number",
    "date",
    "datetime",
    "boolean",
    "choice",
    "geo",
    "country",
    "link",
}


def _native_property_type(
    key: str,
    value: object,
    explicit_type: str = "",
) -> str:
    if explicit_type in PROPERTY_TYPES:
        return explicit_type
    declared = zeroneurone_property_type(key)
    if declared:
        return declared
    normalized_key = str(key).casefold()
    if normalized_key in {"url", "canonical_url"}:
        return "link"
    if normalized_key.endswith("_at") or normalized_key in {
        "date",
        "date/heure",
    }:
        return "datetime"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    return "text"


def _native_properties(
    properties: Mapping[str, object],
    *,
    names: Mapping[str, str] = NATIVE_PROPERTY_NAMES,
) -> list[dict[str, object]]:
    result = []
    property_types = properties.get(PROPERTY_TYPE_OVERRIDES_KEY, {})
    if not isinstance(property_types, Mapping):
        property_types = {}
    for key, value in properties.items():
        if key in {
            "attributes",
            PROPERTY_TYPE_OVERRIDES_KEY,
            *HIDDEN_NATIVE_PROPERTIES,
        }:
            continue
        if value is None or value == "":
            continue
        if key == "confidence_reasons" and isinstance(value, str):
            try:
                loaded = json.loads(value)
            except json.JSONDecodeError:
                loaded = None
            if isinstance(loaded, list):
                value = "; ".join(
                    str(item).strip()
                    for item in loaded
                    if str(item).strip()
                )
                if not value:
                    continue
        property_type = _native_property_type(
            key,
            value,
            str(property_types.get(key, "") or ""),
        )
        if isinstance(value, bool):
            value = "Oui" if value else "Non"
        property_name = names.get(key)
        if property_name is None:
            property_name = (
                key.replace("_", " ").title()
                if "_" in key
                else key
            )
        result.append(
            {
                "key": property_name,
                "value": value,
                "type": property_type,
            }
        )
    return result


def _native_suggested_property_settings(
    tags: Iterable[str],
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    properties_by_key: dict[str, dict[str, object]] = {}
    associations: dict[str, list[dict[str, object]]] = {}
    for tag in sorted(tags, key=str.casefold):
        canonical = canonical_zeroneurone_tag(tag)
        tag_properties = []
        for suggested in zeroneurone_tagset_suggested_properties(canonical):
            key = str(suggested.get("key", "") or "").strip()
            if not key:
                continue
            definition = {
                "key": key,
                "type": str(suggested.get("type", "text") or "text"),
            }
            choices = suggested.get("choices")
            if isinstance(choices, list):
                definition["choices"] = choices
            properties_by_key.setdefault(key, definition)
            tag_properties.append(definition)
        if tag_properties:
            associations[canonical] = tag_properties
    return list(properties_by_key.values()), associations


def _content_size(label: object) -> str:
    """Pick a node size bucket from its label length so wide labels (URLs)
    aren't crammed into tiny nodes."""
    length = len(str(label or ""))
    if length > 38:
        return "large"
    if length > 16:
        return "medium"
    return "small"


def _native_visual(node: GraphNode) -> dict[str, object]:
    node_type = str(node.properties.get("synthesix_type", "") or "")
    entity_type = str(node.properties.get("entity_type", "") or "")
    visual: dict[str, object] = {
        "color": "#ffffff",
        "borderColor": "#e5e7eb",
        "borderWidth": 2,
        "borderStyle": "solid",
        "shape": "rectangle",
        "size": _content_size(node.label),
        "icon": None,
        "image": None,
    }
    if node_type == "investigation":
        visual.update(
            color="#0f172a",
            borderColor="#06b6d4",
            borderWidth=4,
            shape="hexagon",
            size="large",
            icon="Network",
        )
        return visual

    for tag in node.tags:
        tagset_visual = zeroneurone_tagset_visual(tag)
        if tagset_visual is None:
            continue
        for key, value in tagset_visual.items():
            if value is not None:
                visual[key] = value
        return visual

    if node_type == "search":
        visual.update(
            color="var(--color-node-purple)",
            shape="diamond",
        )
    elif node_type == "evidence":
        visual.update(
            color="var(--color-node-orange)",
        )
    elif node_type == "result" or entity_type in {"url", "domain"}:
        visual.update(
            shape="square",
            icon="Globe",
        )
    elif entity_type in {"email", "handle"}:
        visual.update(
            shape="square",
            icon="AtSign",
        )
    return visual


def _native_positions(
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...] = (),
) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[GraphNode]] = {}
    for node in nodes:
        node_type = str(
            node.properties.get("synthesix_type", "entity") or "entity"
        )
        grouped.setdefault(node_type, []).append(node)

    if grouped.get("curated_entity"):
        return _curated_positions(nodes, edges, grouped["curated_entity"])

    columns = {
        "investigation": 0.0,
        "search": -700.0,
        "result": 700.0,
        "entity": 1400.0,
        "evidence": 2100.0,
    }
    positions = {}
    for node_type, items in grouped.items():
        ordered = sorted(items, key=lambda item: (item.label.casefold(), item.id))
        middle = (len(ordered) - 1) / 2
        for index, node in enumerate(ordered):
            positions[node.id] = {
                "x": columns.get(node_type, 650.0),
                "y": (index - middle) * 260.0,
            }
    return positions


def _curated_positions(
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
    entity_nodes: list[GraphNode],
) -> dict[str, dict[str, float]]:
    """Lay curated entities in a column with their source URLs aligned to the
    right, so each entity and its "Trouvé sur" sources read as a row instead of
    a single merged vertical line."""
    source_x = 760.0
    source_row = 220.0
    min_block = 420.0
    sources_by_entity: dict[str, list[str]] = {}
    for edge in edges:
        if edge.label == "Trouvé sur":
            sources_by_entity.setdefault(edge.source_id, []).append(
                edge.target_id
            )

    positions: dict[str, dict[str, float]] = {}
    placed_sources: set[str] = set()
    ordered_entities = sorted(
        entity_nodes, key=lambda item: (item.label.casefold(), item.id)
    )
    cursor = 0.0
    for entity in ordered_entities:
        sources = [
            sid
            for sid in sources_by_entity.get(entity.id, [])
            if sid not in placed_sources
        ]
        # Give each entity a vertical block tall enough for its source fan so
        # clusters never overlap into a single cascading line.
        block = max(min_block, len(sources) * source_row)
        center = cursor + block / 2
        positions[entity.id] = {"x": 0.0, "y": center}
        middle = (len(sources) - 1) / 2
        for source_index, source_id in enumerate(sources):
            placed_sources.add(source_id)
            positions[source_id] = {
                "x": source_x,
                "y": center + (source_index - middle) * source_row,
            }
        cursor += block

    leftover = [node for node in nodes if node.id not in positions]
    middle = (len(leftover) - 1) / 2
    for index, node in enumerate(
        sorted(leftover, key=lambda item: (item.label.casefold(), item.id))
    ):
        positions[node.id] = {
            "x": source_x * 2,
            "y": (index - middle) * min_block,
        }
    return positions


def _resolve_asset_path(
    value: object,
    *,
    base_dir: Path | None,
    asset_root: Path | None,
) -> Path | None:
    if not value or base_dir is None or asset_root is None:
        return None
    path = Path(str(value))
    if not path.is_absolute():
        path = base_dir / path
    path = path.resolve()
    try:
        path.relative_to(asset_root.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _copy_native_assets(
    staging_dir: Path,
    workspace: Mapping,
    *,
    base_dir: Path | None,
    asset_root: Path | None,
) -> tuple[list[dict[str, object]], dict[str, list[str]]]:
    assets_dir = staging_dir / "assets"
    assets = []
    element_asset_ids: dict[str, list[str]] = {}
    copied_paths: dict[Path, str] = {}
    # Evidence files are attached to the curated entities they support, so map
    # each saved page to the entities that source from it.
    entities_by_result: dict[str, list[str]] = {}
    for entity in workspace.get("graph_entities", []):
        entity_id = str(entity.get("id", "") or "")
        if not entity_id:
            continue
        for result_id in entity.get("linked_result_ids", []):
            entities_by_result.setdefault(str(result_id), []).append(entity_id)

    def _attach(asset_id: str, entity_ids: list[str]) -> None:
        for entity_id in entity_ids:
            ids = element_asset_ids.setdefault(entity_id, [])
            if asset_id not in ids:
                ids.append(asset_id)

    for capture in workspace.get("evidence", []):
        capture_id = str(capture.get("id", "") or "")
        if not capture_id:
            continue
        # Curated graph: attach to the entities sourcing this page. Otherwise
        # (results-only export) fall back to the evidence node (capture id).
        target_entity_ids = entities_by_result.get(
            str(capture.get("result_id", "") or ""), []
        ) or [capture_id]
        for artifact in capture.get("artifacts", []):
            source_path = _resolve_asset_path(
                artifact.get("file_path"),
                base_dir=base_dir,
                asset_root=asset_root,
            )
            if source_path is None:
                continue
            if source_path in copied_paths:
                _attach(copied_paths[source_path], target_entity_ids)
                continue
            artifact_id = str(
                artifact.get("id")
                or artifact.get("sha256")
                or source_path
            )
            asset_id = _native_uuid("asset", capture_id, artifact_id)
            copied_paths[source_path] = asset_id
            archive_name = (
                f"{_native_uuid('asset-file', capture_id, artifact_id)}"
                f"{source_path.suffix.lower()}"
            )
            assets_dir.mkdir(parents=True, exist_ok=True)
            destination = assets_dir / archive_name
            shutil.copy2(source_path, destination)
            assets.append(
                {
                    "id": asset_id,
                    "filename": source_path.name,
                    "mimeType": str(
                        artifact.get("mime_type")
                        or "application/octet-stream"
                    ),
                    "size": destination.stat().st_size,
                    "archivePath": f"assets/{archive_name}",
                }
            )
            _attach(asset_id, target_entity_ids)
    return assets, element_asset_ids


def _write_native_dossier(
    staging_dir: Path,
    workspace: Mapping,
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
    *,
    generated_at: str,
    include_evidence: bool,
    base_dir: Path | None,
    asset_root: Path | None,
) -> tuple[Path, Path, int]:
    investigation = workspace.get("investigation", {})
    investigation_id = str(investigation.get("id", "") or "")
    dossier_id = _native_uuid("dossier", investigation_id)
    node_ids = {
        node.id: _native_uuid("element", investigation_id, node.id)
        for node in nodes
    }
    positions = _native_positions(nodes, edges)
    assets: list[dict[str, object]] = []
    element_asset_ids: dict[str, list[str]] = {}
    if include_evidence:
        assets, element_asset_ids = _copy_native_assets(
            staging_dir,
            workspace,
            base_dir=base_dir,
            asset_root=asset_root,
        )

    elements = []
    all_tags: set[str] = set()
    for node in nodes:
        all_tags.update(node.tags)
        synthesix_id = str(node.properties.get("synthesix_id", "") or "")
        # Evidence artifacts are now attached to the curated entity they support.
        asset_ids = element_asset_ids.get(synthesix_id, [])
        geo = None
        if node.latitude is not None and node.longitude is not None:
            geo = {
                "type": "point",
                "lat": node.latitude,
                "lng": node.longitude,
            }
        elements.append(
            {
                "id": node_ids[node.id],
                "dossierId": dossier_id,
                "label": node.label,
                "notes": node.notes,
                "tags": list(node.tags),
                "properties": _native_properties(node.properties),
                "confidence": (
                    round(node.confidence * 100, 2)
                    if node.confidence is not None
                    else None
                ),
                "source": node.source,
                "date": node.date or None,
                "dateRange": None,
                "position": positions[node.id],
                "isPositionLocked": False,
                "geo": geo,
                "events": [dict(event) for event in node.events],
                "visual": _native_visual(node),
                "assetIds": asset_ids,
                "parentGroupId": None,
                "isGroup": False,
                "isAnnotation": False,
                "childIds": [],
                "createdAt": generated_at,
                "updatedAt": generated_at,
            }
        )

    links = []
    for edge in edges:
        links.append(
            {
                "id": _native_uuid("link", investigation_id, edge.id),
                "dossierId": dossier_id,
                "fromId": node_ids[edge.source_id],
                "toId": node_ids[edge.target_id],
                "sourceHandle": None,
                "targetHandle": None,
                "label": edge.label,
                "notes": edge.notes,
                "tags": list(edge.tags),
                "properties": _native_properties(
                    edge.properties,
                    names=NATIVE_LINK_PROPERTIES,
                ),
                "directed": True,
                "direction": "forward",
                "confidence": (
                    round(edge.confidence * 100, 2)
                    if edge.confidence is not None
                    else None
                ),
                "source": "",
                "date": edge.date or None,
                "dateRange": None,
                "visual": {
                    "color": "#9ca3af",
                    "style": "solid",
                    "thickness": 2,
                },
                "curveOffset": {"x": 0, "y": 0},
                "createdAt": generated_at,
                "updatedAt": generated_at,
            }
        )

    suggested_properties, tag_property_associations = (
        _native_suggested_property_settings(all_tags)
    )
    dossier_path = staging_dir / "dossier.json"
    dossier = {
        "version": ZERONEURONE_DOSSIER_VERSION,
        "exportedAt": generated_at,
        "dossier": {
            "id": dossier_id,
            "name": str(
                investigation.get("title")
                or investigation.get("reference")
                or investigation_id
            ),
            "description": str(investigation.get("description", "") or ""),
            "startDate": investigation.get("created_at") or None,
            "creator": "Synthesix",
            "tags": list(investigation.get("tags", [])),
            "properties": _native_properties(
                {
                    "synthesix_id": investigation_id,
                    "reference": investigation.get("reference", ""),
                    "status": investigation.get("status", ""),
                }
            ),
            "createdAt": investigation.get("created_at") or generated_at,
            "updatedAt": investigation.get("updated_at") or generated_at,
            "viewport": {"x": 0, "y": 0, "zoom": 0.75},
            "settings": {
                "defaultElementVisual": {},
                "defaultLinkVisual": {},
                "suggestedProperties": suggested_properties,
                "existingTags": sorted(all_tags, key=str.casefold),
                "tagPropertyAssociations": tag_property_associations,
                "showConfidenceIndicator": True,
                "displayedProperties": [
                    "URL",
                    "Domaine",
                    "Date d'accès",
                ],
                "tagDisplayMode": "icons",
                "tagDisplaySize": "small",
                "linkAnchorMode": "auto",
            },
            "isFavorite": False,
            "isArchived": False,
            "origin": "joined",
            "lastSharedKey": None,
            "lastSharedAsync": False,
        },
        "elements": elements,
        "links": links,
        "assets": assets,
        "report": {
            "id": _native_uuid("report", investigation_id),
            "dossierId": dossier_id,
            "title": "Rapport",
            "sections": [],
            "createdAt": generated_at,
            "updatedAt": generated_at,
        },
    }
    dossier_path.write_text(
        json.dumps(dossier, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    archive_path = staging_dir / "zeroneurone.zip"
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.write(dossier_path, "dossier.json")
        assets_dir = staging_dir / "assets"
        if assets_dir.exists():
            for path in sorted(assets_dir.iterdir()):
                archive.write(path, f"assets/{path.name}")
    return dossier_path, archive_path, len(assets)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_csv_row(row: Mapping[str, object]) -> dict[str, object]:
    safe = {}
    for key, value in row.items():
        if isinstance(value, str) and value.lstrip().startswith(
            ("=", "+", "-", "@")
        ):
            safe[key] = f"'{value}"
        else:
            safe[key] = value
    return safe


def export_zeroneurone_bundle(
    workspace: Mapping,
    output_dir: Path,
    *,
    include_evidence: bool = False,
    include_unreviewed: bool = False,
    tool_version: str = "unknown",
    base_dir: Path | None = None,
    asset_root: Path | None = None,
) -> ZeroNeuroneExport:
    output_dir = Path(output_dir)
    base_dir = Path(base_dir).resolve() if base_dir is not None else None
    asset_root = (
        Path(asset_root).resolve()
        if asset_root is not None
        else base_dir
    )
    staging_dir = output_dir.parent / f".{output_dir.name}-{uuid4().hex}.tmp"
    staging_dir.mkdir(parents=True, exist_ok=False)
    generated_at = _utc_now()
    try:
        nodes, edges = build_export_graph(
            workspace,
            include_evidence=include_evidence,
            include_unreviewed=include_unreviewed,
        )
        graphml_path = staging_dir / "investigation.graphml"
        _write_graphml(graphml_path, nodes, edges)
        csv_path, nodes_csv_path, edges_csv_path = _write_csv_files(
            staging_dir,
            nodes,
            edges,
        )
        dossier_path, archive_path, asset_count = _write_native_dossier(
            staging_dir,
            workspace,
            nodes,
            edges,
            generated_at=generated_at,
            include_evidence=include_evidence,
            base_dir=base_dir,
            asset_root=asset_root,
        )
        artifact_paths = (
            archive_path,
            dossier_path,
            graphml_path,
            csv_path,
            nodes_csv_path,
            edges_csv_path,
        )
        manifest = {
            "schema": EXPORT_SCHEMA_NAME,
            "schema_version": EXPORT_SCHEMA_VERSION,
            "generated_at": generated_at,
            "tool": {
                "name": "Synthesix",
                "version": tool_version,
            },
            "compatibility": {
                "target": (
                    "ZeroNeurone native dossier archive, GraphML, and CSV import"
                ),
                "documentation_url": ZERONEURONE_IMPORT_DOCUMENTATION,
                "documentation_version": "2.19.0",
                "source_version_observed": "2.41.9",
                "source_commit": (
                    "21c2f659b185d9fe9c4adbaccde878367137449a"
                ),
                "verified_on": "2026-06-15",
                "native_dossier_version": ZERONEURONE_DOSSIER_VERSION,
                "native_reference_observed_on": "2026-06-15",
                "tagset_count": len(ZERONEURONE_TAGSETS),
            },
            "options": {
                "include_evidence": include_evidence,
                "include_unreviewed": include_unreviewed,
            },
            "counts": {
                "nodes": len(nodes),
                "edges": len(edges),
                "assets": asset_count,
            },
            "artifacts": [
                {
                    "name": path.name,
                    "sha256": _sha256(path),
                    "byte_size": path.stat().st_size,
                }
                for path in artifact_paths
            ],
        }
        manifest_path = staging_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        staging_dir.replace(output_dir)
    except Exception:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise

    return ZeroNeuroneExport(
        output_dir=output_dir,
        archive_path=output_dir / archive_path.name,
        dossier_path=output_dir / dossier_path.name,
        graphml_path=output_dir / graphml_path.name,
        csv_path=output_dir / csv_path.name,
        nodes_csv_path=output_dir / nodes_csv_path.name,
        edges_csv_path=output_dir / edges_csv_path.name,
        manifest_path=output_dir / manifest_path.name,
        node_count=len(nodes),
        edge_count=len(edges),
        asset_count=asset_count,
        generated_at=generated_at,
    )
