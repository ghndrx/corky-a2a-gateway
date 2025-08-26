from typing import Dict, Any
import httpx


async def call_lmstudio_chat(*, base_url: str, model: str, message: str, timeout_seconds: float = 30.0) -> Dict[str, Any]:
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": message}
        ],
        "temperature": 0.2,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return {"raw": data, "text": data.get("choices", [{}])[0].get("message", {}).get("content", "")}

