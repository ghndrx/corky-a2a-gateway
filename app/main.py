from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from a2a.types import (
    Message as A2AMessage,
    TextPart as A2ATextPart,
    Role as A2ARole,
    SendMessageRequest as A2ASendMessageRequest,
    SendMessageSuccessResponse as A2ASendMessageSuccessResponse,
)

from .config import (
    get_lmstudio_base_url,
    get_lmstudio_model,
    get_gradient_endpoint_url,
    get_gradient_api_key,
    get_gradient_auth_scheme,
    get_do_fallback_url,
    get_do_api_key,
)
from .router import decide_route
from .clients.lmstudio_client import call_lmstudio_chat
from .clients.gradient_client import call_gradient_inference
from .clients.do_client import call_do_inference


app = FastAPI(title="corky-a2a-gateway", version="0.1.0")


class RouteRequest(BaseModel):
    message: str = Field(..., description="User message to route")
    route_hint: Optional[str] = Field(None, description="Optional explicit route: 'lmstudio'|'gradient'|'do'")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional JSON metadata")


class RouteResponse(BaseModel):
    route: str
    output: Dict[str, Any]


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/route", response_model=RouteResponse)
async def route_message(req: RouteRequest) -> RouteResponse:
    route = decide_route(message=req.message, explicit_hint=req.route_hint)

    if route == "lmstudio":
        base_url = get_lmstudio_base_url()
        model = get_lmstudio_model()
        result = await call_lmstudio_chat(base_url=base_url, model=model, message=req.message)
        return RouteResponse(route=route, output=result)

    if route == "gradient":
        endpoint_url = get_gradient_endpoint_url()
        api_key = get_gradient_api_key()
        auth_scheme = get_gradient_auth_scheme()
        if not endpoint_url or not api_key:
            raise HTTPException(status_code=500, detail="Missing Gradient config")
        try:
            result = await call_gradient_inference(
                endpoint_url=endpoint_url,
                api_key=api_key,
                message=req.message,
                auth_scheme=auth_scheme,
                extra_payload={"metadata": req.metadata} if req.metadata else None,
            )
            return RouteResponse(route=route, output=result)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Gradient call failed: {exc}")

    if route == "do":
        endpoint_url = get_do_fallback_url()
        api_key = get_do_api_key()
        if not endpoint_url or not api_key:
            raise HTTPException(status_code=500, detail="Missing DigitalOcean config")
        try:
            result = await call_do_inference(endpoint_url=endpoint_url, api_key=api_key, message=req.message)
            return RouteResponse(route=route, output=result)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"DO call failed: {exc}")

    raise HTTPException(status_code=400, detail=f"Unknown route: {route}")


# Minimal A2A JSON-RPC-like endpoint using a2a types for schema parity
class A2ASendPayload(BaseModel):
    id: str
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]


@app.post("/a2a")
async def a2a_endpoint(payload: A2ASendPayload) -> Dict[str, Any]:
    if payload.method not in {"messages.send_message", "messages.sendStreamingMessage"}:
        raise HTTPException(status_code=404, detail="Method not found")

    params = payload.params or {}
    message_obj = params.get("message")
    if not message_obj:
        raise HTTPException(status_code=400, detail="Missing message in params")

    parts = message_obj.get("parts") or []
    user_text = ""
    for p in parts:
        if (p or {}).get("kind") == "text" and "text" in p:
            user_text = p["text"]
            break
    if not user_text:
        raise HTTPException(status_code=400, detail="No text part found")

    result = await call_lmstudio_chat(
        base_url=get_lmstudio_base_url(),
        model=get_lmstudio_model(),
        message=user_text,
    )

    return {
        "jsonrpc": "2.0",
        "id": payload.id,
        "result": {
            "task": {
                "id": "task-1",
                "status": {"state": "completed"},
                "artifacts": [],
                "history": [
                    {
                        "role": "agent",
                        "parts": [
                            {"kind": "text", "text": result.get("text", "")} 
                        ],
                    }
                ],
            }
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=False)

