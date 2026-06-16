from __future__ import annotations

import unicodedata
from typing import Iterable


ZERONEURONE_TAGSETS = (
    "Personne",
    "Entreprise",
    "Compte bancaire",
    "Véhicule",
    "Téléphone",
    "Email",
    "Site web",
    "Compte en ligne",
    "Wallet crypto",
    "Document d'identité",
    "Lieu",
    "Transaction",
    "Événement",
    "Dirigeant",
    "Militaire",
    "Fonctionnaire",
    "Élu",
    "Avocat",
    "PEP",
    "Sanctionné",
    "Suspect",
    "Témoin",
    "Victime",
    "Filiale",
    "Offshore",
    "Zone",
)

ZERONEURONE_TAGSET_VISUALS = {
    "Personne": {"color": "#3b82f6", "shape": "circle", "icon": "User"},
    "Entreprise": {"color": "#8b5cf6", "shape": "square", "icon": "Building2"},
    "Compte bancaire": {
        "color": "#059669",
        "shape": "rectangle",
        "icon": "Landmark",
    },
    "Véhicule": {"color": "#f59e0b", "shape": "diamond", "icon": "Car"},
    "Téléphone": {"color": "#06b6d4", "shape": "circle", "icon": "Phone"},
    "Email": {"color": "#ec4899", "shape": "circle", "icon": "Mail"},
    "Site web": {"color": "#6366f1", "shape": "square", "icon": "Globe"},
    "Compte en ligne": {
        "color": "#14b8a6",
        "shape": "circle",
        "icon": "AtSign",
    },
    "Wallet crypto": {
        "color": "#f97316",
        "shape": "hexagon",
        "icon": "Wallet",
    },
    "Document d'identité": {
        "color": "#64748b",
        "shape": "rectangle",
        "icon": "CreditCard",
    },
    "Lieu": {"color": "#ef4444", "shape": "square", "icon": "MapPin"},
    "Transaction": {
        "color": "#22c55e",
        "shape": "diamond",
        "icon": "ArrowRightLeft",
    },
    "Événement": {
        "color": "#a855f7",
        "shape": "diamond",
        "icon": "Calendar",
    },
    "Dirigeant": {"color": None, "shape": None, "icon": "Crown"},
    "Militaire": {"color": None, "shape": None, "icon": "Shield"},
    "Fonctionnaire": {"color": None, "shape": None, "icon": "Briefcase"},
    "Élu": {"color": None, "shape": None, "icon": "Vote"},
    "Avocat": {"color": None, "shape": None, "icon": "Scale"},
    "PEP": {"color": "#dc2626", "shape": None, "icon": "AlertTriangle"},
    "Sanctionné": {"color": "#dc2626", "shape": None, "icon": "Ban"},
    "Suspect": {"color": "#f97316", "shape": None, "icon": "AlertCircle"},
    "Témoin": {"color": "#06b6d4", "shape": None, "icon": "Eye"},
    "Victime": {"color": "#8b5cf6", "shape": None, "icon": "Heart"},
    "Filiale": {"color": None, "shape": None, "icon": "GitBranch"},
    "Offshore": {"color": "#f59e0b", "shape": None, "icon": "Palmtree"},
    "Zone": {"color": "#10b981", "shape": "hexagon", "icon": "MapPin"},
}


def _tag_key(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").strip())
    return " ".join(
        text.encode("ascii", "ignore").decode("ascii").casefold().split()
    )


_TAGSET_ALIASES = {
    "person": "Personne",
    "individual": "Personne",
    "company": "Entreprise",
    "business": "Entreprise",
    "organization": "Entreprise",
    "organisation": "Entreprise",
    "societe": "Entreprise",
    "bank account": "Compte bancaire",
    "vehicle": "Véhicule",
    "phone": "Téléphone",
    "telephone": "Téléphone",
    "email address": "Email",
    "website": "Site web",
    "domain": "Site web",
    "online account": "Compte en ligne",
    "social account": "Compte en ligne",
    "crypto wallet": "Wallet crypto",
    "identity document": "Document d'identité",
    "identity card": "Document d'identité",
    "place": "Lieu",
    "location": "Lieu",
    "event": "Événement",
    "executive": "Dirigeant",
    "director": "Dirigeant",
    "military": "Militaire",
    "civil servant": "Fonctionnaire",
    "elected official": "Élu",
    "lawyer": "Avocat",
    "attorney": "Avocat",
    "sanctioned": "Sanctionné",
    "witness": "Témoin",
    "victim": "Victime",
    "subsidiary": "Filiale",
    "area": "Zone",
}
for tagset in ZERONEURONE_TAGSETS:
    _TAGSET_ALIASES[_tag_key(tagset)] = tagset


def canonical_zeroneurone_tag(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return _TAGSET_ALIASES.get(_tag_key(text), text)


def canonical_zeroneurone_tags(values: Iterable[object]) -> tuple[str, ...]:
    result = []
    seen = set()
    for value in values:
        tag = canonical_zeroneurone_tag(value)
        key = tag.casefold()
        if not tag or key in seen:
            continue
        result.append(tag)
        seen.add(key)
    return tuple(result)


def zeroneurone_tagset_visual(tag: object) -> dict[str, object] | None:
    canonical = canonical_zeroneurone_tag(tag)
    visual = ZERONEURONE_TAGSET_VISUALS.get(canonical)
    return dict(visual) if visual is not None else None
