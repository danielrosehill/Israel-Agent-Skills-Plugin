"""Provider backends for fiber-availability-check.

Each provider exposes a `check(city, street, house, entrance)` function returning
a normalized dict:

  {
    "provider": "bezeq" | "hot" | ...,
    "status":   "available" | "coming_soon" | "unavailable" | "address_not_found" | "unknown" | "error",
    "status_code": <provider-specific int or None>,
    "summary":  "<human-readable one-liner>",
    "error":    "<string or None>",
    "raw":      <provider raw response for debugging>,
  }
"""
from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (israel-fiber-check skill)"


def _get(url: str, headers: dict | None = None, timeout: int = 20):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    with urlopen(Request(url, headers=h), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _post(url: str, payload: dict, headers: dict | None = None, timeout: int = 20):
    h = {
        "User-Agent": UA,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
    if headers:
        h.update(headers)
    body = json.dumps(payload).encode("utf-8")
    with urlopen(Request(url, data=body, method="POST", headers=h), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------- Bezeq ----------

BEZEQ_BASE = "https://www.bezeq.co.il"
BEZEQ_AC = BEZEQ_BASE + "/umbraco/api/FormWebApi/GetAutoCompleteAddressValue"
BEZEQ_CHECK = BEZEQ_BASE + "/umbraco/api/FormWebApi/CheckAddress"

_BEZEQ_STATUS = {
    1: ("available", "Bfiber is already deployed — address is connectable now."),
    2: ("coming_soon", "Bfiber deployment is planned / in progress for this address."),
    3: ("unavailable", "Bfiber is not available at this address."),
}


def _bezeq_resolve(text: str, search_type: int, city_id: str = "") -> dict | None:
    data = _get(BEZEQ_AC + "?" + urlencode({"SearchText": text, "SearchType": search_type, "City": city_id}))
    if not isinstance(data, list) or not data:
        return None
    for item in data:
        if item.get("value", "").strip() == text.strip():
            return item
    return data[0]


def check_bezeq(city: str, street: str, house: str, entrance: str = "") -> dict:
    try:
        city_hit = _bezeq_resolve(city, 0)
        if not city_hit:
            return {"provider": "bezeq", "status": "address_not_found", "status_code": None,
                    "summary": f"Bezeq could not resolve city {city!r}.", "error": None, "raw": None}
        street_hit = _bezeq_resolve(street, 1, city_hit["id"])
        payload = {
            "CityId": city_hit["id"],
            "StreetId": street_hit["id"] if street_hit else "",
            "House": str(house),
            "Street": street,
            "City": city,
            "Entrance": entrance or "",
        }
        raw = _post(BEZEQ_CHECK, payload)
        err = raw.get("ErrorMessage") or ""
        status_num = raw.get("Status")
        if err == "כתובת לא נמצאה":
            label, summary = "address_not_found", "Bezeq could not resolve this address."
        else:
            label, summary = _BEZEQ_STATUS.get(status_num, ("unknown", f"Unexpected Bezeq status: {status_num!r}"))
        return {"provider": "bezeq", "status": label, "status_code": status_num,
                "summary": summary, "error": err or None, "raw": raw}
    except Exception as e:
        return {"provider": "bezeq", "status": "error", "status_code": None,
                "summary": f"Bezeq check failed: {e}", "error": str(e), "raw": None}


# ---------- HOT ----------

HOT_BASE = "https://www.hot.net.il/HotCmsApiFront"
HOT_CITIES = HOT_BASE + "/api/Marketing/GetCities"
HOT_STREETS = HOT_BASE + "/api/Marketing/GetStreets"
HOT_CHECK = HOT_BASE + "/api/Marketing/CheckAddressForFiber"
HOT_HEADERS = {
    "Referer": "https://www.hot.net.il/heb/internet/fiber-check/",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.hot.net.il",
}


def _hot_unwrap(resp):
    """HOT responses are {isError, data, ...}, sometimes JSON-encoded twice. Return data list or None."""
    if isinstance(resp, str):
        try:
            resp = json.loads(resp)
        except json.JSONDecodeError:
            return None
    if isinstance(resp, dict):
        if resp.get("isError"):
            return None
        return resp.get("data")
    if isinstance(resp, list):
        return resp
    return None


def _hot_full(resp):
    """Like _hot_unwrap but returns the full decoded dict (for the final CheckAddressForFiber call)."""
    if isinstance(resp, str):
        try:
            resp = json.loads(resp)
        except json.JSONDecodeError:
            return {}
    return resp if isinstance(resp, dict) else {}


def _hot_find(items, value_key, needle):
    if not isinstance(items, list):
        return None
    needle = needle.strip()
    for it in items:
        if str(it.get(value_key, "")).strip() == needle:
            return it
    return None


def check_hot(city: str, street: str, house: str, entrance: str = "") -> dict:
    try:
        cities = _hot_unwrap(_post(HOT_CITIES, {}, HOT_HEADERS))
        city_hit = _hot_find(cities, "cityName", city)
        if not city_hit:
            return {"provider": "hot", "status": "address_not_found", "status_code": None,
                    "summary": f"HOT could not resolve city {city!r}.", "error": None, "raw": None}
        streets = _hot_unwrap(_post(HOT_STREETS, {"cityId": city_hit["cityId"]}, HOT_HEADERS))
        street_hit = _hot_find(streets, "streetName", street)
        if not street_hit:
            return {"provider": "hot", "status": "address_not_found", "status_code": None,
                    "summary": f"HOT could not resolve street {street!r} in {city}.",
                    "error": None, "raw": {"cityId": city_hit["cityId"]}}
        payload = {
            "cityId": city_hit["cityId"],
            "streetId": street_hit["streetId"],
            "houseNumber": str(house),
            "entrance": entrance or "",
            "apartment": "",
            "HotCustomerInd": "N",
            "SendInfoBySMSInd": "N",
        }
        raw = _hot_full(_post(HOT_CHECK, payload, HOT_HEADERS))
        is_error = raw.get("isError")
        data = raw.get("data")
        msg_code = raw.get("messageCode")
        if is_error and data is None:
            label = "unavailable"
            summary = "HOT fiber is not available at this address."
        elif not is_error and data:
            label = "available"
            summary = "HOT fiber is available at this address."
        else:
            label = "unknown"
            summary = f"Unexpected HOT response (messageCode={msg_code!r})."
        return {"provider": "hot", "status": label, "status_code": msg_code,
                "summary": summary, "error": raw.get("messageDesc"), "raw": raw}
    except Exception as e:
        return {"provider": "hot", "status": "error", "status_code": None,
                "summary": f"HOT check failed: {e}", "error": str(e), "raw": None}


# ---------- Registry ----------

PROVIDERS = {
    "bezeq": check_bezeq,
    "hot": check_hot,
}

# Documented-but-not-implemented providers (returned for transparency when --all is used):
UNSUPPORTED = {
    "partner": "Partner does not publish an address-level fiber check — their public form is a lead-capture only (name + phone), with no address verification. Nothing reliable to scrape.",
    "cellcom": "Cellcom's fiber checker is a React SPA behind the Imperva/Incapsula WAF with dynamically assembled endpoint URLs. Would require a headless-browser session; not implemented in this skill (Tier 1 scope).",
    "ibc": "IBC / Unlimited brand sites are offline or parked at time of authoring; no public address-availability tool exists.",
}
