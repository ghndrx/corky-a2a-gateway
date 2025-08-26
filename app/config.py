import os


def _get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def get_lmstudio_base_url() -> str:
    # Example: http://localhost:1234/v1
    return _get_env("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")


def get_lmstudio_model() -> str:
    # Example: The model name as exposed by LM Studio
    return _get_env("LMSTUDIO_MODEL", "lmstudio-community/small-llm")


def get_gradient_endpoint_url() -> str:
    return _get_env("GRADIENT_ENDPOINT_URL")


def get_gradient_api_key() -> str:
    return _get_env("GRADIENT_API_KEY")


def get_gradient_auth_scheme() -> str:
    return _get_env("GRADIENT_AUTH_SCHEME", "authorization_bearer").lower()


def get_do_fallback_url() -> str:
    return _get_env("DO_INFERENCE_URL")


def get_do_api_key() -> str:
    return _get_env("DO_INFERENCE_API_KEY")


def get_route_keywords() -> list[str]:
    raw = _get_env("ROUTE_KEYWORDS", "ai,model,ml,gpt,router,gradient")
    return [kw.strip().lower() for kw in raw.split(",") if kw.strip()]

