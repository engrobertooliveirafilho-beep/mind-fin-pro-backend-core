"""Fail-closed gate for Step452; no synthetic research results are returned."""
class ResearchUnavailable(RuntimeError):
    status_code = 503
    code = "RESEARCH_PROVIDER_NOT_CONFIGURED"

def require_research_provider(mode: str, provider=None):
    if mode not in {"web_stub", "internal", "hybrid"}:
        raise ValueError("UNSUPPORTED_RESEARCH_MODE")
    if provider is None or not callable(provider):
        raise ResearchUnavailable("Real research provider is not configured; synthetic results are disabled.")
    return provider
