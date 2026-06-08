from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class CountryRegion:
    code: str
    name: str
    duckduckgo_region: str = ""
    aliases: tuple[str, ...] = ()


COUNTRY_REGIONS = (
    CountryRegion("AR", "Argentina", "ar-es", ("argentine",)),
    CountryRegion("AU", "Australia", "au-en", ("australie",)),
    CountryRegion("AT", "Austria", "at-de", ("autriche",)),
    CountryRegion("BE", "Belgium", "be-fr", ("belgique",)),
    CountryRegion("BR", "Brazil", "br-pt", ("bresil",)),
    CountryRegion("BG", "Bulgaria", "bg-bg", ("bulgarie",)),
    CountryRegion("CA", "Canada", "ca-en"),
    CountryRegion("CL", "Chile", "cl-es", ("chili",)),
    CountryRegion("CN", "China", "cn-zh", ("chine",)),
    CountryRegion("CO", "Colombia", "co-es", ("colombie",)),
    CountryRegion("HR", "Croatia", "hr-hr", ("croatie",)),
    CountryRegion("CZ", "Czechia", "cz-cs", ("czech republic", "republique tcheque")),
    CountryRegion("DK", "Denmark", "dk-da", ("danemark",)),
    CountryRegion("EE", "Estonia", "ee-et", ("estonie",)),
    CountryRegion("FI", "Finland", "fi-fi", ("finlande",)),
    CountryRegion("FR", "France", "fr-fr"),
    CountryRegion("DE", "Germany", "de-de", ("allemagne", "deutschland")),
    CountryRegion("GR", "Greece", "gr-el", ("grece",)),
    CountryRegion("HK", "Hong Kong", "hk-tzh"),
    CountryRegion("HU", "Hungary", "hu-hu", ("hongrie",)),
    CountryRegion("IS", "Iceland", "is-is", ("islande",)),
    CountryRegion("IN", "India", "in-en", ("inde",)),
    CountryRegion("ID", "Indonesia", "id-id", ("indonesie",)),
    CountryRegion("IE", "Ireland", "ie-en", ("irlande",)),
    CountryRegion("IL", "Israel", "il-he"),
    CountryRegion("IT", "Italy", "it-it", ("italie",)),
    CountryRegion("JP", "Japan", "jp-jp", ("japon",)),
    CountryRegion("KR", "South Korea", "kr-kr", ("korea", "coree du sud")),
    CountryRegion("LV", "Latvia", "lv-lv", ("lettonie",)),
    CountryRegion("LT", "Lithuania", "lt-lt", ("lituanie",)),
    CountryRegion("MY", "Malaysia", "my-ms", ("malaisie",)),
    CountryRegion("MX", "Mexico", "mx-es", ("mexique",)),
    CountryRegion("NL", "Netherlands", "nl-nl", ("pays bas", "holland")),
    CountryRegion("NZ", "New Zealand", "nz-en", ("nouvelle zelande",)),
    CountryRegion("NO", "Norway", "no-no", ("norvege", "norge")),
    CountryRegion("PK", "Pakistan", "pk-en"),
    CountryRegion("PE", "Peru", "pe-es", ("perou",)),
    CountryRegion("PH", "Philippines", "ph-en"),
    CountryRegion("PL", "Poland", "pl-pl", ("pologne",)),
    CountryRegion("PT", "Portugal", "pt-pt"),
    CountryRegion("RO", "Romania", "ro-ro", ("roumanie",)),
    CountryRegion("RU", "Russia", "ru-ru", ("russie",)),
    CountryRegion("SA", "Saudi Arabia", "xa-ar", ("arabie saoudite",)),
    CountryRegion("SG", "Singapore", "sg-en", ("singapour",)),
    CountryRegion("SK", "Slovakia", "sk-sk", ("slovaquie",)),
    CountryRegion("SI", "Slovenia", "sl-sl", ("slovenie",)),
    CountryRegion("ZA", "South Africa", "za-en", ("afrique du sud",)),
    CountryRegion("ES", "Spain", "es-es", ("espagne",)),
    CountryRegion("SE", "Sweden", "se-sv", ("suede", "sverige")),
    CountryRegion("CH", "Switzerland", "ch-de", ("suisse",)),
    CountryRegion("TW", "Taiwan", "tw-tzh"),
    CountryRegion("TH", "Thailand", "th-th", ("thailande",)),
    CountryRegion("TR", "Turkey", "tr-tr", ("turkiye", "turquie")),
    CountryRegion("UA", "Ukraine", "ua-uk"),
    CountryRegion(
        "GB",
        "United Kingdom",
        "uk-en",
        ("uk", "great britain", "britain", "royaume uni", "angleterre"),
    ),
    CountryRegion(
        "US",
        "United States",
        "us-en",
        ("usa", "united states of america", "etats unis"),
    ),
    CountryRegion("VN", "Vietnam", "vn-vi"),
)


def _normalize_country_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", " ", ascii_value).strip()


def _build_country_index() -> dict[str, CountryRegion]:
    index = {}
    for region in COUNTRY_REGIONS:
        values = (region.code, region.name, *region.aliases)
        for value in values:
            index[_normalize_country_name(value)] = region
    return index


COUNTRY_INDEX = _build_country_index()


def resolve_country(value: str) -> CountryRegion | None:
    normalized = _normalize_country_name(value)
    if not normalized:
        return None

    known_region = COUNTRY_INDEX.get(normalized)
    if known_region is not None:
        return known_region

    if len(normalized) == 2 and normalized.isalpha():
        code = normalized.upper()
        return CountryRegion(code=code, name=code)
    return None


def build_engine_region_params(
    engine_name: str,
    filters_or_country: object,
) -> dict[str, str]:
    if isinstance(filters_or_country, Mapping):
        country = filters_or_country.get("country", "")
    else:
        country = getattr(filters_or_country, "country", filters_or_country)

    region = resolve_country(str(country or ""))
    if region is None:
        return {}

    engine = engine_name.lower()
    if engine == "google":
        return {"gl": region.code.lower()}
    if engine == "bing":
        return {"cc": region.code}
    if engine == "brave":
        return {"country": region.code.lower()}
    if engine == "duckduckgo" and region.duckduckgo_region:
        return {"kl": region.duckduckgo_region}
    return {}
