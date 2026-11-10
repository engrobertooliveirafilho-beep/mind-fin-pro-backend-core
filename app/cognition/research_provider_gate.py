"""Fail-closed research adapter; refuses synthetic or unverifiable result payloads."""
from urllib.parse import urlparse

class ResearchUnavailable(RuntimeError):
    status_code = 503
    code = "RESEARCH_PROVIDER_NOT_CONFIGURED"

def require_research_provider(mode: str, provider=None):
    if mode not in {"web_stub", "internal", "hybrid"}:
        raise ValueError("UNSUPPORTED_RESEARCH_MODE")
    if provider is None or not callable(provider):
        raise ResearchUnavailable("Real research provider is not configured; synthetic results are disabled.")
    return provider

def run_research(query: str, mode: str, provider=None):
    provider = require_research_provider(mode, provider)
    if not isinstance(query, str) or not query.strip():
        raise ValueError("EMPTY_RESEARCH_QUERY")
    try:
        results = provider(query=query, mode=mode)
    except Exception as exc:
        raise ResearchUnavailable("Research provider failed; no fallback synthesis is permitted.") from exc
    if not isinstance(results, list):
        raise ResearchUnavailable("Research provider returned an invalid result envelope.")
    validated = []
    for item in results:
        if not isinstance(item, dict):
            raise ResearchUnavailable("Research result must be an object.")
        title, snippet, source = item.get("title"), item.get("snippet"), item.get("source")
        if not all(isinstance(x, str) and x.strip() for x in (title, snippet, source)):
            raise ResearchUnavailable("Research result is missing title, snippet or source.")
        parsed = urlparse(source)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ResearchUnavailable("Research source must be an HTTPS URL; synthetic sources are rejected.")
        validated.append({"title": title.strip(), "snippet": snippet.strip(), "source": source})
    return validated
