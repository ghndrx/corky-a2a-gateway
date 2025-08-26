from typing import Dict, Any
import httpx


async def call_do_inference(*, endpoint_url: str, api_key: str, message: str, timeout_seconds: float = 30.0) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}"}
    payload: Dict[str, Any] = {"input": message}
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        resp = await client.post(endpoint_url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return {"raw": data}

