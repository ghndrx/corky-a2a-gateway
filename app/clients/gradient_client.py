from typing import Optional, Dict, Any
import httpx


async def call_gradient_inference(
    *,
    endpoint_url: str,
    api_key: str,
    message: str,
    auth_scheme: str = "authorization_bearer",
    timeout_seconds: float = 30.0,
    extra_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    headers = _build_headers(api_key=api_key, auth_scheme=auth_scheme)

    payload: Dict[str, Any] = {"input": message}
    if extra_payload:
        payload.update(extra_payload)

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        resp = await client.post(endpoint_url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    return {"raw": data}


def _build_headers(*, api_key: str, auth_scheme: str) -> Dict[str, str]:
    scheme = (auth_scheme or "authorization_bearer").lower()
    if scheme == "x_api_key":
        return {"X-API-Key": api_key}
    return {"Authorization": f"Bearer {api_key}"}

