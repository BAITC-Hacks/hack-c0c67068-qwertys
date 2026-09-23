"""Redact credentials from structured and mixed diagnostic text before logging."""
from __future__ import annotations

import json
import re

_SECRET_KEYS = {"apikey", "token", "accesstoken", "refreshtoken", "password",
                "secret", "clientsecret", "authorization"}
_KEY = r"(?:api[_-]?key|(?:access[_-]?|refresh[_-]?)?token|password|(?:client[_-]?)?secret|authorization)"
_ASSIGNMENT = re.compile(
    r"(?<![\w-])([\"']?" + _KEY + r"[\"']?\s*[:=]\s*)"
    r'''(?:"(?:\\.|[^"\\])*(?:"|$)|'(?:\\.|[^'\\])*(?:'|$)|[^\s,;&}\]]+)''',
    re.IGNORECASE,
)


def _inline(text: str) -> str:
    text = re.sub(r"(?i)(bearer\s+)[^\s,;\"'}\]]+", r"\1[REDACTED]", text)
    text = _ASSIGNMENT.sub(lambda match: match.group(1) + '"[REDACTED]"', text)
    return re.sub(r"\b(?:sk-|nvapi-)[a-zA-Z0-9_-]+", "[REDACTED]", text)


def safe_summary(text: str) -> str:
    """Handle JSON keys/escaping structurally, with a fallback for mixed logs."""
    def redact(value):
        if isinstance(value, dict):
            return {key: "[REDACTED]" if re.sub(r"[-_]", "", key).lower() in _SECRET_KEYS
                    else redact(item) for key, item in value.items()}
        if isinstance(value, list):
            return [redact(item) for item in value]
        if isinstance(value, str):
            return _inline(value)
        return value

    try:
        value = json.loads(text)
        if isinstance(value, (dict, list)):
            return json.dumps(redact(value), ensure_ascii=False)
    except (ValueError, RecursionError):
        pass
    return _inline(text)
