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

ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES = {
    "Personne": (
        ("Date de naissance", "date"),
        ("Lieu de naissance", "text"),
        ("Nationalité", "country"),
        ("Alias", "text"),
        ("Adresse", "text"),
        ("Téléphone", "text"),
        ("Email", "text"),
        ("Profession", "text"),
    ),
    "Entreprise": (
        ("SIREN", "text"),
        ("SIRET", "text"),
        ("Forme juridique", "text"),
        ("Date de création", "date"),
        ("Capital social", "number"),
        ("Adresse siège", "text"),
        ("Secteur d'activité", "text"),
        ("Statut", "choice"),
    ),
    "Compte bancaire": (
        ("IBAN", "text"),
        ("BIC", "text"),
        ("Banque", "text"),
        ("Titulaire", "text"),
        ("Type", "choice"),
    ),
    "Véhicule": (
        ("Immatriculation", "text"),
        ("Marque", "text"),
        ("Modèle", "text"),
        ("Couleur", "text"),
        ("VIN", "text"),
        ("Date mise en circulation", "date"),
    ),
    "Téléphone": (
        ("Numéro", "text"),
        ("Opérateur", "text"),
        ("Type", "choice"),
        ("IMEI", "text"),
    ),
    "Email": (
        ("Adresse", "text"),
        ("Fournisseur", "text"),
    ),
    "Site web": (
        ("URL", "link"),
        ("Domaine", "text"),
        ("Registrar", "text"),
        ("Date création", "date"),
        ("Date expiration", "date"),
        ("IP", "text"),
        ("Hébergeur", "text"),
    ),
    "Compte en ligne": (
        ("Plateforme", "choice"),
        ("Username", "text"),
        ("URL profil", "link"),
        ("Nom affiché", "text"),
        ("Followers", "number"),
    ),
    "Wallet crypto": (
        ("Adresse", "text"),
        ("Blockchain", "choice"),
        ("Type", "choice"),
        ("Plateforme", "text"),
    ),
    "Document d'identité": (
        ("Type", "choice"),
        ("Numéro", "text"),
        ("Pays émetteur", "country"),
        ("Date émission", "date"),
        ("Date expiration", "date"),
    ),
    "Lieu": (
        ("Adresse", "text"),
        ("Code postal", "text"),
        ("Ville", "text"),
        ("Pays", "country"),
        ("Type", "choice"),
    ),
    "Transaction": (
        ("Date", "datetime"),
        ("Montant", "number"),
        ("Devise", "choice"),
        ("Émetteur", "text"),
        ("Bénéficiaire", "text"),
        ("Référence", "text"),
        ("Motif", "text"),
    ),
    "Événement": (
        ("Date/heure", "datetime"),
        ("Lieu", "text"),
        ("Type", "text"),
        ("Description", "text"),
    ),
    "Dirigeant": (
        ("Fonction", "text"),
        ("Organisation", "text"),
        ("Date de prise de fonction", "date"),
        ("Date de fin de fonction", "date"),
    ),
    "Militaire": (
        ("Grade", "text"),
        ("Arme", "choice"),
        ("Unité", "text"),
        ("Matricule", "text"),
        ("Date d'incorporation", "date"),
    ),
    "Fonctionnaire": (
        ("Administration", "text"),
        ("Corps", "text"),
        ("Grade", "text"),
        ("Affectation", "text"),
    ),
    "Élu": (
        ("Mandat", "text"),
        ("Circonscription", "text"),
        ("Parti", "text"),
        ("Date d'élection", "date"),
        ("Fin de mandat", "date"),
    ),
    "Avocat": (
        ("Barreau", "text"),
        ("Spécialité", "text"),
        ("Cabinet", "text"),
        ("Date d'inscription", "date"),
    ),
    "PEP": (
        ("Type PEP", "choice"),
        ("Fonction exposante", "text"),
        ("Pays", "country"),
        ("Source", "text"),
    ),
    "Sanctionné": (
        ("Liste", "choice"),
        ("Motif", "text"),
        ("Date d'inscription", "date"),
        ("Référence", "text"),
    ),
    "Suspect": (
        ("Infractions supposées", "text"),
        ("Niveau de suspicion", "choice"),
    ),
    "Témoin": (
        ("Type", "choice"),
        ("Fiabilité", "choice"),
    ),
    "Victime": (
        ("Préjudice", "text"),
        ("Date des faits", "date"),
        ("Plainte déposée", "boolean"),
    ),
    "Filiale": (
        ("Société mère", "text"),
        ("Pourcentage détenu", "number"),
        ("Date d'acquisition", "date"),
    ),
    "Offshore": (
        ("Juridiction", "choice"),
        ("Agent enregistré", "text"),
        ("Bénéficiaire effectif", "text"),
    ),
    "Zone": (
        ("Type de zone", "choice"),
        ("Surface", "text"),
        ("Adresse", "text"),
        ("Responsable", "text"),
    ),
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


def zeroneurone_tagset_suggested_properties(
    tag: object,
) -> tuple[dict[str, object], ...]:
    canonical = canonical_zeroneurone_tag(tag)
    return tuple(
        {"key": key, "type": property_type}
        for key, property_type in ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES.get(
            canonical,
            (),
        )
    )


_PROPERTY_TYPE_BY_KEY: dict[str, str] = {}
for _tagset_properties in ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES.values():
    for _property_key, _property_type in _tagset_properties:
        _PROPERTY_TYPE_BY_KEY.setdefault(_property_key.casefold(), _property_type)


def zeroneurone_property_type(key: object) -> str:
    """Declared zeroneurone PropertyType for a canonical tagset key, else ''."""
    return _PROPERTY_TYPE_BY_KEY.get(str(key or "").strip().casefold(), "")
