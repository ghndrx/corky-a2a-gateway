# corky-a2a-gateway

FastAPI gateway that exposes an A2A-compatible endpoint and routes to LM Studio locally, with fallbacks to Gradient and DigitalOcean inference endpoints.

## Run locally

1. Install deps:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure LM Studio is running locally (OpenAI-compatible server) at `http://localhost:1234/v1` and a small model is loaded.

3. Start server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

4. Test REST route:

```bash
curl -s http://localhost:8080/healthz
curl -s -X POST http://localhost:8080/route -H 'content-type: application/json' -d '{"message":"hello"}'
```

5. Test A2A endpoint:

```bash
curl -s -X POST http://localhost:8080/a2a -H 'content-type: application/json' -d '{
  "id": "1",
  "jsonrpc": "2.0",
  "method": "messages.send_message",
  "params": {
    "message": {"role": "user", "parts": [{"kind": "text", "text": "Say hi"}]}
  }
}' | jq
```

## Config

- `LMSTUDIO_BASE_URL` (default `http://localhost:1234/v1`)
- `LMSTUDIO_MODEL` (default `lmstudio-community/small-llm`)
- `GRADIENT_ENDPOINT_URL`, `GRADIENT_API_KEY`, `GRADIENT_AUTH_SCHEME` (default bearer)
- `DO_INFERENCE_URL`, `DO_INFERENCE_API_KEY`
- `ROUTE_KEYWORDS` comma list for routing heuristic

## Notes

- A2A type references from the SDK are used for schema parity. See the SDK docs: https://a2a-protocol.org/latest/sdk/python/api/
