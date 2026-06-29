from __future__ import annotations

import os
import json
from html import escape
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from urllib.parse import quote

from exports.zeroneurone_tagsets import (
    ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES,
    ZERONEURONE_TAGSETS,
    zeroneurone_tagset_suggested_properties,
    zeroneurone_property_type,
)

# Classic zeroneurone property keys, deduplicated across tagsets, used as
# free-text suggestions for the extracted-entity property-name input.
_PROPERTY_SUGGESTION_KEYS = sorted(
    {
        key
        for properties in ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES.values()
        for key, _property_type in properties
    },
    key=str.casefold,
)


# Extracted-entity types that describe the source/page itself rather than a
# fact to attach to a curated entity.
_SOURCE_PROPERTY_TYPES = {"domain", "url", "ipv4", "ipv6"}
_ARCHIVE_ARTIFACT_TYPES = {"html", "mhtml", "text", "txt"}
_IMAGE_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "bmp", "svg",
    "avif", "tiff", "tif", "ico", "heic", "heif",
}
# Synthetic URL prefix used for imported files without an external source URL.
_LOCAL_FILE_URL_PREFIX = "https://files.synthesix.local/"


def _is_source_property(entity: Mapping) -> bool:
    """True when a candidate describes the page/source, not an entity.

    Auto-classified by type, with an explicit ``attributes.property_scope``
    override ("page" / "entity") taking precedence (set by the manual toggle).
    """
    attributes = entity.get("attributes", {})
    if isinstance(attributes, Mapping):
        scope = str(attributes.get("property_scope", "") or "").strip()
        if scope == "page":
            return True
        if scope == "entity":
            return False
    entity_type = str(entity.get("entity_type", "") or "")
    return entity_type in _SOURCE_PROPERTY_TYPES


def _has_archive_artifact(capture: Mapping) -> bool:
    for artifact in capture.get("artifacts", []) or []:
        if not isinstance(artifact, Mapping):
            continue
        artifact_type = str(artifact.get("artifact_type", "") or "").casefold()
        mime_type = str(artifact.get("mime_type", "") or "").casefold()
        if artifact_type in _ARCHIVE_ARTIFACT_TYPES:
            return True
        if "html" in mime_type or mime_type.startswith("text/"):
            return True
    return False


def _imported_artifact_view(
    capture: Mapping,
    output_dir: Path,
    base_dir: Path,
) -> dict | None:
    """Resolve a local, openable href for an imported file capture.

    Returns ``{"href", "is_image"}`` for the first artifact whose file is
    resolvable on disk, or ``None`` when the capture is not an import.
    """
    if str(capture.get("capture_kind", "") or "") != "imported":
        return None
    for artifact in capture.get("artifacts", []) or []:
        if not isinstance(artifact, Mapping):
            continue
        path = _resolve_runtime_path(artifact.get("file_path"), base_dir)
        if path is None:
            continue
        mime = str(artifact.get("mime_type", "") or "").casefold()
        ext = str(artifact.get("artifact_type", "") or "").casefold()
        return {
            "href": _relative_href(path, output_dir),
            "is_image": mime.startswith("image/") or ext in _IMAGE_EXTENSIONS,
        }
    return None


def _archive_artifact(capture: Mapping) -> Mapping | None:
    artifacts = [
        artifact
        for artifact in capture.get("artifacts", []) or []
        if isinstance(artifact, Mapping)
    ]
    priority = {"html": 0, "text": 1, "txt": 1, "mhtml": 2}
    candidates = []
    for artifact in artifacts:
        artifact_type = str(artifact.get("artifact_type", "") or "").casefold()
        mime_type = str(artifact.get("mime_type", "") or "").casefold()
        if artifact_type in _ARCHIVE_ARTIFACT_TYPES:
            candidates.append((priority.get(artifact_type, 9), artifact))
        elif "html" in mime_type:
            candidates.append((0, artifact))
        elif mime_type.startswith("text/"):
            candidates.append((1, artifact))
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item[0])[0][1]


def _text_fragment(value: object) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return ""
    if len(text) > 180:
        text = text[:180].rsplit(" ", 1)[0] or text[:180]
    return "#:~:text=" + quote(text, safe="")


def _property_suggestion_keys(
    entities: list[Mapping],
    graph_entities: list[Mapping],
) -> list[str]:
    """Classic keys plus property names already used in this investigation.

    Lets an analyst reuse a custom property name they typed earlier (e.g.
    "Sandwich") without storing anything extra: it is already persisted as a
    custom label / property key on the entities and curated graph.
    """
    keys = set(_PROPERTY_SUGGESTION_KEYS)
    for entity in entities:
        # Only validated facts feed the memory; proposed ones are noise.
        if str(entity.get("status", "") or "") != "validated":
            continue
        for candidate in (entity.get("custom_label"), entity.get("property_key")):
            text = str(candidate or "").strip()
            if text:
                keys.add(text)
        attributes = entity.get("attributes", {})
        if isinstance(attributes, Mapping):
            text = str(attributes.get("property_key", "") or "").strip()
            if text:
                keys.add(text)
    for graph_entity in graph_entities:
        properties = graph_entity.get("properties", {})
        if isinstance(properties, Mapping):
            for key in properties:
                text = str(key or "").strip()
                if text:
                    keys.add(text)
    return sorted(keys, key=str.casefold)


def _used_property_suggestion_keys(
    entities: list[Mapping],
    graph_entities: list[Mapping],
) -> set[str]:
    """Property names already typed or curated in this investigation."""
    keys: set[str] = set()
    for entity in entities:
        # Only validated facts feed the memory; proposed ones are noise.
        if str(entity.get("status", "") or "") != "validated":
            continue
        for candidate in (entity.get("custom_label"), entity.get("property_key")):
            text = str(candidate or "").strip()
            if text:
                keys.add(text)
        attributes = entity.get("attributes", {})
        if isinstance(attributes, Mapping):
            text = str(attributes.get("property_key", "") or "").strip()
            if text:
                keys.add(text)
    for graph_entity in graph_entities:
        properties = graph_entity.get("properties", {})
        if isinstance(properties, Mapping):
            for key in properties:
                text = str(key or "").strip()
                if text:
                    keys.add(text)
    return keys


def _dom_id_fragment(value: object) -> str:
    text = str(value or "").strip()
    cleaned = "".join(char if char.isalnum() else "-" for char in text)
    cleaned = cleaned.strip("-")
    return cleaned or "item"


def _scoped_property_suggestion_keys(
    result: Mapping,
    graph_entities: list[Mapping],
    used_keys: set[str],
) -> list[str]:
    """Property suggestions from tagsets of graph entities linked to a page."""
    result_id = str(result.get("id", "") or "")
    tagset_keys: set[str] = set()
    for graph_entity in graph_entities:
        linked_result_ids = {
            str(value)
            for value in graph_entity.get("linked_result_ids", []) or []
        }
        if result_id not in linked_result_ids:
            continue
        for tag in graph_entity.get("tags", []) or []:
            for property_ in zeroneurone_tagset_suggested_properties(tag):
                key = str(property_.get("key", "") or "").strip()
                if key:
                    tagset_keys.add(key)
    if not tagset_keys:
        return []
    return sorted(tagset_keys | set(used_keys), key=str.casefold)


def _property_datalist_options(keys: Iterable[object]) -> str:
    return "".join(
        f'<option value="{_html(key)}"></option>'
        for key in keys
        if str(key or "").strip()
    )


def _source_property_suggestion_keys(entities: Iterable[Mapping]) -> list[str]:
    keys = {
        str(property_.get("key", "") or "").strip()
        for property_ in zeroneurone_tagset_suggested_properties("Site web")
        if str(property_.get("key", "") or "").strip()
    }
    for entity in entities:
        if not _is_source_property(entity):
            continue
        if str(entity.get("status", "") or "") != "validated":
            continue
        for candidate in (entity.get("custom_label"), entity.get("property_key")):
            text = str(candidate or "").strip()
            if text:
                keys.add(text)
        attributes = entity.get("attributes", {})
        if isinstance(attributes, Mapping):
            text = str(attributes.get("property_key", "") or "").strip()
            if text:
                keys.add(text)
    return sorted(keys, key=str.casefold)

_PROPERTY_TYPE_LABELS = {
    "text": "Texte",
    "number": "Nombre",
    "date": "Date",
    "datetime": "Date/heure",
    "geo": "Géo",
    "country": "Pays",
    "link": "Lien",
}
PROPERTY_TYPE_VALUES = tuple(_PROPERTY_TYPE_LABELS)


def _property_type_options(selected: str = "") -> str:
    selected = str(selected or "").strip()
    options = ['<option value="">Auto</option>']
    for value in PROPERTY_TYPE_VALUES:
        label = _PROPERTY_TYPE_LABELS[value]
        selected_attr = " selected" if value == selected else ""
        options.append(
            f'<option value="{_html(value)}"{selected_attr}>{_html(label)}</option>'
        )
    return "".join(options)


def _infer_property_type(key: object, value: object = "") -> str:
    """Infer a UI-friendly property type when the analyst leaves Auto selected."""
    key_text = str(key or "").strip().casefold()
    value_text = str(value or "").strip()
    value_fold = value_text.casefold()
    if not key_text and not value_text:
        return ""
    if (
        key_text in {"url", "canonical_url", "source", "website", "site"}
        or "url" in key_text
        or value_fold.startswith(("http://", "https://"))
    ):
        return "link"
    if (
        key_text in {"lat", "latitude", "lon", "lng", "longitude"}
        or "coord" in key_text
        or "gps" in key_text
    ):
        return "geo"
    if "pays" in key_text or "country" in key_text or "nationalit" in key_text:
        return "country"
    if "datetime" in key_text or "date/heure" in key_text or "horodat" in key_text:
        return "datetime"
    if "date" in key_text or key_text.endswith("_at"):
        return "datetime" if ":" in value_text else "date"
    normalized_number = (
        value_text.replace("\u202f", "")
        .replace("\xa0", "")
        .replace(" ", "")
        .replace(",", ".")
    )
    if normalized_number:
        try:
            float(normalized_number)
        except ValueError:
            pass
        else:
            return "number"
    return "text"


def _property_type_badge(
    key: str,
    explicit_type: str = "",
    value: object = "",
) -> str:
    """Small zeroneurone-style type chip for explicit or inferred types."""
    if explicit_type in PROPERTY_TYPE_VALUES:
        property_type = explicit_type
    else:
        declared_type = zeroneurone_property_type(key)
        property_type = (
            declared_type
            if declared_type in PROPERTY_TYPE_VALUES
            else _infer_property_type(key, value)
        )
    if not property_type:
        return ""
    label = _PROPERTY_TYPE_LABELS.get(property_type, property_type)
    return f'<span class="prop-type">{_html(label)}</span>'


STATUS_LABELS = {
    "a_verifier": "To verify",
    "pertinent": "Relevant",
    "ecarte": "Discarded",
    "confirme": "Confirmed",
}
ENTITY_STATUS_LABELS = {
    "proposed": "Proposed",
    "validated": "Validated",
    "rejected": "Rejected",
}
ENTITY_TYPE_LABELS = {
    "email": "Email",
    "phone": "Phone",
    "url": "URL",
    "domain": "Domain",
    "ipv4": "IPv4",
    "ipv6": "IPv6",
    "handle": "Handle",
    "identifier": "Identifier",
    "coordinates": "Coordinates",
    "address": "Postal address",
    "vat_number": "VAT number",
    "siret": "SIRET",
    "siren": "SIREN",
    "date": "Date",
    "person": "Person",
    "organization": "Organization",
    "place": "Place",
    "event": "Event",
    "product": "Product or service",
    "other": "Other",
}


def _html(value) -> str:
    return escape(str(value or ""), quote=True)


_ACTION_ICON_PATHS = {
    "trash": (
        '<polyline points="3 6 5 6 21 6"/>'
        '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
        '<line x1="10" y1="11" x2="10" y2="17"/>'
        '<line x1="14" y1="11" x2="14" y2="17"/>'
        '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>'
    ),
    "plus": (
        '<line x1="12" y1="5" x2="12" y2="19"/>'
        '<line x1="5" y1="12" x2="19" y2="12"/>'
    ),
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "x": (
        '<line x1="18" y1="6" x2="6" y2="18"/>'
        '<line x1="6" y1="6" x2="18" y2="18"/>'
    ),
    "info": (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="12"/>'
        '<line x1="12" y1="8" x2="12.01" y2="8"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    ),
    "scan": (
        '<path d="M3 7V5a2 2 0 0 1 2-2h2"/>'
        '<path d="M17 3h2a2 2 0 0 1 2 2v2"/>'
        '<path d="M21 17v2a2 2 0 0 1-2 2h-2"/>'
        '<path d="M7 21H5a2 2 0 0 1-2-2v-2"/>'
        '<line x1="7" y1="12" x2="17" y2="12"/>'
    ),
    "swap": (
        '<path d="M7 7h11l-3-3"/>'
        '<path d="M17 17H6l3 3"/>'
        '<path d="M18 7l-3 3"/>'
        '<path d="M6 17l3-3"/>'
    ),
    "arrow-left": (
        '<line x1="19" y1="12" x2="5" y2="12"/>'
        '<polyline points="12 19 5 12 12 5"/>'
    ),
    "activity": (
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'
    ),
    "archive": (
        '<rect x="3" y="4" width="18" height="4" rx="1"/>'
        '<path d="M5 8v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8"/>'
        '<path d="M10 12h4"/>'
    ),
    "chevron-up": '<polyline points="18 15 12 9 6 15"/>',
    "external": (
        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
        '<polyline points="15 3 21 3 21 9"/>'
        '<line x1="10" y1="14" x2="21" y2="3"/>'
    ),
}


def _icon(name: str) -> str:
    """Inline, dependency-free action icon (mirrors ui.icon, .icon styling)."""
    path = _ACTION_ICON_PATHS.get(name, "")
    return (
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{path}</svg>'
    )


def _compact_url(value: str, *, max_length: int = 160) -> str:
    text = str(value or "")
    if len(text) <= max_length:
        return text
    tail_length = 36
    head_length = max_length - tail_length - 3
    return f"{text[:head_length]}...{text[-tail_length:]}"


def _wayback_url(value: str) -> str:
    text = str(value or "").strip()
    if not text.startswith(("http://", "https://")):
        return ""
    return f"https://web.archive.org/web/*/{quote(text, safe=':/?#[]@!$&()*+,;=%')}"


def _relative_href(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def _resolve_runtime_path(value: str | None, base_dir: Path) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path


def _display_datetime(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return "Unknown"
    return text.replace("T", " ").replace("+00:00", " UTC")


def _local_datetime(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return "Unknown"
    return (
        f'<time datetime="{_html(text)}" data-local-datetime>'
        f"{_html(_display_datetime(text))}</time>"
    )


def _status_options(selected: str) -> str:
    options = []
    for value, label in STATUS_LABELS.items():
        selection = " selected" if value == selected else ""
        options.append(
            f'<option value="{_html(value)}"{selection}>{_html(label)}</option>'
        )
    return "".join(options)


def _entity_status_options(selected: str) -> str:
    return "".join(
        (
            f'<option value="{_html(value)}"'
            f'{" selected" if value == selected else ""}>'
            f"{_html(label)}</option>"
        )
        for value, label in ENTITY_STATUS_LABELS.items()
    )


def _entity_type_options(selected: str) -> str:
    return "".join(
        (
            f'<option value="{_html(value)}"'
            f'{" selected" if value == selected else ""}>'
            f"{_html(label)}</option>"
        )
        for value, label in ENTITY_TYPE_LABELS.items()
    )


def _tag_values_with_custom(values: Iterable[object] = ()) -> tuple[str, ...]:
    tags = []
    seen = set()
    for value in (*ZERONEURONE_TAGSETS, *values):
        tag = str(value or "").strip()
        key = tag.casefold()
        if not tag or key in seen:
            continue
        tags.append(tag)
        seen.add(key)
    return tuple(tags)


def _tag_datalist_options(values: Iterable[object] = ()) -> str:
    return "".join(
        f'<option value="{_html(tag)}"></option>'
        for tag in _tag_values_with_custom(values)
    )


def _tag_select_options() -> str:
    return "".join(
        f'<option value="{_html(tag)}">{_html(tag)}</option>'
        for tag in ZERONEURONE_TAGSETS
    )


def _default_property_key(entity_type: str) -> str:
    return {
        "email": "Email",
        "phone": "Téléphone",
        "url": "URL",
        "domain": "Domaine",
        "ipv4": "IP",
        "ipv6": "IP",
        "handle": "Compte en ligne",
        "identifier": "Identifiant",
        "coordinates": "Coordonnées",
        "address": "Adresse",
        "vat_number": "Numéro de TVA",
        "siret": "SIRET",
        "siren": "SIREN",
        "date": "Date/heure",
    }.get(entity_type, "Information")


def _default_entity_category(entity_type: str) -> str:
    return {
        "email": "Email",
        "phone": "Téléphone",
        "url": "Site web",
        "domain": "Site web",
        "ipv4": "Site web",
        "ipv6": "Site web",
        "handle": "Compte en ligne",
        "coordinates": "Lieu",
        "address": "Lieu",
        "vat_number": "Entreprise",
        "siret": "Entreprise",
        "siren": "Entreprise",
        "date": "Événement",
        "person": "Personne",
        "organization": "Entreprise",
        "place": "Lieu",
        "event": "Événement",
        "product": "Produit ou service",
    }.get(entity_type, "Entité")


def _source_field_label(value: object) -> str:
    text = str(value or "").strip()
    if not text or text.startswith("archive_text:"):
        return ""
    return {
        "url": "URL",
        "title": "title",
        "description": "description",
        "notes": "notes",
    }.get(text, text.replace("_", " "))


def _entity_source_heading(entity: Mapping) -> str:
    entity_type = str(entity.get("suggested_type") or entity.get("entity_type") or "")
    label = ENTITY_TYPE_LABELS.get(entity_type, entity_type)
    source_label = _source_field_label(entity.get("source_field"))
    if source_label:
        return f"Suggested {label} from {source_label}"
    return f"Suggested {label}"


def _entity_property_key(entity: Mapping) -> str:
    existing = str(entity.get("property_key", "") or "").strip()
    custom_label = str(entity.get("custom_label", "") or "").strip()
    attributes = entity.get("attributes", {})
    inferred = ""
    if isinstance(attributes, Mapping):
        inferred = str(
            attributes.get("property_key")
            or attributes.get("field_label")
            or ""
        ).strip()
    default = _default_property_key(str(entity.get("entity_type", "") or ""))
    if custom_label and (
        not existing or existing in {inferred, default}
    ):
        return custom_label
    if existing:
        return existing
    if custom_label:
        return custom_label
    if inferred:
        return inferred
    return default


def _entity_property_type(entity: Mapping) -> str:
    attributes = entity.get("attributes", {})
    if isinstance(attributes, Mapping):
        property_type = str(attributes.get("property_type", "") or "").strip()
        if property_type in PROPERTY_TYPE_VALUES:
            return property_type
    property_key = _entity_property_key(entity)
    declared = zeroneurone_property_type(property_key)
    if declared in PROPERTY_TYPE_VALUES:
        return declared
    return _infer_property_type(
        property_key,
        entity.get("value_original") or entity.get("value_normalized") or "",
    )


def _extracted_entity_row(
    entity: Mapping,
    *,
    graph_entities: list[Mapping] = (),
    property_suggestions_id: str = "property-suggestions",
    entity_property_suggestions_id: str = "property-suggestions",
    page_property_suggestions_id: str = "property-suggestions",
    read_only: bool = False,
    is_source: bool = False,
) -> str:
    """Self-contained, inline-actionable extracted-entity row (rail triage).

    A *source* property describes the page itself, so it carries neither an
    entity-link select nor the promote-to-entity control.
    """
    disabled = " disabled" if read_only else ""
    entity_id = str(entity.get("id", "") or "")
    entity_type = str(entity.get("entity_type", "") or "")
    type_label = ENTITY_TYPE_LABELS.get(entity_type, entity_type or "")
    status = str(entity.get("status", "proposed") or "proposed")
    value = str(
        entity.get("value_original")
        or entity.get("value_normalized")
        or ""
    )
    property_name = str(entity.get("custom_label", "") or "")
    parent_id = str(entity.get("investigation_entity_id", "") or "")
    property_type = _entity_property_type(entity)
    property_scope = "page" if is_source else "entity"
    next_scope = "entity" if is_source else "page"
    scope_title = (
        "Ranger avec les propriétés à rattacher"
        if is_source
        else "Ranger avec les propriétés de la page"
    )
    property_label = property_name or _entity_property_key(entity)
    property_type_badge = _property_type_badge(
        property_label,
        property_type,
        value,
    )
    if graph_entities:
        options = ['<option value="">Lier à une entité…</option>']
        for graph_entity in graph_entities:
            gid = str(graph_entity.get("id", "") or "")
            selected = " selected" if gid and gid == parent_id else ""
            properties = graph_entity.get("properties", {})
            if not isinstance(properties, Mapping):
                properties = {}
            options.append(
                f'<option value="{_html(gid)}"{selected} '
                f"data-properties='{_html(json.dumps(properties, ensure_ascii=False))}'>"
                f'{_html(graph_entity.get("label", ""))}</option>'
            )
        attach_control = (
            '<select class="entity-chip-row__link" '
            f'data-extracted-attach{disabled}>{"".join(options)}</select>'
        )
    else:
        attach_control = (
            '<span class="field-hint">Créez une entité pour rattacher.</span>'
        )
    # A validated candidate no longer needs the validate button.
    validate_button = (
        ""
        if status == "validated"
        else (
            '<button type="button" class="icon-action entity-validate" '
            f'title="Valider" aria-label="Valider"{disabled}>'
            f'{_icon("check")}</button>'
        )
    )
    promote_button = (
        '<button type="button" class="icon-action entity-promote-toggle" '
        f'title="Promouvoir en entité" aria-label="Promouvoir en entité"'
        f'{disabled}>{_icon("plus")}</button>'
    )
    promote_form = f"""
        <div class="entity-chip-row__promote" hidden>
            <input
                type="text"
                data-quick-entity-category
                list="tag-suggestions"
                maxlength="50"
                placeholder="Catégorie"
                value="{_html(_default_entity_category(entity_type))}"
                {disabled}
            >
            <input
                type="text"
                data-quick-entity-label
                maxlength="200"
                placeholder="Nom de l'entité"
                value="{_html(property_name or value)}"
                {disabled}
            >
            <div class="entity-chip-row__promote-actions">
                <button
                    type="button"
                    class="primary-button create-entity-from-property"
                    {disabled}
                >{_icon("check")} Créer</button>
                <button
                    type="button"
                    class="secondary-button promote-cancel"
                >Annuler</button>
            </div>
        </div>
    """
    return f"""
        <div
            class="entity-chip-row entity-item--{_html(status)}"
            data-entity-id="{_html(entity_id)}"
            data-entity-type="{_html(entity_type)}"
            data-property-type="{_html(property_type)}"
            data-property-scope="{_html(property_scope)}"
            data-attached-entity-id="{_html(parent_id)}"
            data-entity-property-list="{_html(entity_property_suggestions_id)}"
            data-page-property-list="{_html(page_property_suggestions_id)}"
        >
            <div class="entity-chip-row__head">
                <input
                    type="checkbox"
                    class="entity-chip-row__select"
                    data-entity-checkbox
                    aria-label="Sélectionner pour une action groupée"
                    {disabled}
                >
                <span class="entity-chip-row__summary">
                    <strong>{_html(property_label)}</strong>
                    {property_type_badge}
                    <span class="entity-chip-row__value" title="{_html(value)}">{_html(value)}</span>
                </span>
                <span class="entity-chip-row__actions">
                    <span
                        class="info-tip"
                        tabindex="0"
                        role="img"
                        aria-label="Détection"
                        title="{_html(_detection_title(entity))}"
                    >{_icon("info")}</span>
                    <button
                        type="button"
                        class="icon-action entity-scope-toggle"
                        data-scope-toggle
                        data-next-scope="{_html(next_scope)}"
                        title="{_html(scope_title)}"
                        aria-label="{_html(scope_title)}"
                        {disabled}
                    >{_icon("swap")}</button>
                    {validate_button}
                    <button
                        type="button"
                        class="icon-action icon-action--danger entity-reject"
                        title="Rejeter"
                        aria-label="Rejeter"
                        {disabled}
                    >{_icon("trash")}</button>
                    {promote_button}
                </span>
            </div>
            <div class="entity-chip-row__fields">
                <input
                    type="text"
                    class="entity-chip-row__name"
                    data-entity-custom-label
                    list="{_html(property_suggestions_id)}"
                    maxlength="120"
                    value="{_html(property_label)}"
                    placeholder="Nom de propriété"
                    {disabled}
                >
                {attach_control}
            </div>
            {promote_form}
        </div>
    """


def _detection_title(entity: Mapping) -> str:
    """Plain-text detection summary for the info tooltip (native title)."""
    lines = [_entity_source_heading(entity)]
    source_text = str(entity.get("source_text", "") or "").strip()
    if source_text:
        lines.append(source_text)
    for reason in entity.get("confidence_reasons", []):
        text = str(reason).strip()
        if text:
            lines.append(f"• {text}")
    attributes = entity.get("attributes", {})
    if isinstance(attributes, Mapping):
        for key, value in sorted(attributes.items()):
            if key in {"property_type", "property_scope"}:
                continue
            if value in ("", None, [], {}):
                continue
            rendered = (
                json.dumps(value, ensure_ascii=False)
                if isinstance(value, (dict, list))
                else value
            )
            lines.append(f"{key}: {rendered}")
    return "\n".join(line for line in lines if line)


def _entity_markup(
    entities: list[Mapping],
    *,
    graph_entities: list[Mapping] = (),
    property_suggestions_id: str = "property-suggestions",
    page_property_suggestions_id: str = "property-suggestions",
    has_extractable_archive: bool = False,
    read_only: bool,
) -> str:
    disabled = " disabled" if read_only else ""
    scan_hint = (
        ""
        if has_extractable_archive
        else (
            '<button type="button" '
            'class="icon-action icon-action--frame extract-result-entities" '
            'title="Archive HTML/texte requise pour scanner la page" '
            'aria-label="Archive HTML/texte requise pour scanner la page" '
            f'disabled>{_icon("scan")}</button>'
        )
    )
    entity_candidates = [e for e in entities if not _is_source_property(e)]
    source_candidates = [e for e in entities if _is_source_property(e)]
    entity_rows = "".join(
        _extracted_entity_row(
            entity,
            graph_entities=graph_entities,
            property_suggestions_id=property_suggestions_id,
            entity_property_suggestions_id=property_suggestions_id,
            read_only=read_only,
        )
        for entity in entity_candidates
    )
    source_rows = "".join(
        _extracted_entity_row(
            entity,
            graph_entities=graph_entities,
            property_suggestions_id=page_property_suggestions_id,
            entity_property_suggestions_id=property_suggestions_id,
            page_property_suggestions_id=page_property_suggestions_id,
            read_only=read_only,
            is_source=True,
        )
        for entity in source_candidates
    )
    entity_group = (
        '<details class="entity-group" data-entity-group="entity" open'
        f'{" hidden" if not entity_candidates else ""}>'
        '<summary class="entity-group__label">À rattacher à une entité</summary>'
        f'<div class="entity-chip-list" data-entity-list="entity">{entity_rows}</div>'
        "</details>"
    )
    source_group = (
        '<details class="entity-group entity-group--source" data-entity-group="page" open'
        f'{" hidden" if not source_candidates else ""}>'
        '<summary class="entity-group__label">Propriétés de la page</summary>'
        f'<div class="entity-chip-list" data-entity-list="page">{source_rows}</div>'
        "</details>"
    )
    empty = (
        ""
        if entities
        else '<p class="session-note">No entity candidate extracted yet.</p>'
    )
    batch_attach = ""
    if graph_entities:
        options = ['<option value="">Lier la sélection à…</option>']
        for graph_entity in graph_entities:
            gid = str(graph_entity.get("id", "") or "")
            properties = graph_entity.get("properties", {})
            if not isinstance(properties, Mapping):
                properties = {}
            options.append(
                f'<option value="{_html(gid)}" '
                f"data-properties='{_html(json.dumps(properties, ensure_ascii=False))}'>"
                f'{_html(graph_entity.get("label", ""))}</option>'
            )
        batch_attach = (
            '<select class="entity-batch-bar__link" data-batch-attach'
            f'{disabled}>{"".join(options)}</select>'
        )
    batch_bar = (
        (
            '<div class="entity-batch-bar" data-entity-batch hidden>'
            '<span class="entity-batch-bar__count" data-batch-count></span>'
            f'{batch_attach}'
            '<button type="button" class="icon-action icon-action--danger" '
            'data-batch-reject title="Rejeter la sélection" '
            f'aria-label="Rejeter la sélection"{disabled}>'
            f'{_icon("trash")}</button>'
            "</div>"
        )
        if entities
        else ""
    )
    filter_bar = (
        (
            '<div class="entity-filter" data-entity-filter>'
            '<input type="search" class="entity-filter__query" '
            'data-entity-filter-query placeholder="Filtrer les propriétés…" '
            'aria-label="Filtrer les propriétés">'
            '<select class="entity-filter__status" data-entity-filter-status '
            'aria-label="Filtrer par statut">'
            '<option value="">Toutes</option>'
            '<option value="proposed">En attente</option>'
            '<option value="validated">Validées</option>'
            "</select>"
            "</div>"
        )
        if entities
        else ""
    )
    return f"""
        <div class="result-entities">
            <div class="entity-heading">
                <span class="provenance-label">
                    Entities (<span data-extracted-entity-count>{len(entities)}</span>)
                </span>
                {scan_hint}
            </div>
            {empty}
            {filter_bar}
            {batch_bar}
            {entity_group}
            {source_group}
        </div>
    """


def _graph_entities_markup(
    graph_entities: list[Mapping],
    results_by_id: Mapping[str, Mapping],
    *,
    entities: list[Mapping] = (),
    evidence_by_result: Mapping[str, list[Mapping]] | None = None,
    output_dir: Path | None = None,
    base_dir: Path | None = None,
    read_only: bool,
) -> str:
    disabled = " disabled" if read_only else ""
    evidence_by_result = evidence_by_result or {}
    output_dir = output_dir or Path(".")
    base_dir = base_dir or Path(".")
    captures_by_id = {
        str(capture.get("id", "") or ""): capture
        for captures in evidence_by_result.values()
        for capture in captures
    }
    latest_archive_by_result: dict[str, Mapping] = {}
    for result_id, captures in evidence_by_result.items():
        archives = [
            capture
            for capture in captures
            if capture.get("capture_kind") == "page_archive"
            and _has_archive_artifact(capture)
        ]
        if archives:
            latest_archive_by_result[str(result_id)] = sorted(
                archives,
                key=lambda item: str(item.get("captured_at", "") or ""),
                reverse=True,
            )[0]
    # Map each curated entity's property keys to the saved page they were
    # extracted from, so a property can link back to its source/proof.
    sources_by_parent: dict[str, dict[str, list[dict[str, str]]]] = {}
    for extracted in entities or ():
        parent_id = str(extracted.get("investigation_entity_id", "") or "")
        if not parent_id or extracted.get("status") == "rejected":
            continue
        result = results_by_id.get(str(extracted.get("result_id", "") or ""))
        url = str(result.get("url", "") or "") if result else ""
        if not url.startswith(("http://", "https://")):
            continue
        attributes = extracted.get("attributes", {})
        if not isinstance(attributes, Mapping):
            attributes = {}
        capture = captures_by_id.get(
            str(attributes.get("source_capture_id", "") or "")
        )
        if capture is None:
            capture = latest_archive_by_result.get(
                str(extracted.get("result_id", "") or "")
            )
        archive_href = _archive_href(
            capture,
            output_dir=output_dir,
            base_dir=base_dir,
            fragment_text=extracted.get("source_text", ""),
        )
        source = {
            "url": url,
            "href": archive_href or url,
            "source_href": (
                _archive_href(
                    capture,
                    output_dir=output_dir,
                    base_dir=base_dir,
                )
                or url
            ),
            "title": str(result.get("title") or url) if result else url,
        }
        keys = set()
        resolved = _entity_property_key(extracted)
        if resolved:
            keys.add(resolved.casefold())
        raw_key = str(extracted.get("property_key", "") or "").strip()
        if raw_key:
            keys.add(raw_key.casefold())
        for key in keys:
            key_sources = sources_by_parent.setdefault(parent_id, {}).setdefault(
                key,
                [],
            )
            if all(item.get("url") != url for item in key_sources):
                key_sources.append(source)
    cards = []
    for entity in graph_entities:
        entity_id = str(entity.get("id", "") or "")
        properties = entity.get("properties", {})
        if not isinstance(properties, Mapping):
            properties = {}
        property_sources = sources_by_parent.get(entity_id, {})
        source_entries: list[tuple[int, str, str, str]] = []
        seen_source_urls: set[str] = set()
        for result_id in entity.get("linked_result_ids", []):
            result = results_by_id.get(str(result_id))
            if not result:
                continue
            url = str(result.get("url", "") or "")
            if not url or url in seen_source_urls:
                continue
            seen_source_urls.add(url)
            capture = latest_archive_by_result.get(str(result_id))
            source_href = (
                _archive_href(capture, output_dir=output_dir, base_dir=base_dir)
                or url
            )
            source_entries.append(
                (
                    len(source_entries) + 1,
                    url,
                    source_href,
                    str(result.get("title") or url),
                )
            )
        for sources in property_sources.values():
            for source in sources:
                url = source.get("url", "")
                if not url or url in seen_source_urls:
                    continue
                seen_source_urls.add(url)
                source_entries.append(
                    (
                        len(source_entries) + 1,
                        url,
                        source.get("source_href", "") or url,
                        source.get("title", "") or url,
                    )
                )
        source_index_by_url = {
            url: index for index, url, _href, _title in source_entries
        }

        def _property_source_link(key: str) -> str:
            sources = property_sources.get(str(key).casefold(), [])
            if not sources:
                return ""
            links = []
            for source in sources:
                url = source.get("url", "")
                index = source_index_by_url.get(url, len(links) + 1)
                links.append(
                    f'<a class="graph-property-source" href="{_html(source.get("href", "") or url)}" '
                    'target="_blank" rel="noopener noreferrer" '
                    f'title="Open source {index}" '
                    f'aria-label="Open source {index}">'
                    f'<span class="source-ref">{index}</span>{_icon("external")}</a>'
                )
            return "".join(links)

        def _property_type_for_key(key: object) -> str:
            key_text = str(key).casefold()
            for extracted in entities or ():
                if (
                    str(extracted.get("investigation_entity_id", "") or "")
                    != entity_id
                    or extracted.get("status") == "rejected"
                ):
                    continue
                keys = {
                    _entity_property_key(extracted).casefold(),
                    str(extracted.get("property_key", "") or "").strip().casefold(),
                }
                if key_text in keys:
                    return _entity_property_type(extracted)
            return ""

        def _source_row(entry: tuple[int, str, str, str]) -> str:
            index, _url, href, title = entry
            return (
                '<li>'
                f'<span class="source-ref source-ref--list">{index}</span>'
                f'<a href="{_html(href)}" target="_blank" '
                f'rel="noopener noreferrer">{_html(title)}</a>'
                '</li>'
            )

        property_rows = "".join(
            f"""
            <li>
                <div class="graph-property-head">
                    <span class="graph-property-key">
                        <strong>{_html(key)}</strong>
                        {_property_type_badge(key, _property_type_for_key(key), value)}
                    </span>
                    <span class="graph-property-actions">
                        {_property_source_link(key)}
                        <button
                            type="button"
                            class="icon-action icon-action--danger delete-graph-property"
                            data-property-key="{_html(key)}"
                            title="Remove property"
                            aria-label="Remove property"
                            {disabled}
                        >{_icon("trash")}</button>
                    </span>
                </div>
                <span class="graph-property-value">{_html(value)}</span>
            </li>
            """
            for key, value in properties.items()
            if str(value or "").strip()
        )
        source_rows = "".join(_source_row(entry) for entry in source_entries)
        relations = entity.get("relations", []) or []
        relation_rows = "".join(
            f"""
            <li class="entity-relation" data-relation-id="{_html(relation.get("id", ""))}">
                <input
                    type="text"
                    class="entity-relation__label"
                    data-relation-label
                    maxlength="120"
                    value="{_html(relation.get("label", ""))}"
                    placeholder="Mot clé…"
                    {disabled}
                >
                <button type="button" class="entity-relation__target entity-relation__goto" data-relation-goto="{_html(relation.get("target_entity_id", ""))}" title="Aller à l'entité">→ {_html(relation.get("target_label", ""))}</button>
                <button type="button" class="icon-action icon-action--danger delete-relation"
                    title="Supprimer la relation" aria-label="Supprimer la relation"{disabled}>{_icon("trash")}</button>
            </li>
            """
            for relation in relations
        )
        incoming_relations = entity.get("incoming_relations", []) or []
        relation_rows += "".join(
            f"""
            <li class="entity-relation entity-relation--incoming" data-relation-id="{_html(relation.get("id", ""))}">
                <button type="button" class="entity-relation__incoming entity-relation__goto" data-relation-goto="{_html(relation.get("source_entity_id", ""))}" title="Aller à l'entité">← {_html(relation.get("source_label", ""))} : {_html(relation.get("label", "") or "lié")}</button>
                <button type="button" class="icon-action icon-action--danger delete-relation"
                    title="Supprimer la relation" aria-label="Supprimer la relation"{disabled}>{_icon("trash")}</button>
            </li>
            """
            for relation in incoming_relations
        )
        relation_options = "".join(
            f'<option value="{_html(str(other.get("id", "") or ""))}">'
            f'{_html(other.get("label", ""))}</option>'
            for other in graph_entities
            if str(other.get("id", "") or "") != entity_id
        )
        entity_tags = entity.get("tags", []) or []
        tag_chips = "".join(
            f'<span class="tag-chip" data-tag="{_html(tag)}">{_html(tag)}'
            '<button type="button" class="tag-chip__remove" data-tag-remove '
            f'aria-label="Remove tag"{disabled}>&times;</button></span>'
            for tag in entity_tags
        )
        cards.append(
            f"""
            <article class="graph-entity-card inspector-entity" data-graph-entity-id="{_html(entity_id)}" data-inspector-entity="{_html(entity_id)}" hidden>
                <div class="entity-section entity-identity">
                    <div class="entity-section__head">
                        <span class="entity-section__title">Identité</span>
                        <button
                            type="button"
                            class="icon-action icon-action--danger delete-graph-entity"
                            title="Delete entity"
                            aria-label="Delete entity"
                            {disabled}
                        >{_icon("trash")}</button>
                    </div>
                    <label class="entity-field">
                        <span class="entity-field__label">Nom</span>
                        <input
                            type="text"
                            data-graph-entity-label
                            maxlength="200"
                            value="{_html(entity.get("label", ""))}"
                            {disabled}
                        >
                    </label>
                    <label class="entity-field">
                        <span class="entity-field__label">Notes</span>
                        <textarea
                            rows="3"
                            data-graph-entity-notes
                            placeholder="Notes…"
                            {disabled}
                        >{_html(entity.get("notes", ""))}</textarea>
                    </label>
                    <div class="entity-field">
                        <span class="entity-field__label">Tags</span>
                        <div class="tag-editor" data-tags-editor>
                            <div class="tag-editor__chips" data-tags-chips>{tag_chips}</div>
                            <input
                                type="text"
                                class="tag-editor__input"
                                data-tag-input
                                list="entity-tagsets"
                                placeholder="Nouveau tag…"
                                {disabled}
                            >
                        </div>
                    </div>
                </div>
                <div class="entity-section">
                    <span class="entity-section__title">Propriétés</span>
                    <ul class="graph-property-list">
                        {property_rows or '<li class="entity-empty">Aucune propriété.</li>'}
                    </ul>
                    <form class="graph-property-add" data-add-property>
                        <input
                            type="text"
                            class="graph-property-add__key"
                            data-add-property-key
                            list="property-suggestions"
                            maxlength="80"
                            placeholder="Propriété"
                            aria-label="Nom de la propriété"
                            {disabled}
                        >
                        <input
                            type="text"
                            class="graph-property-add__value"
                            data-add-property-value
                            maxlength="500"
                            placeholder="Valeur"
                            aria-label="Valeur de la propriété"
                            {disabled}
                        >
                        <button
                            type="submit"
                            class="secondary-button graph-property-add__submit"
                            {disabled}
                        >Ajouter</button>
                    </form>
                </div>
                <div class="entity-section">
                    <span class="entity-section__title">Relations</span>
                    <ul class="entity-relation-list">{relation_rows}</ul>
                    <form class="entity-relation-add" data-add-relation>
                        <input
                            type="text"
                            class="entity-relation-add__label"
                            data-relation-add-label
                            maxlength="120"
                            placeholder="Mot clé (ex. PDG de)"
                            {disabled}
                        >
                        <select class="entity-relation-add__target" data-relation-add-target{disabled}>
                            <option value="">Entité…</option>
                            {relation_options}
                        </select>
                        <button type="submit" class="secondary-button"{disabled}>Lier</button>
                    </form>
                </div>
                <div class="entity-section">
                    <span class="entity-section__title">Sources</span>
                    <ul class="entity-source-list">{source_rows or '<li class="entity-empty">Aucune source liée.</li>'}</ul>
                </div>
            </article>
            """
        )
    return "".join(cards)


def _entity_rows_markup(
    graph_entities: list[Mapping],
    *,
    read_only: bool,
) -> str:
    """Compact, clickable entity list for the main column.

    Each row selects the matching ``.graph-entity-card`` management panel
    rendered (hidden) in the workspace rail.
    """
    if not graph_entities:
        return """
            <p class="session-note">
                No investigation entity yet. Create the person, company, place,
                event, or other element that should appear in the final graph.
            </p>
        """
    rows = []
    for entity in graph_entities:
        entity_id = str(entity.get("id", "") or "")
        properties = entity.get("properties", {})
        property_count = len(properties) if isinstance(properties, Mapping) else 0
        source_count = sum(
            1 for _ in entity.get("linked_result_ids", []) or []
        )
        tags = [str(tag) for tag in entity.get("tags", []) or [] if str(tag).strip()]
        visible_tags = tags[:2]
        tag_markup = "".join(
            f'<span class="result-tag">{_html(tag)}</span>' for tag in visible_tags
        )
        if len(tags) > len(visible_tags):
            tag_markup += (
                f'<span class="result-tag" title="{_html(", ".join(tags))}">'
                f"+{len(tags) - len(visible_tags)}</span>"
            )
        search_text = " ".join(
            [
                str(entity.get("label", "") or ""),
                " ".join(tags),
                " ".join(str(key) for key in properties.keys()),
                " ".join(str(value) for value in properties.values()),
            ]
        ).casefold()
        rows.append(
            f"""
            <button
                type="button"
                class="entity-row"
                data-entity-select="{_html(entity_id)}"
                data-entity-search="{_html(search_text)}"
            >
                <span class="entity-row__label">{_html(entity.get("label", ""))}</span>
                <span class="entity-row__tags">{tag_markup}</span>
                <span class="entity-row__meta" aria-label="{property_count} properties and {source_count} sources">
                    <span title="{property_count} properties">◇ {property_count}</span>
                    <span title="{source_count} linked sources">↗ {source_count}</span>
                </span>
            </button>
            """
        )
    return "".join(rows)


def _url_analysis_markup(
    analyses: list[Mapping],
    *,
    read_only: bool,
) -> str:
    disabled = " disabled" if read_only else ""
    if not analyses:
        return f"""
            <div class="result-url-analysis">
                <div class="entity-heading">
                    <span class="provenance-label">Technical URL analysis</span>
                    <button
                        type="button"
                        class="icon-action icon-action--frame analyze-result-url"
                        title="Analyze URL"
                        aria-label="Analyze URL"
                        {disabled}
                    >{_icon("search")}</button>
                </div>
                <p class="session-note">
                    No explicit network analysis has been run.
                </p>
            </div>
        """

    latest = analyses[0]
    redirects = [
        item
        for item in latest.get("redirects", [])
        if isinstance(item, Mapping)
    ]
    headers = latest.get("headers", {})
    if not isinstance(headers, Mapping):
        headers = {}
    redirect_items = "".join(
        (
            "<li>"
            f"{int(item.get('status_code', 0) or 0)} "
            f"{_html(item.get('url', ''))} to "
            f"{_html(item.get('location', ''))}"
            "</li>"
        )
        for item in redirects
    )
    header_items = "".join(
        f"<li><code>{_html(name)}</code>: {_html(value)}</li>"
        for name, value in sorted(headers.items())
    )
    content_length = latest.get("content_length")
    size_text = (
        f"{int(content_length):,} declared bytes"
        if content_length is not None
        else f"{int(latest.get('bytes_read', 0) or 0):,} bytes read"
    )
    hash_value = str(latest.get("content_sha256", "") or "")
    hash_markup = (
        f"<code>SHA-256 {_html(hash_value)}</code>"
        if hash_value
        else "<span>Content hash skipped because the response exceeded 5 MiB.</span>"
    )
    tracking_parameters = [
        str(value)
        for value in latest.get("tracking_parameters", [])
        if str(value).strip()
    ]
    cleaned_url = str(latest.get("cleaned_url", "") or "")
    final_url = str(latest.get("final_url", "") or "")
    cleaned_markup = (
        f'<a href="{_html(cleaned_url)}" target="_blank" '
        'rel="noopener noreferrer">Open suggested URL without known tracking parameters</a>'
        if tracking_parameters and cleaned_url and cleaned_url != final_url
        else ""
    )
    return f"""
        <div class="result-url-analysis">
            <div class="entity-heading">
                <span class="provenance-label">
                    Technical URL analysis ({len(analyses)})
                </span>
                <button
                    type="button"
                    class="icon-action icon-action--frame analyze-result-url"
                    title="Analyze URL"
                    aria-label="Analyze URL"
                    {disabled}
                >{_icon("search")}</button>
            </div>
            <div class="url-analysis-summary">
                <strong>HTTP {int(latest.get("status_code", 0) or 0)}</strong>
                <span>{len(redirects)} redirect(s)</span>
                <span>{_html(latest.get("content_type", "") or "Unknown content type")}</span>
                <span>{_html(size_text)}</span>
                <span>{int(latest.get("elapsed_ms", 0) or 0)} ms</span>
                <span>{_local_datetime(latest.get("analyzed_at"))}</span>
            </div>
            <div class="result-url" title="{_html(final_url)}">
                {_html(_compact_url(final_url))}
            </div>
            <div class="url-analysis-domains">
                <span>Unicode domain: {_html(latest.get("final_domain_unicode", ""))}</span>
                <span>Punycode: {_html(latest.get("final_domain_punycode", ""))}</span>
            </div>
            <div class="url-analysis-hash">{hash_markup}</div>
            {cleaned_markup}
            <details>
                <summary>Redirects and retained headers</summary>
                <ul>{redirect_items or "<li>No redirect.</li>"}</ul>
                <ul>{header_items or "<li>No retained header.</li>"}</ul>
            </details>
        </div>
    """


def _inspector_panel(
    result: Mapping,
    *,
    is_monitored: bool,
    details_markup: str = "",
    local_file_href: str = "",
) -> str:
    """Compact summary of a saved page, shown in the workspace rail on click."""
    result_id = str(result.get("id", ""))
    title = str(result.get("title") or result.get("url") or "Untitled result")
    url = str(result.get("url", ""))
    is_local_file = url.startswith(_LOCAL_FILE_URL_PREFIX)
    status = str(result.get("analyst_status", "a_verifier"))
    status_label = STATUS_LABELS.get(status, status)
    if is_local_file and local_file_href:
        title_markup = (
            f'<a class="inspector-panel__title" href="{_html(local_file_href)}" '
            f'target="_blank" rel="noopener noreferrer">{_html(title)}</a>'
        )
    elif url.startswith(("http://", "https://")):
        title_markup = (
            f'<a class="inspector-panel__title" href="{_html(url)}" target="_blank" '
            f'rel="noopener noreferrer">{_html(title)}</a>'
        )
    else:
        title_markup = f'<span class="inspector-panel__title">{_html(title)}</span>'
    if is_local_file:
        url_markup = (
            '<div class="inspector-panel__url">Imported document</div>'
        )
    elif url:
        url_markup = (
            f'<div class="inspector-panel__url" title="{_html(url)}">'
            f"{_html(_compact_url(url, max_length=90))}</div>"
        )
    else:
        url_markup = ""
    badges = [
        f'<span class="inspector-badge inspector-badge--status">'
        f"{_html(status_label)}</span>"
    ]
    if bool(result.get("favorite", False)):
        badges.append(
            '<span class="inspector-badge inspector-badge--fav">Favorite</span>'
        )
    if is_monitored:
        badges.append(
            '<span class="inspector-badge inspector-badge--mon">Monitoring</span>'
        )
    return (
        f'<div class="inspector-panel" data-inspector-panel="{_html(result_id)}" '
        f'data-result-id="{_html(result_id)}" hidden>'
        f"{title_markup}{url_markup}"
        f'<div class="inspector-panel__badges">{"".join(badges)}</div>'
        f'<div class="inspector-panel__details">{details_markup}</div>'
        "</div>"
    )


def _has_extractable_archive(captures: Sequence[Mapping]) -> bool:
    archive_types = {"html", "mhtml", "text", "txt"}
    for capture in captures:
        for artifact in capture.get("artifacts", []) or []:
            if not isinstance(artifact, Mapping):
                continue
            artifact_type = str(artifact.get("artifact_type", "") or "").casefold()
            mime_type = str(artifact.get("mime_type", "") or "").casefold()
            if artifact_type in archive_types:
                return True
            if "html" in mime_type or mime_type.startswith("text/"):
                return True
    return False


def _page_linked_entities_markup(
    result: Mapping,
    graph_entities: Sequence[Mapping],
    extracted_entities: Sequence[Mapping],
) -> str:
    result_id = str(result.get("id", "") or "")
    linked_parent_ids = {
        str(entity.get("investigation_entity_id", "") or "")
        for entity in extracted_entities
        if str(entity.get("investigation_entity_id", "") or "").strip()
        and entity.get("status") != "rejected"
    }
    linked = []
    for graph_entity in graph_entities:
        entity_id = str(graph_entity.get("id", "") or "")
        linked_result_ids = {
            str(value)
            for value in graph_entity.get("linked_result_ids", []) or []
        }
        if result_id in linked_result_ids or entity_id in linked_parent_ids:
            linked.append(graph_entity)
    if not linked:
        return ""
    items = "".join(
        f"""
        <button
            type="button"
            class="page-linked-entity"
            data-page-linked-entity="{_html(entity.get("id", ""))}"
            title="Ouvrir le détail de {_html(entity.get("label", ""))}"
            aria-label="Ouvrir le détail de {_html(entity.get("label", ""))}"
        >
            <span class="page-linked-entity__label">{_html(entity.get("label", ""))}</span>
            <span class="page-linked-entity__meta">↗</span>
        </button>
        """
        for entity in linked
    )
    return f"""
        <div class="result-page-entities">
            <span class="provenance-label">Entités utilisant cette page</span>
            <div class="page-linked-entity-list">{items}</div>
        </div>
    """


def _archive_href(
    capture: Mapping | None,
    *,
    output_dir: Path,
    base_dir: Path,
    fragment_text: object = "",
) -> str:
    if not capture:
        return ""
    artifact = _archive_artifact(capture)
    if not artifact:
        return ""
    artifact_path = _resolve_runtime_path(artifact.get("file_path"), base_dir)
    if artifact_path is None:
        return ""
    href = _relative_href(artifact_path, output_dir)
    fragment = _text_fragment(fragment_text)
    return href + fragment


def _protected_capture_ids(
    graph_entities: Sequence[Mapping],
    entities: Sequence[Mapping],
    evidence_by_result: Mapping[str, list[Mapping]],
) -> set[str]:
    protected = {
        str(entity.get("attributes", {}).get("source_capture_id", "") or "")
        for entity in entities
        if isinstance(entity.get("attributes", {}), Mapping)
    }
    for graph_entity in graph_entities:
        for result_id in graph_entity.get("linked_result_ids", []) or []:
            archives = [
                capture
                for capture in evidence_by_result.get(str(result_id), [])
                if capture.get("capture_kind") == "page_archive"
                and _has_archive_artifact(capture)
            ]
            if archives:
                latest = sorted(
                    archives,
                    key=lambda item: str(item.get("captured_at", "") or ""),
                    reverse=True,
                )[0]
                protected.add(str(latest.get("id", "") or ""))
    return {capture_id for capture_id in protected if capture_id}


def _evidence_markup(
    captures: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
    protected_capture_ids: set[str] | None = None,
    read_only: bool,
) -> str:
    if not captures:
        return ""

    items = []
    protected_capture_ids = protected_capture_ids or set()
    for capture in captures:
        artifact_hrefs = {}
        for artifact in capture.get("artifacts", []):
            artifact_type = str(artifact.get("artifact_type", "") or "")
            artifact_path = _resolve_runtime_path(
                artifact.get("file_path"),
                base_dir,
            )
            if artifact_type and artifact_path is not None:
                artifact_hrefs[artifact_type] = _relative_href(
                    artifact_path,
                    output_dir,
                )
        png_href = artifact_hrefs.get("png", "")
        manifest_path = _resolve_runtime_path(
            capture.get("manifest_path"),
            base_dir,
        )
        manifest_href = (
            _relative_href(manifest_path, output_dir)
            if manifest_path is not None
            else ""
        )
        artifact_links = "".join(
            f'<a class="secondary-link" href="{_html(href)}" '
            'target="_blank" rel="noopener noreferrer">'
            f"{_html(label)}</a>"
            for artifact_type, label in (
                ("html", "HTML"),
                ("mhtml", "MHTML"),
                ("text", "Text"),
            )
            if (href := artifact_hrefs.get(artifact_type))
        )
        if manifest_href:
            artifact_links += (
                f'<a class="secondary-link" href="{_html(manifest_href)}" '
                'target="_blank" rel="noopener noreferrer">Manifest</a>'
            )
        capture_kind = str(
            capture.get("capture_kind", "screenshot") or "screenshot"
        )
        imported_view = _imported_artifact_view(capture, output_dir, base_dir)
        imported_href = imported_view["href"] if imported_view else ""
        if imported_href:
            artifact_links = (
                '<a class="secondary-link" '
                f'href="{_html(imported_href)}" '
                'target="_blank" rel="noopener noreferrer">Ouvrir</a>'
            ) + artifact_links
        # Image imports get an inline thumbnail; other files reuse png logic.
        thumb_img_href = png_href or (
            imported_href if imported_view and imported_view["is_image"] else ""
        )
        view_href = png_href or imported_href
        can_extract_properties = _has_extractable_archive([capture])
        if capture_kind == "page_archive":
            scope = "Page archive"
        else:
            scope = (
                "Selected area"
                if capture.get("capture_scope") == "region"
                else "Visible area"
            )
        capture_name = str(capture.get("name", "") or "").strip()
        display_name = capture_name or scope
        scope_detail = (
            f'<span class="evidence-scope">{_html(scope)}</span>'
            if capture_name
            else ""
        )
        status_detail = (
            '<span class="evidence-scope">Partial capture</span>'
            if capture.get("status") == "partial"
            else ""
        )
        disabled = " disabled" if read_only else ""
        capture_id = str(capture.get("id", "") or "")
        is_protected = capture_id in protected_capture_ids
        delete_control = (
            '<button type="button" '
            'class="icon-action icon-action--danger delete-evidence" '
            'title="Archive utilisée comme preuve de provenance" '
            'aria-label="Archive utilisée comme preuve de provenance" '
            'disabled>'
            f'{_icon("trash")}</button>'
            if is_protected
            else (
                '<button type="button" '
                'class="icon-action icon-action--danger delete-evidence" '
                'title="Delete this capture and its local evidence files" '
                'aria-label="Delete this capture and its local evidence files" '
                f'{disabled}>{_icon("trash")}</button>'
            )
        )
        if thumb_img_href:
            thumbnail = (
                f'<a class="evidence-thumbnail" href="{_html(thumb_img_href)}" '
                'target="_blank" rel="noopener noreferrer" '
                f'aria-label="Open {_html(display_name)}">'
                f'<img src="{_html(thumb_img_href)}" alt="" loading="lazy"></a>'
            )
        elif capture_kind == "page_archive":
            thumbnail = (
                '<div class="evidence-thumbnail '
                'evidence-thumbnail--empty evidence-thumbnail--archive" '
                'aria-label="Page archive"></div>'
            )
        elif imported_href:
            thumbnail = (
                f'<a class="evidence-thumbnail '
                'evidence-thumbnail--empty evidence-thumbnail--file" '
                f'href="{_html(imported_href)}" '
                'target="_blank" rel="noopener noreferrer" '
                f'aria-label="Open {_html(display_name)}"></a>'
            )
        else:
            thumbnail = (
                '<div class="evidence-thumbnail evidence-thumbnail--empty"></div>'
            )
        name_markup = (
            f'<a class="evidence-name" href="{_html(view_href)}" '
            'target="_blank" rel="noopener noreferrer">'
            f"{_html(display_name)}</a>"
            if view_href
            else f'<strong class="evidence-name">{_html(display_name)}</strong>'
        )
        verify_title = (
            "Recalculate every artifact hash and compare it with the "
            "recorded SHA-256"
        )
        items.append(
            f"""
            <li
                class="evidence-item"
                data-evidence-id="{_html(capture_id)}"
            >
                {thumbnail}
                <div class="evidence-copy">
                    {name_markup}
                    {scope_detail}
                    {status_detail}
                    <span>{_local_datetime(capture.get("captured_at"))}</span>
                </div>
                <div class="evidence-links">
                    {artifact_links}
                    {
                        (
                            '<button type="button" '
                            'class="icon-action icon-action--frame '
                            'extract-result-entities evidence-extract-properties" '
                            'title="Extraire les propriétés depuis cette archive" '
                            'aria-label="Extraire les propriétés depuis cette archive" '
                            f'{disabled}>{_icon("scan")}</button>'
                        )
                        if can_extract_properties
                        else ""
                    }
                    <button
                        type="button"
                        class="icon-action icon-action--frame verify-evidence"
                        title="{verify_title}"
                        aria-label="{verify_title}"
                    >{_icon("check")}</button>
                    {delete_control}
                </div>
                <span
                    class="evidence-verification"
                    data-evidence-verification
                    aria-live="polite"
                ></span>
            </li>
            """
        )
    return (
        '<details class="result-evidence" open>'
        '<summary class="provenance-label">'
        f'Evidence (<span data-evidence-count>{len(items)}</span>)'
        "</summary>"
        f'<ul class="evidence-list">{"".join(items)}</ul>'
        "</details>"
    )


def _result_cards(
    results: list[Mapping],
    *,
    evidence_by_result: Mapping[str, list[Mapping]],
    entities_by_result: Mapping[str, list[Mapping]],
    graph_entities: list[Mapping],
    url_analyses_by_result: Mapping[str, list[Mapping]],
    monitors_by_result: Mapping[str, Mapping],
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not results:
        return """
            <div class="investigation-empty">
                No page has been explicitly saved to this investigation yet.
            </div>
        """

    cards = []
    disabled = " disabled" if read_only else ""
    for result in results:
        result_id = str(result.get("id", ""))
        title = str(result.get("title") or result.get("url") or "Untitled result")
        description = str(result.get("description", ""))
        url = str(result.get("url", ""))
        result_captures = evidence_by_result.get(result_id, [])
        is_imported = url.startswith(_LOCAL_FILE_URL_PREFIX) or any(
            str(capture.get("capture_kind", "") or "") == "imported"
            for capture in result_captures
        )
        # Imported files without a source URL use a synthetic, unreachable URL.
        # Point the title at the local file instead so it can be opened.
        title_href = url
        compact_url = _compact_url(url)
        if url.startswith(_LOCAL_FILE_URL_PREFIX):
            imported_view = next(
                (
                    view
                    for capture in result_captures
                    if (view := _imported_artifact_view(
                        capture, output_dir, base_dir
                    ))
                ),
                None,
            )
            if imported_view and imported_view["href"]:
                title_href = imported_view["href"]
                compact_url = "Imported document"
        type_badge = (
            '<span class="result-type-badge">Imported document</span>'
            if is_imported
            else ""
        )
        wayback_url = (
            ""
            if url.startswith(_LOCAL_FILE_URL_PREFIX)
            else _wayback_url(url)
        )
        wayback_control = (
            f'<a class="icon-action icon-action--frame" href="{_html(wayback_url)}" '
            'target="_blank" rel="noopener noreferrer" '
            'title="Open Wayback Machine" aria-label="Open Wayback Machine">'
            f'{_icon("archive")}</a>'
            if wayback_url
            else ""
        )
        sources = [str(item) for item in result.get("sources", []) if str(item).strip()]
        discovery_sources = [
            str(item)
            for item in result.get("discovery_sources", [])
            if str(item).strip()
        ]
        filter_sources = sorted(
            set([*sources, *discovery_sources]),
            key=str.casefold,
        )
        tags = [str(item) for item in result.get("tags", []) if str(item).strip()]
        notes = str(result.get("notes", ""))
        status = str(result.get("analyst_status", "a_verifier"))
        favorite = bool(result.get("favorite", False))
        latest_observed = str(result.get("latest_observed_at", ""))
        search_text = " ".join(
            [title, description, url, notes, *filter_sources, *tags]
        ).casefold()
        source_filter = "|" + "|".join(
            source.casefold() for source in filter_sources
        ) + "|"
        tag_filter = "|" + "|".join(tag.casefold() for tag in tags) + "|"
        favorite_checked = " checked" if favorite else ""
        tag_markup = "".join(
            f'<span class="result-tag">{_html(tag)}</span>' for tag in tags
        )
        monitor = monitors_by_result.get(result_id)
        if monitor:
            monitor_control = (
                '<span class="meta-pill">Monitoring</span>'
                '<button type="button" class="icon-action icon-action--frame stop-page-monitor" '
                f'data-monitor-id="{_html(monitor.get("id", ""))}" '
                'title="Stop monitoring" aria-label="Stop monitoring" '
                f"{disabled}>{_icon('activity')}</button>"
            )
        else:
            monitor_control = (
                '<button type="button" class="icon-action icon-action--frame start-page-monitor" '
                'title="Monitor changes" aria-label="Monitor changes" '
                f"{disabled}>{_icon('activity')}</button>"
            )
        cards.append(
            f"""
            <article
                id="result-{_html(result_id)}"
                class="investigation-result"
                data-result-id="{_html(result_id)}"
                data-search="{_html(search_text)}"
                data-status="{_html(status)}"
                data-sources="{_html(source_filter)}"
                data-tags="{_html(tag_filter)}"
                data-observed="{_html(latest_observed[:10])}"
                data-favorite="{"1" if favorite else "0"}"
                data-imported="{"1" if is_imported else "0"}"
            >
                <div class="result-heading">
                    <div class="result-title-block">
                        <a
                            class="result-title"
                            href="{_html(title_href)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >{_html(title)}</a>
                        <div class="result-url" title="{_html(compact_url if is_imported else url)}">
                            {_html(compact_url)}
                        </div>
                        {type_badge}
                    </div>
                    <div class="result-review-controls">
                        {wayback_control}
                        {monitor_control}
                        <label
                            class="favorite-toggle"
                            title="Add or remove this page from favorites"
                        >
                            <input
                                class="sr-only"
                                type="checkbox"
                                data-result-favorite
                                aria-label="Favorite"
                                {favorite_checked}{disabled}
                            >
                            <span class="favorite-star" aria-hidden="true"></span>
                        </label>
                        <label class="status-control">
                            <span class="sr-only">Analyst status</span>
                            <select data-result-status{disabled}>
                                {_status_options(status)}
                            </select>
                        </label>
                        <button
                            type="button"
                            class="icon-action icon-action--danger remove-saved-page"
                            title="Remove this saved page from the investigation"
                            aria-label="Remove this saved page from the investigation"
                            {disabled}
                        >{_icon("trash")}</button>
                    </div>
                </div>
                <div
                    id="result-body-{_html(result_id)}"
                    class="result-body"
                >
                    <p class="result-description">{_html(description)}</p>
                    <div class="result-metadata">
                        <span>{int(result.get("observation_count", 0) or 0)} observation(s)</span>
                        <span>First seen {_local_datetime(result.get("first_observed_at"))}</span>
                        <span>Last seen {_local_datetime(latest_observed)}</span>
                    </div>
                    <div class="result-tags" data-result-tags-display>
                        {tag_markup}
                    </div>
                    <textarea data-result-notes hidden>{_html(notes)}</textarea>
                    <input
                        type="hidden"
                        data-result-tags
                        value="{_html(", ".join(tags))}"
                    >
                </div>
            </article>
            """
        )
    return "".join(cards)


def _page_monitor_cards(
    monitors: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not monitors:
        return """
            <div class="investigation-empty">
                No page is monitored. Enable monitoring from a saved page,
                then use the HTML archive button while browsing it.
            </div>
        """

    labels = {
        "unchanged": "No content change",
        "minor_change": "Minor change",
        "changed": "Significant change",
        "inconclusive": "Inconclusive",
    }
    cards = []
    disabled = " disabled" if read_only else ""
    for monitor in monitors:
        report_path = _resolve_runtime_path(
            monitor.get("comparison_report_path"),
            base_dir,
        )
        report_link = (
            f'<a class="secondary-link" '
            f'href="{_html(_relative_href(report_path, output_dir))}" '
            'target="_blank" rel="noopener noreferrer">Open comparison</a>'
            if report_path is not None
            else '<span>Archive the page twice to generate a comparison.</span>'
        )
        status = str(monitor.get("comparison_status", "") or "")
        similarity = monitor.get("comparison_similarity")
        similarity_text = (
            f"{float(similarity) * 100:.2f}% text similarity"
            if similarity is not None
            else ""
        )
        cards.append(
            f"""
            <article
                class="page-monitor-card"
                data-page-monitor-id="{_html(monitor.get("id", ""))}"
            >
                <div>
                    <a
                        class="result-title"
                        href="{_html(monitor.get("result_url", ""))}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >{_html(monitor.get("result_title") or monitor.get("result_url"))}</a>
                    <div class="result-url">{_html(monitor.get("result_url", ""))}</div>
                </div>
                <div class="page-monitor-summary">
                    <span class="meta-pill">
                        {int(monitor.get("archive_count", 0) or 0)} archive(s)
                    </span>
                    <strong>{_html(labels.get(status, "Waiting for baseline"))}</strong>
                    <span>{_html(similarity_text)}</span>
                    {report_link}
                </div>
                <button
                    type="button"
                    class="danger-button stop-page-monitor"
                    data-monitor-id="{_html(monitor.get("id", ""))}"
                    {disabled}
                >Stop monitoring</button>
            </article>
            """
        )
    return "".join(cards)


def _search_rows(
    searches: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
) -> str:
    if not searches:
        return """
            <tr>
                <td colspan="5" class="empty-row">No search attached.</td>
            </tr>
        """

    rows = []
    for search in searches:
        report_path = _resolve_runtime_path(search.get("report_path"), base_dir)
        report_link = (
            f'<a href="{_html(_relative_href(report_path, output_dir))}" '
            'target="_blank" rel="noopener noreferrer">Open report</a>'
            if report_path is not None
            else "No report"
        )
        enabled_engines = [
            str(name).title()
            for name, enabled in search.get("engines", {}).items()
            if enabled
        ]
        query = search.get("original_query") or search.get("parsed_query") or "Filter-only search"
        rows.append(
            f"""
            <tr>
                <td>{_local_datetime(search.get("started_at"))}</td>
                <td>{_html(query)}</td>
                <td>{_html(", ".join(enabled_engines) or "Legacy")}</td>
                <td>{int(search.get("result_count", 0) or 0)}</td>
                <td>{report_link}</td>
            </tr>
            """
        )
    return "".join(rows)


def _export_cards(
    exports: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not exports:
        return """
            <div class="investigation-empty">
                No ZeroNeurone export has been generated yet.
            </div>
        """

    cards = []
    disabled = " disabled" if read_only else ""
    for export in exports:
        links = []
        for key, label in (
            ("archive_path", "ZeroNeurone ZIP"),
            ("dossier_path", "Dossier JSON"),
            ("graphml_path", "GraphML"),
            ("csv_path", "ZeroNeurone CSV"),
            ("nodes_csv_path", "Nodes CSV"),
            ("edges_csv_path", "Edges CSV"),
            ("manifest_path", "Manifest"),
        ):
            path = _resolve_runtime_path(export.get(key), base_dir)
            if path is None:
                continue
            links.append(
                f'<a class="secondary-link" '
                f'href="{_html(_relative_href(path, output_dir))}" '
                'target="_blank" rel="noopener noreferrer">'
                f"{_html(label)}</a>"
            )
        options = ["curated entities or validated candidates"]
        if export.get("include_unreviewed"):
            options.append("all entity review states")
        if export.get("include_evidence"):
            options.append("evidence assets")
        cards.append(
            f"""
            <article
                class="investigation-export-card"
                data-export-id="{_html(export.get("id", ""))}"
            >
                <div>
                    <strong>ZeroNeurone export</strong>
                    <span>{_local_datetime(export.get("generated_at"))}</span>
                </div>
                <div class="export-summary">
                    <span>{int(export.get("node_count", 0) or 0)} nodes</span>
                    <span>{int(export.get("edge_count", 0) or 0)} links</span>
                    <span>{int(export.get("asset_count", 0) or 0)} assets</span>
                    <span>{_html(", ".join(options))}</span>
                </div>
                <div class="export-links">
                    {"".join(links)}
                    <button
                        type="button"
                        class="danger-link delete-export"
                        {disabled}
                    >Delete export</button>
                </div>
            </article>
            """
        )
    return "".join(cards)


def _unassigned_options(searches: list[Mapping]) -> str:
    options = ['<option value="">Select a search</option>']
    for search in searches:
        query = search.get("original_query") or search.get("parsed_query") or "Filter-only search"
        label = (
            f"{_display_datetime(search.get('started_at'))} - "
            f"{query} ({int(search.get('result_count', 0) or 0)} results)"
        )
        options.append(
            f'<option value="{_html(search.get("id", ""))}">{_html(label)}</option>'
        )
    return "".join(options)


def generate_investigation_page(
    workspace: Mapping,
    output_path: Path,
    *,
    base_dir: Path,
    history_report_path: Path,
) -> str:
    investigation = workspace["investigation"]
    results = list(workspace.get("results", []))
    evidence = list(workspace.get("evidence", []))
    entities = list(workspace.get("entities", []))
    graph_entities = list(workspace.get("graph_entities", []))
    exports = list(workspace.get("exports", []))
    url_analyses = list(workspace.get("url_analyses", []))
    searches = list(workspace.get("searches", []))
    page_monitors = list(workspace.get("page_monitors", []))
    unassigned_searches = list(workspace.get("unassigned_searches", []))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir = output_path.parent

    asset_prefix = _relative_href(base_dir, output_dir).rstrip("/") + "/"
    home_href = _relative_href(base_dir / "index.html", output_dir)
    history_href = _relative_href(history_report_path, output_dir)
    read_only = investigation.get("status") != "active"
    results_by_id = {
        str(result.get("id", "") or ""): result
        for result in results
    }
    all_sources = sorted(
        {
            str(source)
            for result in results
            for source in (
                *result.get("sources", []),
                *result.get("discovery_sources", []),
            )
            if str(source).strip()
        },
        key=str.casefold,
    )
    all_tags = sorted(
        {
            str(tag)
            for result in results
            for tag in result.get("tags", [])
            if str(tag).strip()
        },
        key=str.casefold,
    )
    suggested_tags = sorted(
        {
            str(tag)
            for source in (
                [investigation],
                results,
                entities,
                graph_entities,
            )
            for item in source
            for tag in item.get("tags", [])
            if str(tag).strip()
        },
        key=str.casefold,
    )
    source_options = "".join(
        f'<option value="{_html(source.casefold())}">{_html(source)}</option>'
        for source in all_sources
    )
    tag_options = "".join(
        f'<option value="{_html(tag.casefold())}">{_html(tag)}</option>'
        for tag in all_tags
    )
    tag_datalist_options = _tag_datalist_options(suggested_tags)
    property_suggestion_keys = _property_suggestion_keys(entities, graph_entities)
    source_property_suggestion_keys = _source_property_suggestion_keys(entities)
    used_property_suggestion_keys = _used_property_suggestion_keys(
        entities,
        graph_entities,
    )
    scoped_property_suggestions_by_result: dict[str, tuple[str, list[str]]] = {}
    for result in results:
        result_id = str(result.get("id", "") or "")
        scoped_keys = _scoped_property_suggestion_keys(
            result,
            graph_entities,
            used_property_suggestion_keys,
        )
        if scoped_keys:
            scoped_property_suggestions_by_result[result_id] = (
                f"property-suggestions-{_dom_id_fragment(result_id)}",
                scoped_keys,
            )
    scoped_property_datalists = "".join(
        f'<datalist id="{_html(datalist_id)}">'
        f"{_property_datalist_options(keys)}</datalist>"
        for datalist_id, keys in scoped_property_suggestions_by_result.values()
    )
    investigation_tags = "".join(
        f'<span class="result-tag">{_html(tag)}</span>'
        for tag in investigation.get("tags", [])
    )
    archive_notice = (
        '<p class="archive-notice">This investigation is archived and read-only.</p>'
        if read_only
        else ""
    )
    attach_disabled = " disabled" if read_only or not unassigned_searches else ""
    evidence_by_result: dict[str, list[Mapping]] = {}
    for capture in evidence:
        evidence_by_result.setdefault(
            str(capture.get("result_id", "")),
            [],
        ).append(capture)
    entities_by_result: dict[str, list[Mapping]] = {}
    for entity in entities:
        entities_by_result.setdefault(
            str(entity.get("result_id", "")),
            [],
        ).append(entity)
    url_analyses_by_result: dict[str, list[Mapping]] = {}
    for analysis in url_analyses:
        url_analyses_by_result.setdefault(
            str(analysis.get("result_id", "")),
            [],
        ).append(analysis)
    protected_capture_ids = _protected_capture_ids(
        graph_entities,
        entities,
        evidence_by_result,
    )
    monitors_by_result = {
        str(monitor.get("result_id", "")): monitor
        for monitor in page_monitors
    }

    pages_to_review = sum(
        1
        for item in results
        if str(item.get("analyst_status") or "a_verifier") == "a_verifier"
    )
    monitored_changes = sum(
        1
        for monitor in page_monitors
        if monitor.get("comparison_status") == "changed"
    )
    proposed_entities = sum(
        1 for entity in entities if entity.get("status") == "proposed"
    )
    focus_summary = (
        '<div class="focus-summary" aria-label="Investigation next actions">'
        f'<div class="focus-item"><strong>{pages_to_review}</strong>'
        "<span>pages to review</span>"
        "<small>Triage saved pages before exporting.</small></div>"
        f'<div class="focus-item"><strong>{monitored_changes}</strong>'
        "<span>monitored changes</span>"
        "<small>Open changed pages and compare archives.</small></div>"
        f'<div class="focus-item"><strong>{proposed_entities}</strong>'
        "<span>proposed entities</span>"
        "<small>Validate or attach extracted identifiers.</small></div>"
        f'<div class="focus-item"><strong>{len(evidence)}</strong>'
        "<span>captures</span>"
        "<small>Evidence files attached to saved pages.</small></div>"
        "</div>"
    )

    inspector_panel_items = []
    for result in results:
        result_id = str(result.get("id", ""))
        result_entities = entities_by_result.get(result_id, [])
        result_evidence = evidence_by_result.get(result_id, [])
        local_file_href = ""
        if str(result.get("url", "")).startswith(_LOCAL_FILE_URL_PREFIX):
            imported_view = next(
                (
                    view
                    for capture in result_evidence
                    if (view := _imported_artifact_view(
                        capture, output_dir, base_dir
                    ))
                ),
                None,
            )
            if imported_view:
                local_file_href = imported_view["href"]
        inspector_panel_items.append(
            _inspector_panel(
                result,
                is_monitored=result_id in monitors_by_result,
                local_file_href=local_file_href,
                details_markup=(
                    _page_linked_entities_markup(
                        result,
                        graph_entities,
                        result_entities,
                    )
                    + _entity_markup(
                        result_entities,
                        graph_entities=graph_entities,
                        property_suggestions_id=(
                            scoped_property_suggestions_by_result.get(
                                result_id,
                                ("property-suggestions", []),
                            )[0]
                        ),
                        page_property_suggestions_id=(
                            "property-suggestions-site-web"
                        ),
                        has_extractable_archive=_has_extractable_archive(
                            result_evidence
                        ),
                        read_only=read_only,
                    )
                    + _evidence_markup(
                        result_evidence,
                        output_dir=output_dir,
                        base_dir=base_dir,
                        protected_capture_ids=protected_capture_ids,
                        read_only=read_only,
                    )
                ),
            )
        )
    inspector_panels = "".join(inspector_panel_items)

    entity_inspector_cards = _graph_entities_markup(
        graph_entities,
        results_by_id,
        entities=entities,
        evidence_by_result=evidence_by_result,
        output_dir=output_dir,
        base_dir=base_dir,
        read_only=read_only,
    )

    metric_items = (
        ("⌕", len(searches), "Searches"),
        ("▣", len(results), "Saved pages"),
        ("◇", len(graph_entities), "Entities"),
        ("★", sum(1 for item in results if item.get("favorite")), "Favorites"),
        (
            "✓",
            sum(1 for item in results if item.get("analyst_status") == "confirme"),
            "Confirmed pages",
        ),
    )
    metrics_markup = "".join(
        (
            '<span class="metric-chip" '
            f'title="{_html(label)}: {count}" '
            f'aria-label="{_html(label)}: {count}">'
            f'<span class="metric-chip__icon" aria-hidden="true">{_html(icon)}</span>'
            f'<strong>{count}</strong>'
            '</span>'
        )
        for icon, count, label in metric_items
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_html(investigation.get("title"))} - Synthesix</title>
    <link rel="icon" href="{asset_prefix}assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="{asset_prefix}theme.css">
    <script src="{asset_prefix}theme.js"></script>
    <script src="{asset_prefix}i18n.js"></script>
</head>
<body>
    <main class="app app--wide app--workspace">
        <datalist id="tag-suggestions">
            {tag_datalist_options}
        </datalist>
        <datalist id="entity-tagsets">
            {"".join(f'<option value="{_html(tag)}"></option>' for tag in ZERONEURONE_TAGSETS)}
        </datalist>
        <datalist id="property-suggestions">
            {_property_datalist_options(property_suggestion_keys)}
        </datalist>
        <datalist id="property-suggestions-site-web">
            {_property_datalist_options(source_property_suggestion_keys)}
        </datalist>
        {scoped_property_datalists}
        <header class="topbar investigation-topbar">
            <div class="brand">
                <img class="brand-logo" src="{asset_prefix}assets/synthesix-mark.svg" alt="">
                <div class="brand-copy">
                    <h1 class="brand-name">Synthesix</h1>
                    <span class="brand-subtitle">Investigation workspace</span>
                </div>
            </div>
            <div class="top-actions">
                <button type="button" class="nav-link" data-refresh-investigation>Refresh</button>
                <a href="{_html(home_href)}" data-home-link class="nav-link">Search</a>
                <a href="{_html(history_href)}" class="nav-link">History</a>
            </div>
        </header>
        <p id="investigation-action-status" class="action-status"></p>

        <nav class="investigation-nav" aria-label="Investigation sections">
            <a href="#overview">Overview</a>
            <a href="#entities">Entities</a>
            <a href="#saved-pages">Saved pages</a>
            <a href="#page-monitoring">Monitoring</a>
            <a href="#exports">Exports</a>
            <a href="#attach-search">Attach search</a>
            <a href="#search-runs">Search runs</a>
        </nav>

        <div class="workspace" data-rail-collapsed="false">
        <div class="workspace__main">
        <section id="overview" class="investigation-overview">
            <div>
                <div class="overview-kicker">
                    <p class="section-eyebrow">Investigation</p>
                    <div class="investigation-metrics" aria-label="Investigation metrics">
                        {metrics_markup}
                    </div>
                </div>
                <h2 class="page-title">{_html(investigation.get("title"))}</h2>
                <p class="investigation-reference">{_html(investigation.get("reference"))}</p>
                <p class="investigation-description">{_html(investigation.get("description"))}</p>
                <div class="result-tags">{investigation_tags}</div>
                {archive_notice}
            </div>
        </section>

        <section
            id="entities"
            class="investigation-section"
            aria-label="Entités"
        >
            <div class="section-header">
                <div>
                    <h3>Entités</h3>
                </div>
                <div class="section-header__actions">
                    <span id="visible-entity-count" class="meta-pill">{len(graph_entities)} entités</span>
                    <button
                        id="open-entity-create"
                        type="button"
                        class="primary-button primary-button--compact"
                        aria-controls="graph-entity-create-form"
                    >+ Entité</button>
                </div>
            </div>
            <div class="entity-list-tools">
                <label class="entity-search">
                    <span class="sr-only">Rechercher une entité</span>
                    <span class="entity-search__icon">{_icon("search")}</span>
                    <input
                        id="entity-filter-query"
                        type="search"
                        placeholder="Filtrer les entités..."
                        autocomplete="off"
                    >
                </label>
            </div>
            <div class="graph-entity-list">
                {_entity_rows_markup(
                    graph_entities,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section id="import-file" class="investigation-section">
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Sources externes</p>
                    <h3>Importer un fichier</h3>
                </div>
            </div>
            <div class="import-dropzone" data-import-dropzone>
                <p class="import-dropzone__hint">Glissez un fichier (PDF, image, audio, vidéo, document…) ici ou cliquez pour le choisir.</p>
                <input
                    type="url"
                    class="import-dropzone__url"
                    data-import-url
                    placeholder="URL source (optionnel — laisser vide si externe)"
                    {"disabled" if read_only else ""}
                >
                <input
                    type="file"
                    class="import-dropzone__file"
                    data-import-file
                    hidden
                    {"disabled" if read_only else ""}
                >
            </div>
            <p class="import-status" data-import-status aria-live="polite"></p>
        </section>

        <section
            id="saved-pages"
            class="investigation-section"
            aria-label="Saved investigation pages"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Analyst selection</p>
                    <h3>Saved pages</h3>
                </div>
                <div class="section-header__actions">
                    <span id="visible-result-count" class="meta-pill">{len(results)} visibles</span>
                    <button
                        id="toggle-result-filters"
                        type="button"
                        class="icon-action icon-action--frame"
                        aria-label="Afficher les filtres"
                        aria-controls="result-filters"
                        aria-expanded="false"
                        title="Afficher les filtres"
                    >{_icon("search")}</button>
                </div>
            </div>
            <div id="result-filters" class="investigation-filters" hidden>
                <label class="filter-wide">
                    Search
                    <input id="result-filter-query" type="search" placeholder="Title, URL, notes, tags...">
                </label>
                <label>
                    Status
                    <select id="result-filter-status">
                        <option value="">All statuses</option>
                        <option value="a_verifier">To verify</option>
                        <option value="pertinent">Relevant</option>
                        <option value="confirme">Confirmed</option>
                        <option value="ecarte">Discarded</option>
                    </select>
                </label>
                <label>
                    Source
                    <select id="result-filter-source">
                        <option value="">All sources</option>
                        {source_options}
                    </select>
                </label>
                <label>
                    Tag
                    <select id="result-filter-tag">
                        <option value="">All tags</option>
                        {tag_options}
                    </select>
                </label>
                <label>
                    Type
                    <select id="result-filter-type">
                        <option value="">All types</option>
                        <option value="page">Web pages</option>
                        <option value="imported">Imported documents</option>
                    </select>
                </label>
                <label>
                    Observed after
                    <input id="result-filter-after" type="date">
                </label>
                <label>
                    Observed before
                    <input id="result-filter-before" type="date">
                </label>
                <label class="favorite-filter">
                    <input id="result-filter-favorite" type="checkbox">
                    Favorites only
                </label>
                <button id="clear-result-filters" type="button" class="secondary-button">Clear filters</button>
            </div>
            <div id="investigation-results" class="investigation-results">
                {_result_cards(
                    results,
                    evidence_by_result=evidence_by_result,
                    entities_by_result=entities_by_result,
                    graph_entities=graph_entities,
                    url_analyses_by_result=url_analyses_by_result,
                    monitors_by_result=monitors_by_result,
                    output_dir=output_dir,
                    base_dir=base_dir,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section
            id="page-monitoring"
            class="investigation-section"
            aria-label="Page monitoring"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Temporal comparison</p>
                    <h3>Page monitoring</h3>
                </div>
                <span class="meta-pill" data-monitor-count>{len(page_monitors)} monitored</span>
            </div>
            <p class="session-note">
                Monitoring compares normalized text from explicit HTML archives.
                Screenshots are not compared automatically to avoid noisy alerts
                from animations, maps, ads, or cursor changes. Open a monitored
                page and use the HTML archive button to create the next snapshot.
            </p>
            <div class="page-monitor-list">
                {_page_monitor_cards(
                    page_monitors,
                    output_dir=output_dir,
                    base_dir=base_dir,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section
            id="exports"
            class="investigation-section"
            aria-label="ZeroNeurone exports"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Interoperability</p>
                    <h3>ZeroNeurone export</h3>
                </div>
                <span class="meta-pill" data-export-count>{len(exports)} export(s)</span>
            </div>
            <form id="zeroneurone-export-form" class="export-form">
                <label>
                    <input id="export-include-evidence" type="checkbox">
                    Include evidence files as assets
                </label>
                <label>
                    <input id="export-include-unreviewed" type="checkbox">
                    Include unreviewed candidates in the legacy fallback
                </label>
                <button type="submit" class="primary-button">
                    Export GraphML and CSV
                </button>
            </form>
            <p class="session-note">
                When investigation entities exist, they define the graph and
                linked pages become source properties. Otherwise, Synthesix uses
                the legacy saved-page and validated-candidate graph.
            </p>
            <div class="investigation-export-list">
                {_export_cards(
                    exports,
                    output_dir=output_dir,
                    base_dir=base_dir,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section
            id="attach-search"
            class="investigation-section"
            aria-label="Attach existing search"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Existing collection</p>
                    <h3>Attach a previous search</h3>
                </div>
            </div>
            <form id="attach-search-form" class="attach-search-form">
                <label>
                    Unassigned search
                    <select id="unassigned-search"{attach_disabled}>
                        {_unassigned_options(unassigned_searches)}
                    </select>
                </label>
                <button type="submit" class="primary-button"{attach_disabled}>Attach</button>
            </form>
            <p class="session-note">
                Attaching a search preserves its original query, report, and observations.
                Its results are not added to the saved pages automatically.
            </p>
        </section>

        <section
            id="search-runs"
            class="investigation-section"
            aria-label="Investigation searches"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Provenance</p>
                    <h3>Search runs</h3>
                </div>
            </div>
            <div class="table-shell investigation-table-shell">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Query</th>
                            <th>Engines</th>
                            <th>Results</th>
                            <th>Report</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_search_rows(searches, output_dir=output_dir, base_dir=base_dir)}
                    </tbody>
                </table>
            </div>
        </section>
        </div>
        <div
            class="workspace__resizer"
            data-rail-resizer
            role="separator"
            aria-orientation="vertical"
            aria-label="Resize workspace panel"
            title="Drag to resize · double-click to reset"
        ></div>
        <aside class="workspace__rail" id="investigation-rail" aria-label="Workspace panel">
            <div class="workspace__rail-header">
                <span class="workspace__rail-title">Workspace</span>
                <button
                    type="button"
                    class="workspace__rail-toggle"
                    data-rail-toggle
                    aria-expanded="true"
                    aria-controls="investigation-rail-body"
                    title="Collapse panel"
                    aria-label="Collapse panel"
                >&rsaquo;</button>
            </div>
            <div class="workspace__rail-body" id="investigation-rail-body">
                <div class="rail-section" id="rail-next-actions">
                    <p class="rail-section__title">Next actions</p>
                    {focus_summary}
                </div>
                <div class="rail-section inspector" id="inspector-detail" hidden>
                    <div class="inspector-head">
                        <span
                            class="save-indicator"
                            data-save-indicator
                            role="status"
                            aria-live="polite"
                        >{_icon("check")} Enregistré</span>
                    </div>
                    <form
                        id="graph-entity-create-form"
                        class="graph-entity-create-form graph-entity-create-panel entity-section"
                        data-inspector-create-entity
                        hidden
                    >
                        <div class="entity-section__head">
                            <span class="entity-section__title">Nouvelle entité</span>
                        </div>
                        <label class="entity-field">
                            <span class="entity-field__label">Nom</span>
                            <input
                                id="new-graph-entity-label"
                                type="text"
                                maxlength="200"
                                placeholder="Nom de l'entité"
                                aria-label="Entity name"
                                required
                                {"disabled" if read_only else ""}
                            >
                        </label>
                        <label class="entity-field">
                            <span class="entity-field__label">Tags</span>
                            <div class="tag-editor" data-create-tags-editor>
                                <div class="tag-editor__chips" data-create-tags-chips></div>
                                <input
                                    id="new-graph-entity-tags"
                                    type="text"
                                    class="tag-editor__input"
                                    list="tag-suggestions"
                                    placeholder="Nouveau tag..."
                                    aria-label="Entity tags"
                                    {"disabled" if read_only else ""}
                                >
                            </div>
                        </label>
                        <label class="entity-field">
                            <span class="entity-field__label">Notes</span>
                            <textarea
                                id="new-graph-entity-notes"
                                rows="4"
                                maxlength="4000"
                                placeholder="Contexte utile..."
                                aria-label="Entity notes"
                                {"disabled" if read_only else ""}
                            ></textarea>
                        </label>
                        <button
                            type="submit"
                            class="primary-button"
                            {"disabled" if read_only else ""}
                        >Créer l'entité</button>
                    </form>
                    {inspector_panels}
                    {entity_inspector_cards}
                </div>
            </div>
        </aside>
        </div>
    </main>
    <script>
        (() => {{
            const investigationId = {json.dumps(str(investigation.get("id", "")))};
            // Persist the queue so a no-reload action (e.g. a delete) that is
            // still pending is not lost if the analyst refreshes the page.
            const actionQueueKey = `synthesix:action-queue:${{investigationId}}`;
            const loadActionQueue = () => {{
                try {{
                    const stored = JSON.parse(
                        localStorage.getItem(actionQueueKey) || "[]"
                    );
                    return Array.isArray(stored) ? stored : [];
                }} catch (_error) {{
                    return [];
                }}
            }};
            const actionQueue = loadActionQueue();
            const persistActionQueue = () => {{
                try {{
                    localStorage.setItem(
                        actionQueueKey, JSON.stringify(actionQueue)
                    );
                }} catch (_error) {{
                    // The queue still works in memory without persistence.
                }}
            }};
            const resultCards = Array.from(
                document.querySelectorAll(".investigation-result")
            );
            const filterIds = [
                "result-filter-query",
                "result-filter-status",
                "result-filter-source",
                "result-filter-tag",
                "result-filter-type",
                "result-filter-after",
                "result-filter-before",
                "result-filter-favorite"
            ];
            const resultFilters = document.getElementById("result-filters");
            const toggleResultFilters = document.getElementById(
                "toggle-result-filters"
            );

            toggleResultFilters?.addEventListener("click", () => {{
                const isHidden = Boolean(resultFilters?.hidden);
                if (resultFilters) {{
                    resultFilters.hidden = !isHidden;
                }}
                toggleResultFilters.setAttribute(
                    "aria-expanded",
                    String(isHidden)
                );
                toggleResultFilters.setAttribute(
                    "aria-label",
                    isHidden ? "Masquer les filtres" : "Afficher les filtres"
                );
                toggleResultFilters.title = (
                    isHidden ? "Masquer les filtres" : "Afficher les filtres"
                );
                if (isHidden) {{
                    document.getElementById("result-filter-query")?.focus();
                }}
            }});

            const queueAction = (action, payload = {{}}) => {{
                actionQueue.push({{ action, investigationId, ...payload }});
                persistActionQueue();
            }};
            const viewStateKey = `synthesix:view-state:${{investigationId}}`;
            const storeViewState = (state = {{}}) => {{
                try {{
                    localStorage.setItem(viewStateKey, JSON.stringify({{
                        scrollX: window.scrollX,
                        scrollY: window.scrollY,
                        ...state
                    }}));
                }} catch (_error) {{
                    // Refresh still works without restoring context.
                }}
            }};
            const clearViewState = () => {{
                try {{
                    localStorage.removeItem(viewStateKey);
                }} catch (_error) {{
                    // Nothing to clear when storage is unavailable.
                }}
            }};
            const loadViewState = () => {{
                try {{
                    const raw = localStorage.getItem(viewStateKey);
                    return raw ? JSON.parse(raw) : null;
                }} catch (_error) {{
                    return null;
                }}
            }};

            const formatLocalDatetimes = () => {{
                const formatter = new Intl.DateTimeFormat(undefined, {{
                    dateStyle: "medium",
                    timeStyle: "medium"
                }});
                document.querySelectorAll("time[data-local-datetime]").forEach(
                    (element) => {{
                        const rawValue = element.getAttribute("datetime") || "";
                        const normalizedValue = rawValue.replace(
                            /(\\.\\d{{3}})\\d+(?=(?:Z|[+-]\\d{{2}}:\\d{{2}})$)/,
                            "$1"
                        );
                        const parsed = new Date(normalizedValue);
                        if (Number.isNaN(parsed.getTime())) {{
                            return;
                        }}
                        element.textContent = formatter.format(parsed);
                        element.title = rawValue;
                    }}
                );
            }};

            window.synthesixPage = {{
                consumeAction() {{
                    const next = actionQueue.shift() || null;
                    persistActionQueue();
                    return next;
                }},
                setStatus(message, isError = false) {{
                    const status = document.getElementById(
                        "investigation-action-status"
                    );
                    status.textContent = String(message || "");
                    status.classList.toggle("is-error", Boolean(isError));
                }}
            }};
            formatLocalDatetimes();

            document.querySelectorAll("[data-home-link]").forEach((link) => {{
                link.addEventListener("click", (event) => {{
                    event.preventDefault();
                    queueAction("focus_home");
                }});
            }});

            document.querySelectorAll("[data-refresh-investigation]").forEach((button) => {{
                button.addEventListener("click", () => {{
                    queueAction("refresh_investigation");
                }});
            }});

            const resultPayload = (card) => ({{
                analyst_status: card.querySelector("[data-result-status]").value,
                favorite: card.querySelector("[data-result-favorite]").checked,
                notes: card.querySelector("[data-result-notes]").value.trim(),
                tags: card.querySelector("[data-result-tags]").value.trim()
            }});

            const saveResult = (card) => {{
                const payload = resultPayload(card);
                // Mirror favorite state on the card so the favorite filter and
                // metrics stay correct without a reload.
                card.dataset.favorite = payload.favorite ? "1" : "0";
                queueAction("update_investigation_result", {{
                    resultId: card.dataset.resultId,
                    result: payload
                }});
            }};

            const createEntityForm = document.getElementById(
                "graph-entity-create-form"
            );
            const createTagsHost = createEntityForm?.querySelector(
                "[data-create-tags-chips]"
            );
            const createTagInput = createEntityForm?.querySelector(
                "[data-create-tags-editor] input"
            );
            const gatherCreateTags = () => Array.from(
                createEntityForm?.querySelectorAll(".tag-chip") || []
            ).map((chip) => chip.dataset.tag).filter(Boolean);
            const addCreateTag = (value) => {{
                const tag = String(value || "").trim();
                if (!tag || !createTagsHost) {{
                    return;
                }}
                const exists = gatherCreateTags().some(
                    (existing) => existing.toLowerCase() === tag.toLowerCase()
                );
                if (exists) {{
                    return;
                }}
                const chip = document.createElement("span");
                chip.className = "tag-chip";
                chip.dataset.tag = tag;
                chip.textContent = tag;
                const remove = document.createElement("button");
                remove.type = "button";
                remove.className = "tag-chip__remove";
                remove.dataset.createTagRemove = "";
                remove.setAttribute("aria-label", "Remove tag");
                remove.textContent = "\\u00d7";
                chip.appendChild(remove);
                createTagsHost.appendChild(chip);
            }};
            const commitCreateTags = () => {{
                if (!createTagInput) {{
                    return;
                }}
                createTagInput.value.split(",").forEach(addCreateTag);
                createTagInput.value = "";
            }};
            createTagInput?.addEventListener("keydown", (event) => {{
                if (event.key === "Enter" || event.key === ",") {{
                    event.preventDefault();
                    commitCreateTags();
                }}
            }});
            createTagInput?.addEventListener("change", commitCreateTags);
            createTagInput?.addEventListener("blur", commitCreateTags);
            createTagsHost?.addEventListener("click", (event) => {{
                const button = event.target.closest("[data-create-tag-remove]");
                if (button) {{
                    button.closest(".tag-chip")?.remove();
                }}
            }});
            createEntityForm?.addEventListener(
                "submit",
                (event) => {{
                    event.preventDefault();
                    commitCreateTags();
                    const label = document.getElementById(
                        "new-graph-entity-label"
                    ).value.trim();
                    if (!label) {{
                        return;
                    }}
                    storeViewState({{ inspectorType: "create" }});
                    queueAction("create_graph_entity", {{
                        entity: {{
                            label,
                            tags: gatherCreateTags().join(", "),
                            notes: document.getElementById(
                                "new-graph-entity-notes"
                            ).value.trim()
                        }}
                    }});
                }}
            );

            const saveIndicator = document.querySelector(
                "[data-save-indicator]"
            );
            let saveIndicatorTimer = null;
            const flashSaved = () => {{
                if (!saveIndicator) {{
                    return;
                }}
                saveIndicator.classList.add("is-visible");
                if (saveIndicatorTimer) {{
                    clearTimeout(saveIndicatorTimer);
                }}
                saveIndicatorTimer = setTimeout(() => {{
                    saveIndicator.classList.remove("is-visible");
                }}, 1500);
            }};
            const bindGraphPropertyDelete = (card, button, entityId) => {{
                button.addEventListener("click", () => {{
                    if (
                        confirm(
                            "Supprimer cette propriété ? Les propriétés "
                            + "extraites liées aux pages enregistrées "
                            + "seront aussi supprimées."
                        )
                    ) {{
                        queueAction("delete_graph_entity_property", {{
                            entityId,
                            key: button.dataset.propertyKey
                        }});
                        removeLinkedExtractedRows(
                            entityId,
                            button.dataset.propertyKey
                        );
                        button.closest("li")?.remove();
                        flashSaved();
                    }}
                }});
            }};
            const appendGraphPropertyRow = (card, entityId, key, value) => {{
                const list = card.querySelector(".graph-property-list");
                if (!list) {{
                    return;
                }}
                const existingButton = Array.from(
                    list.querySelectorAll(".delete-graph-property")
                ).find((button) => button.dataset.propertyKey === key);
                if (existingButton) {{
                    const existingValue = existingButton
                        .closest("li")
                        ?.querySelector(".graph-property-value");
                    if (existingValue) {{
                        existingValue.textContent = value;
                    }}
                    return;
                }}
                list.querySelector(".entity-empty")?.remove();
                const item = document.createElement("li");
                const head = document.createElement("div");
                head.className = "graph-property-head";
                const keyWrap = document.createElement("span");
                keyWrap.className = "graph-property-key";
                const strong = document.createElement("strong");
                strong.textContent = key;
                keyWrap.appendChild(strong);
                const actions = document.createElement("span");
                actions.className = "graph-property-actions";
                const remove = document.createElement("button");
                remove.type = "button";
                remove.className = (
                    "icon-action icon-action--danger delete-graph-property"
                );
                remove.dataset.propertyKey = key;
                remove.title = "Remove property";
                remove.setAttribute("aria-label", "Remove property");
                remove.innerHTML = {json.dumps(_icon("trash"))};
                actions.appendChild(remove);
                head.appendChild(keyWrap);
                head.appendChild(actions);
                const valueNode = document.createElement("span");
                valueNode.className = "graph-property-value";
                valueNode.textContent = value;
                item.appendChild(head);
                item.appendChild(valueNode);
                list.appendChild(item);
                bindGraphPropertyDelete(card, remove, entityId);
            }};

            document.querySelectorAll(".graph-entity-card").forEach((card) => {{
                const entityId = card.dataset.graphEntityId;
                const chipsHost = card.querySelector("[data-tags-chips]");
                const gatherTags = () => Array.from(
                    card.querySelectorAll(".tag-chip")
                ).map((chip) => chip.dataset.tag).filter(Boolean);
                const saveEntity = () => {{
                    const label = card.querySelector(
                        "[data-graph-entity-label]"
                    ).value.trim();
                    const notes = card.querySelector(
                        "[data-graph-entity-notes]"
                    ).value.trim();
                    const tags = gatherTags().join(", ");
                    queueAction("update_graph_entity", {{
                        entityId,
                        entity: {{ label, tags, notes }}
                    }});
                    flashSaved();
                    // Mirror the edit in the compact row without a reload.
                    const row = document.querySelector(
                        `[data-entity-select="${{entityId}}"]`
                    );
                    if (row) {{
                        const rowLabel = row.querySelector(".entity-row__label");
                        if (rowLabel && label) {{
                            rowLabel.textContent = label;
                        }}
                        row.dataset.entitySearch = [
                            label,
                            gatherTags().join(" "),
                            row.dataset.entitySearch || ""
                        ].join(" ").toLowerCase();
                        const rowTags = row.querySelector(".entity-row__tags");
                        if (rowTags) {{
                            rowTags.replaceChildren();
                            gatherTags().forEach((tag) => {{
                                const chip = document.createElement("span");
                                chip.className = "result-tag";
                                chip.textContent = tag;
                                rowTags.appendChild(chip);
                            }});
                        }}
                    }}
                }};
                card.querySelector("[data-graph-entity-label]")
                    ?.addEventListener("blur", saveEntity);
                card.querySelector("[data-graph-entity-notes]")
                    ?.addEventListener("blur", saveEntity);
                const addTag = (value) => {{
                    const tag = value.trim();
                    if (!tag || !chipsHost) {{
                        return;
                    }}
                    const exists = gatherTags().some(
                        (existing) => existing.toLowerCase() === tag.toLowerCase()
                    );
                    if (exists) {{
                        return;
                    }}
                    const chip = document.createElement("span");
                    chip.className = "tag-chip";
                    chip.dataset.tag = tag;
                    chip.textContent = tag;
                    const remove = document.createElement("button");
                    remove.type = "button";
                    remove.className = "tag-chip__remove";
                    remove.dataset.tagRemove = "";
                    remove.setAttribute("aria-label", "Remove tag");
                    remove.textContent = "\\u00d7";
                    chip.appendChild(remove);
                    chipsHost.appendChild(chip);
                    saveEntity();
                }};
                const tagInput = card.querySelector("[data-tag-input]");
                if (tagInput) {{
                    const commitTag = () => {{
                        if (tagInput.value.trim()) {{
                            addTag(tagInput.value);
                            tagInput.value = "";
                        }}
                    }};
                    tagInput.addEventListener("keydown", (event) => {{
                        if (event.key === "Enter") {{
                            event.preventDefault();
                            commitTag();
                        }}
                    }});
                    tagInput.addEventListener("change", commitTag);
                    tagInput.addEventListener("blur", commitTag);
                }}
                card.addEventListener("click", (event) => {{
                    const removeBtn = event.target.closest("[data-tag-remove]");
                    if (!removeBtn) {{
                        return;
                    }}
                    const chip = removeBtn.closest(".tag-chip");
                    if (chip) {{
                        chip.remove();
                        saveEntity();
                    }}
                }});
                card.querySelector(".delete-graph-entity")?.addEventListener(
                    "click",
                    () => {{
                        if (confirm("Delete this entity from the final graph?")) {{
                            queueAction("delete_graph_entity", {{ entityId }});
                        }}
                    }}
                );
                card.querySelectorAll(".delete-graph-property").forEach(
                    (button) => bindGraphPropertyDelete(card, button, entityId)
                );
                card.querySelector("[data-add-property]")
                    ?.addEventListener("submit", (event) => {{
                        event.preventDefault();
                        const keyInput = card.querySelector(
                            "[data-add-property-key]"
                        );
                        const valueInput = card.querySelector(
                            "[data-add-property-value]"
                        );
                        const key = keyInput?.value.trim() || "";
                        const value = valueInput?.value.trim() || "";
                        if (!key || !value) {{
                            return;
                        }}
                        queueAction("set_graph_entity_property", {{
                            entityId,
                            property: {{ key, value }}
                        }});
                        appendGraphPropertyRow(card, entityId, key, value);
                        if (keyInput) {{
                            keyInput.value = "";
                        }}
                        if (valueInput) {{
                            valueInput.value = "";
                        }}
                        flashSaved();
                    }});
                const relationList = card.querySelector(
                    ".entity-relation-list"
                );
                const bindRelationLabel = (input) => {{
                    let last = input.value.trim();
                    input.addEventListener("change", () => {{
                        const li = input.closest("[data-relation-id]");
                        const value = input.value.trim();
                        if (!li || value === last) {{
                            return;
                        }}
                        last = value;
                        queueAction("update_graph_entity_relation", {{
                            relationId: li.dataset.relationId,
                            label: value
                        }});
                        flashSaved();
                    }});
                }};
                card.querySelectorAll("[data-relation-label]").forEach(
                    bindRelationLabel
                );
                card.addEventListener("click", (event) => {{
                    const goto = event.target.closest("[data-relation-goto]");
                    if (goto && goto.dataset.relationGoto) {{
                        selectInspectorEntity(goto.dataset.relationGoto);
                        return;
                    }}
                    const del = event.target.closest(".delete-relation");
                    const li = del && del.closest("[data-relation-id]");
                    if (!li) {{
                        return;
                    }}
                    queueAction("delete_graph_entity_relation", {{
                        relationId: li.dataset.relationId
                    }});
                    li.remove();
                    flashSaved();
                }});
                card.querySelector("[data-add-relation]")?.addEventListener(
                    "submit",
                    (event) => {{
                        event.preventDefault();
                        const labelInput = card.querySelector(
                            "[data-relation-add-label]"
                        );
                        const targetSelect = card.querySelector(
                            "[data-relation-add-target]"
                        );
                        const targetId = targetSelect?.value || "";
                        const label = labelInput?.value.trim() || "";
                        if (!targetId) {{
                            return;
                        }}
                        const relationId = (
                            window.crypto && crypto.randomUUID
                                ? crypto.randomUUID()
                                : String(Date.now()) + Math.random()
                        );
                        queueAction("add_graph_entity_relation", {{
                            entityId,
                            targetEntityId: targetId,
                            label,
                            relationId
                        }});
                        if (relationList) {{
                            const targetLabel = targetSelect.options[
                                targetSelect.selectedIndex
                            ].text;
                            const li = document.createElement("li");
                            li.className = "entity-relation";
                            li.dataset.relationId = relationId;
                            const input = document.createElement("input");
                            input.type = "text";
                            input.className = "entity-relation__label";
                            input.setAttribute("data-relation-label", "");
                            input.maxLength = 120;
                            input.value = label;
                            input.placeholder = "Mot clé…";
                            const span = document.createElement("button");
                            span.type = "button";
                            span.className = (
                                "entity-relation__target entity-relation__goto"
                            );
                            span.dataset.relationGoto = targetId;
                            span.title = "Aller à l'entité";
                            span.textContent = "→ " + targetLabel;
                            const btn = document.createElement("button");
                            btn.type = "button";
                            btn.className = (
                                "icon-action icon-action--danger delete-relation"
                            );
                            btn.title = "Supprimer la relation";
                            btn.setAttribute(
                                "aria-label", "Supprimer la relation"
                            );
                            btn.textContent = "×";
                            li.appendChild(input);
                            li.appendChild(span);
                            li.appendChild(btn);
                            relationList.appendChild(li);
                            bindRelationLabel(input);
                        }}
                        if (labelInput) {{
                            labelInput.value = "";
                        }}
                        if (targetSelect) {{
                            targetSelect.value = "";
                        }}
                        flashSaved();
                    }}
                );
            }});

            resultCards.forEach((card) => {{
                card.querySelector("[data-result-status]")?.addEventListener(
                    "change",
                    () => saveResult(card)
                );
                card.querySelector("[data-result-favorite]")?.addEventListener(
                    "change",
                    () => {{
                        card.dataset.favorite = card.querySelector(
                            "[data-result-favorite]"
                        ).checked ? "1" : "0";
                        saveResult(card);
                    }}
                );
                card.querySelector(".start-page-monitor")?.addEventListener(
                    "click",
                    () => {{
                        storeViewState({{
                            inspectorType: "page",
                            inspectorId: card.dataset.resultId
                        }});
                        queueAction("create_page_monitor", {{
                            resultId: card.dataset.resultId
                        }});
                    }}
                );
                card.querySelector(".extract-result-entities")?.addEventListener(
                    "click",
                    () => {{
                        storeViewState({{
                            inspectorType: "page",
                            inspectorId: card.dataset.resultId
                        }});
                        queueAction("extract_result_entities", {{
                            resultId: card.dataset.resultId
                        }});
                    }}
                );
                card.querySelector(".analyze-result-url")?.addEventListener(
                    "click",
                    () => {{
                        storeViewState({{
                            inspectorType: "page",
                            inspectorId: card.dataset.resultId
                        }});
                        window.synthesixPage.setStatus("Analyzing URL...");
                        queueAction("analyze_result_url", {{
                            resultId: card.dataset.resultId
                        }});
                    }}
                );
                card.querySelector(".remove-saved-page")?.addEventListener(
                    "click",
                    () => {{
                        if (
                            confirm(
                                "Remove this page from the investigation? "
                                + "The underlying search observation is preserved."
                            )
                        ) {{
                            queueAction("remove_saved_page", {{
                                resultId: card.dataset.resultId
                            }});
                            document.querySelector(
                                `[data-inspector-panel="${{card.dataset.resultId}}"]`
                            )?.remove();
                            card.remove();
                            flashSaved();
                        }}
                    }}
                );
                card.querySelectorAll(".delete-evidence").forEach((button) => {{
                    button.addEventListener("click", () => {{
                        const item = button.closest("[data-evidence-id]");
                        if (
                            item
                            && confirm("Delete this evidence capture and its files?")
                        ) {{
                            queueAction("delete_evidence_capture", {{
                                captureId: item.dataset.evidenceId
                            }});
                            removeEvidenceItem(item);
                        }}
                    }});
                }});
                card.querySelectorAll(".verify-evidence").forEach((button) => {{
                    button.addEventListener("click", () => {{
                        const item = button.closest("[data-evidence-id]");
                        if (!item) {{
                            return;
                        }}
                        const status = item.querySelector(
                            "[data-evidence-verification]"
                        );
                        status.textContent = "Checking...";
                        status.className = "evidence-verification";
                        queueAction("verify_evidence_capture", {{
                            captureId: item.dataset.evidenceId
                        }});
                    }});
                }});
            }});

            document.addEventListener("click", (event) => {{
                const panel = event.target.closest(".inspector-panel");
                if (!panel) {{
                    return;
                }}
                const resultId = panel.dataset.resultId;
                if (event.target.closest(".extract-result-entities")) {{
                    storeViewState({{
                        inspectorType: "page",
                        inspectorId: resultId
                    }});
                    queueAction("extract_result_entities", {{ resultId }});
                    return;
                }}
                if (event.target.closest(".analyze-result-url")) {{
                    storeViewState({{
                        inspectorType: "page",
                        inspectorId: resultId
                    }});
                    window.synthesixPage.setStatus("Analyzing URL...");
                    queueAction("analyze_result_url", {{ resultId }});
                    return;
                }}
                const deleteEvidence = event.target.closest(".delete-evidence");
                if (deleteEvidence) {{
                    const item = deleteEvidence.closest("[data-evidence-id]");
                    if (
                        item
                        && confirm("Delete this evidence capture and its files?")
                    ) {{
                        queueAction("delete_evidence_capture", {{
                            captureId: item.dataset.evidenceId
                        }});
                        removeEvidenceItem(item);
                    }}
                    return;
                }}
                const verifyEvidence = event.target.closest(".verify-evidence");
                if (verifyEvidence) {{
                    const item = verifyEvidence.closest("[data-evidence-id]");
                    if (!item) {{
                        return;
                    }}
                    const status = item.querySelector(
                        "[data-evidence-verification]"
                    );
                    status.textContent = "Checking...";
                    status.className = "evidence-verification";
                    queueAction("verify_evidence_capture", {{
                        captureId: item.dataset.evidenceId
                    }});
                }}
            }});

            const updateMonitorCount = () => {{
                const count = document.querySelectorAll(
                    "[data-page-monitor-id]"
                ).length;
                document.querySelectorAll("[data-monitor-count]").forEach(
                    (node) => {{ node.textContent = `${{count}} monitored`; }}
                );
            }};
            document.querySelectorAll(".stop-page-monitor").forEach((button) => {{
                button.addEventListener("click", () => {{
                    if (confirm("Stop monitoring this page?")) {{
                        queueAction("delete_page_monitor", {{
                            monitorId: button.dataset.monitorId
                        }});
                        document.querySelectorAll(
                            `[data-monitor-id="${{button.dataset.monitorId}}"]`
                        ).forEach((control) => {{
                            const card = control.closest("[data-page-monitor-id]");
                            if (card) {{
                                card.remove();
                                return;
                            }}
                            if (
                                control.previousElementSibling
                                && control.previousElementSibling.textContent
                                    .trim() === "Monitoring"
                            ) {{
                                control.previousElementSibling.remove();
                            }}
                            const hostCard = control.closest(
                                ".investigation-result"
                            );
                            control.remove();
                            if (hostCard) {{
                                const actions = hostCard.querySelector(
                                    ".result-review-controls"
                                );
                                const start = document.createElement("button");
                                start.type = "button";
                                start.className = (
                                    "icon-action icon-action--frame "
                                    + "start-page-monitor"
                                );
                                start.title = "Monitor changes";
                                start.setAttribute(
                                    "aria-label",
                                    "Monitor changes"
                                );
                                start.innerHTML = {json.dumps(_icon("activity"))};
                                start.addEventListener("click", () => {{
                                    storeViewState({{
                                        inspectorType: "page",
                                        inspectorId: hostCard.dataset.resultId
                                    }});
                                    queueAction("create_page_monitor", {{
                                        resultId: hostCard.dataset.resultId
                                    }});
                                }});
                                actions?.insertBefore(
                                    start,
                                    actions.querySelector(".favorite-toggle")
                                );
                            }}
                        }});
                        updateMonitorCount();
                        flashSaved();
                    }}
                }});
            }});

            const normalize = (value) => String(value || "").toLowerCase().trim();
            const applyFilters = () => {{
                const query = normalize(document.getElementById("result-filter-query").value);
                const status = document.getElementById("result-filter-status").value;
                const source = normalize(document.getElementById("result-filter-source").value);
                const tag = normalize(document.getElementById("result-filter-tag").value);
                const type = document.getElementById("result-filter-type").value;
                const after = document.getElementById("result-filter-after").value;
                const before = document.getElementById("result-filter-before").value;
                const favoritesOnly = document.getElementById(
                    "result-filter-favorite"
                ).checked;
                let visible = 0;

                resultCards.forEach((card) => {{
                    const observed = card.dataset.observed || "";
                    const matches = (
                        (!query || card.dataset.search.includes(query))
                        && (!status || card.dataset.status === status)
                        && (!source || card.dataset.sources.includes(`|${{source}}|`))
                        && (!tag || card.dataset.tags.includes(`|${{tag}}|`))
                        && (
                            !type
                            || (type === "imported" && card.dataset.imported === "1")
                            || (type === "page" && card.dataset.imported !== "1")
                        )
                        && (!after || observed >= after)
                        && (!before || observed <= before)
                        && (!favoritesOnly || card.dataset.favorite === "1")
                    );
                    card.hidden = !matches;
                    if (matches) {{
                        visible += 1;
                    }}
                }});
                document.getElementById(
                    "visible-result-count"
                ).textContent = `${{visible}} visibles`;
            }};

            filterIds.forEach((id) => {{
                document.getElementById(id)?.addEventListener("input", applyFilters);
                document.getElementById(id)?.addEventListener("change", applyFilters);
            }});
            document.getElementById("clear-result-filters")?.addEventListener(
                "click",
                () => {{
                    filterIds.forEach((id) => {{
                        const field = document.getElementById(id);
                        if (field.type === "checkbox") {{
                            field.checked = false;
                        }} else {{
                            field.value = "";
                        }}
                    }});
                    applyFilters();
                }}
            );

            document.getElementById("attach-search-form")?.addEventListener(
                "submit",
                (event) => {{
                    event.preventDefault();
                    const searchRunId = document.getElementById(
                        "unassigned-search"
                    ).value;
                    if (searchRunId) {{
                        queueAction("attach_investigation_search", {{ searchRunId }});
                    }}
                }}
            );

            document.getElementById(
                "zeroneurone-export-form"
            )?.addEventListener("submit", (event) => {{
                event.preventDefault();
                queueAction("export_zeroneurone", {{
                    includeEvidence: document.getElementById(
                        "export-include-evidence"
                    ).checked,
                    includeUnreviewed: document.getElementById(
                        "export-include-unreviewed"
                    ).checked
                }});
                window.synthesixPage.setStatus("Generating export...");
            }});
            document.querySelectorAll(".delete-export").forEach((button) => {{
                button.addEventListener("click", () => {{
                    const card = button.closest("[data-export-id]");
                    if (
                        card
                        && confirm("Delete this ZeroNeurone export and its files?")
                    ) {{
                        queueAction("delete_zeroneurone_export", {{
                            exportId: card.dataset.exportId
                        }});
                        card.remove();
                        const count = document.querySelectorAll(
                            "[data-export-id]"
                        ).length;
                        document.querySelectorAll("[data-export-count]").forEach(
                            (node) => {{
                                node.textContent = `${{count}} export(s)`;
                            }}
                        );
                        flashSaved();
                    }}
                }});
            }});
            const railStorageKey = (
                `synthesix:rail-collapsed:${{investigationId}}`
            );
            const workspace = document.querySelector(".workspace");
            const railToggle = document.querySelector("[data-rail-toggle]");
            const setRailCollapsed = (collapsed) => {{
                if (!workspace || !railToggle) {{
                    return;
                }}
                workspace.dataset.railCollapsed = String(collapsed);
                railToggle.setAttribute("aria-expanded", String(!collapsed));
                railToggle.textContent = collapsed ? "\\u2039" : "\\u203a";
                const label = collapsed ? "Expand panel" : "Collapse panel";
                railToggle.title = label;
                railToggle.setAttribute("aria-label", label);
                try {{
                    localStorage.setItem(railStorageKey, collapsed ? "1" : "0");
                }} catch (_error) {{
                    // Panel still toggles without persistence on file URLs.
                }}
            }};
            if (workspace && railToggle) {{
                let railCollapsed = false;
                try {{
                    railCollapsed = localStorage.getItem(railStorageKey) === "1";
                }} catch (_error) {{
                    railCollapsed = false;
                }}
                setRailCollapsed(railCollapsed);
                railToggle.addEventListener("click", () => {{
                    setRailCollapsed(
                        workspace.dataset.railCollapsed !== "true"
                    );
                }});
            }}

            const inspectorDetail = document.getElementById("inspector-detail");
            const nextActions = document.getElementById("rail-next-actions");
            const inspectorClose = inspectorDetail
                ? inspectorDetail.querySelector("[data-inspector-close]")
                : null;
            const inspectorPagePanels = inspectorDetail
                ? Array.from(
                    inspectorDetail.querySelectorAll("[data-inspector-panel]")
                )
                : [];
            const inspectorEntityPanels = inspectorDetail
                ? Array.from(
                    inspectorDetail.querySelectorAll("[data-inspector-entity]")
                )
                : [];
            const inspectorCreateEntity = inspectorDetail
                ? inspectorDetail.querySelector("[data-inspector-create-entity]")
                : null;
            const restoredViewState = loadViewState();
            const openEntityCreate = document.getElementById("open-entity-create");
            const entityRows = Array.from(
                document.querySelectorAll("[data-entity-select]")
            );
            const entityFilterQuery = document.getElementById(
                "entity-filter-query"
            );
            const visibleEntityCount = document.getElementById(
                "visible-entity-count"
            );
            const applyEntityFilter = () => {{
                const query = normalize(entityFilterQuery?.value || "");
                let visible = 0;
                entityRows.forEach((row) => {{
                    const matches = (
                        !query
                        || normalize(row.dataset.entitySearch || "").includes(query)
                    );
                    row.hidden = !matches;
                    if (matches) {{
                        visible += 1;
                    }}
                }});
                if (visibleEntityCount) {{
                    visibleEntityCount.textContent = `${{visible}} entités`;
                }}
            }};
            entityFilterQuery?.addEventListener("input", applyEntityFilter);
            const extractedRows = Array.from(
                document.querySelectorAll(".entity-chip-row")
            );
            const hideInspectorPanels = () => {{
                inspectorPagePanels.forEach((panel) => {{
                    panel.hidden = true;
                }});
                inspectorEntityPanels.forEach((panel) => {{
                    panel.hidden = true;
                }});
                if (inspectorCreateEntity) {{
                    inspectorCreateEntity.hidden = true;
                }}
            }};
            const clearInspectorSelection = () => {{
                resultCards.forEach((card) => {{
                    card.classList.remove("is-inspected");
                }});
                entityRows.forEach((row) => {{
                    row.classList.remove("is-inspected");
                }});
            }};
            const revealInspector = (matched) => {{
                if (nextActions) {{
                    nextActions.hidden = matched;
                }}
                if (inspectorDetail) {{
                    inspectorDetail.hidden = !matched;
                }}
                if (
                    matched
                    && workspace
                    && workspace.dataset.railCollapsed === "true"
                ) {{
                    setRailCollapsed(false);
                }}
            }};
            const closeInspector = () => {{
                hideInspectorPanels();
                clearInspectorSelection();
                if (nextActions) {{
                    nextActions.hidden = false;
                }}
                if (inspectorDetail) {{
                    inspectorDetail.hidden = true;
                }}
                clearViewState();
            }};
            if (inspectorClose) {{
                inspectorClose.addEventListener("click", closeInspector);
            }}
            openEntityCreate?.addEventListener("click", () => {{
                hideInspectorPanels();
                clearInspectorSelection();
                if (inspectorCreateEntity) {{
                    inspectorCreateEntity.hidden = false;
                }}
                revealInspector(Boolean(inspectorCreateEntity));
                storeViewState({{ inspectorType: "create" }});
                document.getElementById("new-graph-entity-label")?.focus();
            }});
            const selectInspectorPage = (resultId, persist = true) => {{
                hideInspectorPanels();
                clearInspectorSelection();
                let matched = false;
                inspectorPagePanels.forEach((panel) => {{
                    if (panel.dataset.inspectorPanel === resultId) {{
                        panel.hidden = false;
                        matched = true;
                    }}
                }});
                if (matched) {{
                    resultCards.forEach((card) => {{
                        if (card.dataset.resultId === resultId) {{
                            card.classList.add("is-inspected");
                        }}
                    }});
                }}
                revealInspector(matched);
                if (matched && persist) {{
                    storeViewState({{
                        inspectorType: "page",
                        inspectorId: resultId
                    }});
                }}
            }};
            const selectInspectorEntity = (entityId, persist = true) => {{
                hideInspectorPanels();
                clearInspectorSelection();
                let matched = false;
                inspectorEntityPanels.forEach((panel) => {{
                    if (panel.dataset.inspectorEntity === entityId) {{
                        panel.hidden = false;
                        matched = true;
                    }}
                }});
                if (matched) {{
                    entityRows.forEach((row) => {{
                        if (row.dataset.entitySelect === entityId) {{
                            row.classList.add("is-inspected");
                        }}
                    }});
                }}
                revealInspector(matched);
                if (matched && persist) {{
                    storeViewState({{
                        inspectorType: "entity",
                        inspectorId: entityId
                    }});
                }}
            }};
            resultCards.forEach((card) => {{
                // The whole card opens the detail rail; only the title link
                // (and explicit controls) keep their own behaviour.
                card.addEventListener("click", (event) => {{
                    if (event.target.closest(
                        "a, button, input, select, textarea, label"
                    )) {{
                        return;
                    }}
                    selectInspectorPage(card.dataset.resultId);
                }});
            }});
            entityRows.forEach((row) => {{
                row.addEventListener(
                    "click",
                    () => selectInspectorEntity(row.dataset.entitySelect)
                );
            }});
            document.querySelectorAll("[data-page-linked-entity]").forEach(
                (button) => {{
                    button.addEventListener("click", () => {{
                        selectInspectorEntity(button.dataset.pageLinkedEntity);
                    }});
                }}
            );
            if (restoredViewState) {{
                if (restoredViewState.inspectorType === "page") {{
                    selectInspectorPage(restoredViewState.inspectorId || "", false);
                }} else if (restoredViewState.inspectorType === "entity") {{
                    selectInspectorEntity(restoredViewState.inspectorId || "", false);
                }} else if (
                    restoredViewState.inspectorType === "create"
                    && inspectorCreateEntity
                ) {{
                    hideInspectorPanels();
                    clearInspectorSelection();
                    inspectorCreateEntity.hidden = false;
                    revealInspector(true);
                }}
                if (
                    Number.isFinite(Number(restoredViewState.scrollX))
                    && Number.isFinite(Number(restoredViewState.scrollY))
                ) {{
                    window.requestAnimationFrame(() => {{
                        window.scrollTo(
                            Number(restoredViewState.scrollX),
                            Number(restoredViewState.scrollY)
                        );
                    }});
                }}
            }}
            const refreshEntityGroups = (section) => {{
                if (!section) {{
                    return;
                }}
                section.querySelectorAll("[data-entity-group]").forEach(
                    (group) => {{
                        const hasRows = Boolean(
                            group.querySelector(
                                ".entity-chip-row:not([data-removed='true'])"
                            )
                        );
                        group.hidden = !hasRows;
                    }}
                );
            }};
            const refreshExtractedEntityState = (section) => {{
                if (!section) {{
                    return;
                }}
                const rows = Array.from(
                    section.querySelectorAll(".entity-chip-row")
                ).filter((row) => row.dataset.removed !== "true");
                const count = section.querySelector(
                    "[data-extracted-entity-count]"
                );
                if (count) {{
                    count.textContent = String(rows.length);
                }}
                refreshEntityGroups(section);
            }};
            const refreshEvidenceState = (container) => {{
                if (!container) {{
                    return;
                }}
                const items = Array.from(
                    container.querySelectorAll("[data-evidence-id]")
                ).filter((item) => item.dataset.removed !== "true");
                const count = container.querySelector("[data-evidence-count]");
                if (count) {{
                    count.textContent = String(items.length);
                }}
                container.hidden = items.length === 0;
            }};
            const removeEvidenceItem = (item) => {{
                if (!item) {{
                    return;
                }}
                const container = item.closest(".result-evidence");
                item.dataset.removed = "true";
                item.remove();
                refreshEvidenceState(container);
                flashSaved();
            }};
            const removeLinkedExtractedRows = (graphEntityId, propertyKey) => {{
                const wantedKey = String(propertyKey || "").toLowerCase().trim();
                if (!graphEntityId || !wantedKey) {{
                    return;
                }}
                document.querySelectorAll(".entity-chip-row").forEach((row) => {{
                    const link = row.querySelector("[data-extracted-attach]");
                    const name = row.querySelector("[data-entity-custom-label]");
                    const rowKey = String(name?.value || "").toLowerCase().trim();
                    if (link?.value === graphEntityId && rowKey === wantedKey) {{
                        row.dataset.removed = "true";
                        row.hidden = true;
                        const box = row.querySelector("[data-entity-checkbox]");
                        if (box) {{
                            box.checked = false;
                        }}
                        refreshExtractedEntityState(
                            row.closest(".result-entities")
                        );
                    }}
                }});
            }};
            const optionProperties = (option) => {{
                try {{
                    const parsed = JSON.parse(option?.dataset.properties || "{{}}");
                    return parsed && typeof parsed === "object" ? parsed : {{}};
                }} catch (_error) {{
                    return {{}};
                }}
            }};
            const findExistingPropertyKey = (properties, propertyKey) => {{
                const wanted = String(propertyKey || "").toLowerCase().trim();
                return Object.keys(properties).find(
                    (key) => key.toLowerCase().trim() === wanted
                ) || "";
            }};
            const duplicateStrategyForAttach = (
                select,
                propertyKey,
                propertyType
            ) => {{
                const option = select?.selectedOptions?.[0] || null;
                const properties = optionProperties(option);
                const existingKey = findExistingPropertyKey(
                    properties,
                    propertyKey
                );
                if (!existingKey) {{
                    return {{ ok: true, strategy: "append" }};
                }}
                // An empty placeholder (e.g. a tagset base property) is not a
                // real conflict: just fill it without prompting.
                if (!String(properties[existingKey] ?? "").trim()) {{
                    return {{ ok: true, strategy: "replace" }};
                }}
                const label = option?.textContent?.trim() || "cette entité";
                const typeLabel = propertyType ? ` (${{propertyType}})` : "";
                const choice = window.prompt(
                    `Une propriété "${{propertyKey}}"${{typeLabel}} existe `
                    + `déjà pour ${{label}}.\\n`
                    + "Tapez A pour ajouter la valeur avec ';', "
                    + "R pour remplacer, ou Annuler pour ne rien faire.",
                    "A"
                );
                if (choice === null) {{
                    return {{ ok: false, strategy: "" }};
                }}
                const normalized = choice.trim().toLowerCase();
                if (normalized.startsWith("r")) {{
                    return {{ ok: true, strategy: "replace" }};
                }}
                if (normalized.startsWith("a")) {{
                    return {{ ok: true, strategy: "append" }};
                }}
                return {{ ok: false, strategy: "" }};
            }};
            const updateEntityOptionProperty = (
                graphEntityId,
                propertyKey,
                value,
                strategy
            ) => {{
                document.querySelectorAll(
                    `option[value="${{CSS.escape(graphEntityId)}}"]`
                ).forEach((option) => {{
                    const properties = optionProperties(option);
                    const existingKey = (
                        findExistingPropertyKey(properties, propertyKey)
                        || propertyKey
                    );
                    if (strategy === "replace") {{
                        properties[existingKey] = value;
                    }} else {{
                        const values = String(properties[existingKey] || "")
                            .split(";")
                            .map((item) => item.trim())
                            .filter(Boolean);
                        if (!values.includes(value)) {{
                            values.push(value);
                        }}
                        properties[existingKey] = values.join("; ");
                    }}
                    option.dataset.properties = JSON.stringify(properties);
                }});
            }};
            const setExtractedRowScope = (row, scope) => {{
                const normalizedScope = scope === "page" ? "page" : "entity";
                const section = row.closest(".result-entities");
                const targetList = section?.querySelector(
                    `[data-entity-list="${{normalizedScope}}"]`
                );
                if (targetList && row.parentElement !== targetList) {{
                    targetList.appendChild(row);
                }}
                row.dataset.propertyScope = normalizedScope;
                const input = row.querySelector("[data-entity-custom-label]");
                if (input) {{
                    input.setAttribute(
                        "list",
                        normalizedScope === "page"
                            ? row.dataset.pagePropertyList || "property-suggestions"
                            : row.dataset.entityPropertyList || "property-suggestions"
                    );
                }}
                if (normalizedScope === "page") {{
                    const promoteForm = row.querySelector(
                        ".entity-chip-row__promote"
                    );
                    if (promoteForm) {{
                        promoteForm.hidden = true;
                    }}
                }}
                const toggle = row.querySelector("[data-scope-toggle]");
                if (toggle) {{
                    const nextScope = (
                        normalizedScope === "page" ? "entity" : "page"
                    );
                    const label = (
                        normalizedScope === "page"
                            ? "Ranger avec les propriétés à rattacher"
                            : "Ranger avec les propriétés de la page"
                    );
                    toggle.dataset.nextScope = nextScope;
                    toggle.title = label;
                    toggle.setAttribute("aria-label", label);
                }}
                refreshExtractedEntityState(section);
                row.querySelector("[data-entity-checkbox]")?.dispatchEvent(
                    new Event("change", {{ bubbles: true }})
                );
            }};
            extractedRows.forEach((row) => {{
                const entityId = row.dataset.entityId;
                const nameInput = row.querySelector("[data-entity-custom-label]");
                nameInput?.addEventListener("change", () => {{
                    queueAction("update_entity_metadata", {{
                        entityId,
                        entity: {{
                            entity_type: row.dataset.entityType,
                            custom_label: nameInput.value.trim(),
                            property_type: row.dataset.propertyType || ""
                        }}
                    }});
                    flashSaved();
                }});
                const validateButton = row.querySelector(".entity-validate");
                validateButton?.addEventListener("click", () => {{
                    row.className = "entity-chip-row entity-item--validated";
                    validateButton.hidden = true;
                    queueAction("update_entity_status", {{
                        entityId,
                        status: "validated"
                    }});
                    flashSaved();
                }});
                row.querySelector(".entity-reject")?.addEventListener(
                    "click",
                    () => {{
                        queueAction("delete_entity", {{ entityId }});
                        row.dataset.removed = "true";
                        row.hidden = true;
                        refreshExtractedEntityState(row.closest(".result-entities"));
                        flashSaved();
                    }}
                );
                row.querySelector("[data-scope-toggle]")?.addEventListener(
                    "click",
                    () => {{
                        const scope = (
                            row.dataset.propertyScope === "page"
                                ? "entity"
                                : "page"
                        );
                        setExtractedRowScope(row, scope);
                        queueAction("set_entity_property_scope", {{
                            extractedEntityId: entityId,
                            scope
                        }});
                        flashSaved();
                    }}
                );
                row.querySelector("[data-extracted-attach]")?.addEventListener(
                    "change",
                    (event) => {{
                        const graphEntityId = event.target.value;
                        const propertyKey = nameInput?.value.trim() || "";
                        if (graphEntityId && propertyKey) {{
                            const strategy = duplicateStrategyForAttach(
                                event.target,
                                propertyKey,
                                row.dataset.propertyType || ""
                            );
                            if (!strategy.ok) {{
                                event.target.value = row.dataset.attachedEntityId || "";
                                return;
                            }}
                            const value = row.querySelector(
                                ".entity-chip-row__value"
                            )?.textContent.trim() || "";
                            queueAction("attach_extracted_property", {{
                                extractedEntityId: entityId,
                                property: {{
                                    graph_entity_id: graphEntityId,
                                    property_key: propertyKey,
                                    property_type: row.dataset.propertyType || "",
                                    duplicate_strategy: strategy.strategy
                                }}
                            }});
                            updateEntityOptionProperty(
                                graphEntityId,
                                propertyKey,
                                value,
                                strategy.strategy
                            );
                            row.dataset.attachedEntityId = graphEntityId;
                            // No reload: reflect validation in place.
                            row.classList.remove("entity-item--proposed");
                            row.classList.add("entity-item--validated");
                            if (validateButton) {{
                                validateButton.hidden = true;
                            }}
                        }} else if (!graphEntityId) {{
                            queueAction("detach_extracted_property", {{
                                extractedEntityId: entityId
                            }});
                            row.dataset.attachedEntityId = "";
                            row.classList.remove("entity-item--validated");
                            row.classList.add("entity-item--proposed");
                            if (validateButton) {{
                                validateButton.hidden = false;
                            }}
                        }}
                        flashSaved();
                    }}
                );
                const promoteToggle = row.querySelector(
                    ".entity-promote-toggle"
                );
                const promoteForm = row.querySelector(
                    ".entity-chip-row__promote"
                );
                if (promoteToggle && promoteForm) {{
                    promoteToggle.addEventListener("click", () => {{
                        promoteForm.hidden = !promoteForm.hidden;
                    }});
                    row.querySelector(".promote-cancel")?.addEventListener(
                        "click",
                        () => {{ promoteForm.hidden = true; }}
                    );
                }}
                row.querySelector(".create-entity-from-property")
                    ?.addEventListener("click", () => {{
                        const label = row.querySelector(
                            "[data-quick-entity-label]"
                        )?.value.trim() || "";
                        const category = row.querySelector(
                            "[data-quick-entity-category]"
                        )?.value.trim() || "";
                        const propertyKey = nameInput?.value.trim() || label;
                        if (label && category) {{
                            const panel = row.closest("[data-inspector-panel]");
                            const resultId = panel?.dataset.resultId || "";
                            if (resultId) {{
                                storeViewState({{
                                    inspectorType: "page",
                                    inspectorId: resultId
                                }});
                            }}
                            queueAction("create_graph_entity_from_extracted", {{
                                extractedEntityId: entityId,
                                entity: {{
                                    label,
                                    category,
                                    property_key: propertyKey
                                }}
                            }});
                        }}
                    }});
            }});
            document.querySelectorAll(".result-entities").forEach((section) => {{
                const batchBar = section.querySelector("[data-entity-batch]");
                if (!batchBar) {{
                    return;
                }}
                const batchCount = batchBar.querySelector("[data-batch-count]");
                const batchReject = batchBar.querySelector(
                    "[data-batch-reject]"
                );
                const batchAttach = batchBar.querySelector(
                    "[data-batch-attach]"
                );
                const filterQuery = section.querySelector(
                    "[data-entity-filter-query]"
                );
                const filterStatus = section.querySelector(
                    "[data-entity-filter-status]"
                );
                const filterRows = Array.from(
                    section.querySelectorAll(".entity-chip-row")
                );
                const applyFilter = () => {{
                    const query = normalize(filterQuery?.value || "");
                    const status = filterStatus?.value || "";
                    filterRows.forEach((row) => {{
                        if (row.dataset.removed === "true") {{
                            row.hidden = true;
                            return;
                        }}
                        const name = row.querySelector(
                            "[data-entity-custom-label]"
                        );
                        const value = row.querySelector(
                            ".entity-chip-row__value"
                        );
                        const haystack = normalize(
                            (value ? value.textContent : "")
                            + " "
                            + (name ? name.value : "")
                        );
                        const isValidated = row.classList.contains(
                            "entity-item--validated"
                        );
                        const statusOk = (
                            !status
                            || (status === "validated" && isValidated)
                            || (status === "proposed" && !isValidated)
                        );
                        row.hidden = !(
                            statusOk && (!query || haystack.includes(query))
                        );
                    }});
                }};
                filterQuery?.addEventListener("input", applyFilter);
                filterStatus?.addEventListener("change", applyFilter);
                const checkboxes = Array.from(
                    section.querySelectorAll("[data-entity-checkbox]")
                );
                const checkedRows = () => checkboxes
                    .filter((box) => box.checked)
                    .map((box) => box.closest(".entity-chip-row"))
                    .filter((row) => row && !row.hidden);
                const refreshBatch = () => {{
                    const rows = checkedRows();
                    const count = rows.length;
                    const attachableCount = rows.filter(
                        (row) => row.dataset.propertyScope !== "page"
                    ).length;
                    batchBar.hidden = count === 0;
                    if (batchCount) {{
                        batchCount.textContent = count + " sélectionnée(s)";
                    }}
                    if (batchAttach) {{
                        batchAttach.hidden = (
                            count === 0 || attachableCount !== count
                        );
                    }}
                }};
                checkboxes.forEach((box) => {{
                    box.addEventListener("change", refreshBatch);
                }});
                batchReject?.addEventListener("click", () => {{
                    const rows = checkedRows();
                    if (!rows.length) {{
                        return;
                    }}
                    const entityIds = rows.map((row) => row.dataset.entityId);
                    rows.forEach((row) => {{
                        row.dataset.removed = "true";
                        row.hidden = true;
                        const box = row.querySelector("[data-entity-checkbox]");
                        if (box) {{
                            box.checked = false;
                        }}
                    }});
                    refreshBatch();
                    refreshExtractedEntityState(section);
                    queueAction("delete_entities", {{ entityIds }});
                    flashSaved();
                }});
                batchAttach?.addEventListener("change", (event) => {{
                    const graphEntityId = event.target.value;
                    const rows = checkedRows();
                    if (!graphEntityId || !rows.length) {{
                        event.target.value = "";
                        return;
                    }}
                    if (rows.some((row) => row.dataset.propertyScope === "page")) {{
                        event.target.value = "";
                        refreshBatch();
                        return;
                    }}
                    const items = [];
                    rows.forEach((row) => {{
                        const nameInput = row.querySelector(
                            "[data-entity-custom-label]"
                        );
                        const propertyKey = nameInput
                            ? nameInput.value.trim()
                            : "";
                        const strategy = duplicateStrategyForAttach(
                            event.target,
                            propertyKey,
                            row.dataset.propertyType || ""
                        );
                        if (!strategy.ok) {{
                            return;
                        }}
                        const value = row.querySelector(
                            ".entity-chip-row__value"
                        )?.textContent.trim() || "";
                        updateEntityOptionProperty(
                            graphEntityId,
                            propertyKey,
                            value,
                            strategy.strategy
                        );
                        items.push({{
                            extractedEntityId: row.dataset.entityId,
                            propertyKey,
                            propertyType: row.dataset.propertyType || "",
                            duplicateStrategy: strategy.strategy
                        }});
                    }});
                    if (!items.length) {{
                        event.target.value = "";
                        refreshBatch();
                        return;
                    }}
                    queueAction("attach_extracted_properties", {{
                        graphEntityId,
                        items
                    }});
                    const attachedIds = new Set(
                        items.map((item) => item.extractedEntityId)
                    );
                    // No reload: reflect validation on each selected row.
                    rows.forEach((row) => {{
                        if (!attachedIds.has(row.dataset.entityId)) {{
                            return;
                        }}
                        row.classList.remove("entity-item--proposed");
                        row.classList.add("entity-item--validated");
                        row.dataset.attachedEntityId = graphEntityId;
                        const validate = row.querySelector(".entity-validate");
                        if (validate) {{
                            validate.hidden = true;
                        }}
                        const box = row.querySelector("[data-entity-checkbox]");
                        if (box) {{
                            box.checked = false;
                        }}
                    }});
                    refreshBatch();
                    event.target.value = "";
                    flashSaved();
                }});
            }});
            if (inspectorDetail) {{
                inspectorDetail.addEventListener("click", (event) => {{
                    const goto = event.target.closest("[data-inspector-goto]");
                    if (!goto) {{
                        return;
                    }}
                    const card = document.getElementById(
                        "result-" + goto.dataset.inspectorGoto
                    );
                    if (card) {{
                        card.scrollIntoView({{
                            behavior: "smooth",
                            block: "center"
                        }});
                    }}
                }});
            }}

            const railResizer = document.querySelector("[data-rail-resizer]");
            const railWidthKey = `synthesix:rail-width:${{investigationId}}`;
            const clampRailWidth = (px) => Math.max(280, Math.min(680, px));
            const applyRailWidth = (px) => {{
                if (workspace) {{
                    workspace.style.setProperty(
                        "--rail-w", clampRailWidth(px) + "px"
                    );
                }}
            }};
            try {{
                const storedWidth = parseInt(
                    localStorage.getItem(railWidthKey) || "", 10
                );
                if (!Number.isNaN(storedWidth)) {{
                    applyRailWidth(storedWidth);
                }}
            }} catch (_error) {{
                // Default width is used when storage is unavailable.
            }}
            if (railResizer && workspace) {{
                let dragging = false;
                const onMove = (event) => {{
                    if (!dragging) {{
                        return;
                    }}
                    const rect = workspace.getBoundingClientRect();
                    applyRailWidth(rect.right - event.clientX);
                }};
                const onUp = () => {{
                    if (!dragging) {{
                        return;
                    }}
                    dragging = false;
                    document.body.style.userSelect = "";
                    const current = parseInt(
                        workspace.style.getPropertyValue("--rail-w"), 10
                    );
                    if (!Number.isNaN(current)) {{
                        try {{
                            localStorage.setItem(railWidthKey, String(current));
                        }} catch (_error) {{
                            // Resizing still works without persistence.
                        }}
                    }}
                    window.removeEventListener("pointermove", onMove);
                    window.removeEventListener("pointerup", onUp);
                }};
                railResizer.addEventListener("pointerdown", (event) => {{
                    event.preventDefault();
                    dragging = true;
                    document.body.style.userSelect = "none";
                    window.addEventListener("pointermove", onMove);
                    window.addEventListener("pointerup", onUp);
                }});
                railResizer.addEventListener("dblclick", () => {{
                    workspace.style.removeProperty("--rail-w");
                    try {{
                        localStorage.removeItem(railWidthKey);
                    }} catch (_error) {{
                        // Nothing to clear when storage is unavailable.
                    }}
                }});
            }}

            const importDropzone = document.querySelector(
                "[data-import-dropzone]"
            );
            if (importDropzone) {{
                const fileInput = importDropzone.querySelector(
                    "[data-import-file]"
                );
                const urlInput = importDropzone.querySelector(
                    "[data-import-url]"
                );
                const statusEl = document.querySelector("[data-import-status]");
                const importFiles = (files) => {{
                    Array.from(files || []).forEach((file) => {{
                        if (!file) {{
                            return;
                        }}
                        const reader = new FileReader();
                        reader.onload = () => {{
                            const text = String(reader.result || "");
                            const comma = text.indexOf(",");
                            const data = comma >= 0
                                ? text.slice(comma + 1)
                                : text;
                            queueAction("import_evidence_file", {{
                                fileName: file.name,
                                mimeType: (
                                    file.type || "application/octet-stream"
                                ),
                                sourceUrl: (urlInput?.value || "").trim(),
                                data: data
                            }});
                            if (statusEl) {{
                                statusEl.textContent = (
                                    "Import de " + file.name + "…"
                                );
                            }}
                        }};
                        reader.readAsDataURL(file);
                    }});
                    if (urlInput) {{
                        urlInput.value = "";
                    }}
                }};
                importDropzone.addEventListener("click", (event) => {{
                    if (event.target.closest("[data-import-url]")) {{
                        return;
                    }}
                    fileInput?.click();
                }});
                fileInput?.addEventListener("change", () => {{
                    importFiles(fileInput.files);
                }});
                ["dragover", "dragenter"].forEach((name) => {{
                    importDropzone.addEventListener(name, (event) => {{
                        event.preventDefault();
                        importDropzone.classList.add("is-dragover");
                    }});
                }});
                ["dragleave", "drop"].forEach((name) => {{
                    importDropzone.addEventListener(name, (event) => {{
                        event.preventDefault();
                        importDropzone.classList.remove("is-dragover");
                    }});
                }});
                importDropzone.addEventListener("drop", (event) => {{
                    importFiles(event.dataTransfer?.files);
                }});
            }}
        }})();
    </script>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")
    return str(output_path)
