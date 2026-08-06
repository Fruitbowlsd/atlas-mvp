"""
SAP Cloud ALM Test Management Anbindung.

Authentifizierung folgt dem von SAP dokumentierten OAuth2-Client-Credentials-Flow
(Client-ID/Secret gegen einen Token-Endpunkt, danach Bearer-Token gegen die API).

WICHTIG: Der genaue REST/OData-Pfad der Test-Management-API kann sich je nach
SAP Cloud ALM Tenant/API-Version unterscheiden -- vor dem produktiven Einsatz
gegen die aktuelle Dokumentation im SAP Business Accelerator Hub
(https://api.sap.com/package/SAPCloudALM) verifizieren. Der Pfad ist deshalb
hier bewusst konfigurierbar statt hartkodiert.
"""
import httpx


class SapCloudAlmError(Exception):
    pass


async def get_access_token(token_url: str, client_id: str, client_secret: str) -> str:
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.post(
                token_url,
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise SapCloudAlmError(f"Token-Anfrage fehlgeschlagen: {e}") from e
    token = resp.json().get("access_token")
    if not token:
        raise SapCloudAlmError("Keine access_token im Antwort-Payload gefunden")
    return token


async def fetch_test_cases(base_url: str, api_path: str, token: str) -> list[dict]:
    """
    Ruft Testfaelle ueber die konfigurierte API ab. Erwartet eine JSON-Antwort mit
    einer Liste von Objekten, die mindestens ein Titel-/Namensfeld und ein
    Status-Feld enthalten. Feldnamen variieren je nach API-Version -- werden
    tolerant ausgelesen (title/name/testCaseTitle, status/testStatus).
    """
    url = base_url.rstrip("/") + "/" + api_path.lstrip("/")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise SapCloudAlmError(f"Abruf der Testfaelle fehlgeschlagen: {e}") from e

    data = resp.json()
    items = data.get("value", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise SapCloudAlmError("Unerwartetes Antwortformat der SAP Cloud ALM API")

    normalized = []
    for item in items:
        title = item.get("title") or item.get("name") or item.get("testCaseTitle") or ""
        status = item.get("status") or item.get("testStatus") or ""
        normalized.append({"title": title, "status": status, "raw": item})
    return normalized
