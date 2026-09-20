"""Cliente para Hotels Com Provider (RapidAPI): precio total de alojamiento."""

import re
from dataclasses import dataclass
from datetime import datetime

import requests

REGIONS_URL = "https://{host}/v2/regions"
HOTELS_SEARCH_URL = "https://{host}/v3/hotels/search"


@dataclass
class HotelOffer:
    name: str
    total_price: float
    currency: str
    nights: int
    link: str


def find_cheapest_hotel(
    destination_name: str,
    destination_code: str,
    checkin: str,
    checkout: str,
    currency: str,
    api_key: str,
    api_host: str,
) -> HotelOffer | None:
    """Busca el hotel mas barato en destination_name para las fechas dadas, o
    None si no se encuentra ninguno (nunca lanza excepcion por esto: el aviso
    de vuelo debe poder mandarse igual aunque el hotel falle)."""
    try:
        regions = _search_regions(destination_name, api_key, api_host)
        region_id = select_region_id(regions, destination_code)
        if region_id is None:
            return None

        properties = _search_hotels(region_id, checkin, checkout, api_key, api_host)
        nights = nights_between(checkin, checkout)
        return pick_cheapest(properties, currency, nights)
    except requests.RequestException:
        return None


def _search_regions(query: str, api_key: str, api_host: str) -> list[dict]:
    response = requests.get(
        REGIONS_URL.format(host=api_host),
        params={"query": query, "locale": "es_ES", "domain": "ES"},
        headers=_headers(api_key, api_host),
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def _search_hotels(region_id: str, checkin: str, checkout: str, api_key: str, api_host: str) -> list[dict]:
    response = requests.get(
        HOTELS_SEARCH_URL.format(host=api_host),
        params={
            "region_id": region_id,
            "locale": "es_ES",
            "domain": "ES",
            "checkin_date": checkin,
            "checkout_date": checkout,
            "adults_number": "1",
            "sort_order": "PRICE_LOW_TO_HIGH",
        },
        headers=_headers(api_key, api_host),
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("data", {}).get("properties", [])


def _headers(api_key: str, api_host: str) -> dict:
    return {"x-rapidapi-host": api_host, "x-rapidapi-key": api_key}


def select_region_id(regions: list[dict], iata_code: str) -> str | None:
    """Entre los resultados de busqueda por nombre, elige el que coincide con
    el codigo IATA del vuelo (evita confundir ciudades homonimas). Si ninguno
    coincide, se queda con el primer resultado como mejor aproximacion."""
    for region in regions:
        airport = (region.get("hierarchyInfo") or {}).get("airport") or {}
        if airport.get("airportCode") == iata_code:
            return region.get("gaiaId")
    return regions[0].get("gaiaId") if regions else None


def pick_cheapest(properties: list[dict], currency: str, nights: int) -> HotelOffer | None:
    offers = [offer for offer in (_to_offer(p, currency, nights) for p in properties) if offer]
    return min(offers, key=lambda offer: offer.total_price) if offers else None


def _to_offer(property_data: dict, currency: str, nights: int) -> HotelOffer | None:
    price = property_data.get("price") or {}
    summary = price.get("priceSummary") or {}
    definition = summary.get("definition") or {}
    price_text = definition.get("displayPrice")
    price_value = extract_number(price_text) if price_text else None
    if price_value is None:
        return None

    link = property_data.get("link", "")
    return HotelOffer(
        name=property_data.get("name", "un alojamiento"),
        total_price=price_value,
        currency=currency,
        nights=nights,
        link=f"https://www.hotels.com{link}" if link else "",
    )


def extract_number(text: str) -> float | None:
    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not match:
        return None
    return float(match.group().replace(",", "."))


def nights_between(checkin: str, checkout: str) -> int:
    return (datetime.fromisoformat(checkout) - datetime.fromisoformat(checkin)).days
