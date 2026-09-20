"""Consulta y cambia el estado (activo/pausado) del workflow de GitHub Actions."""

import requests

API_BASE = "https://api.github.com"
WORKFLOW_FILE = "check-deals.yml"


def get_workflow_state(repo: str, github_token: str) -> str:
    """Devuelve 'active' o 'disabled_manually'."""
    response = requests.get(
        f"{API_BASE}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}",
        headers=_headers(github_token),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["state"]


def set_workflow_enabled(repo: str, github_token: str, enabled: bool) -> None:
    action = "enable" if enabled else "disable"
    response = requests.put(
        f"{API_BASE}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/{action}",
        headers=_headers(github_token),
        timeout=10,
    )
    response.raise_for_status()


def _headers(github_token: str) -> dict:
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
