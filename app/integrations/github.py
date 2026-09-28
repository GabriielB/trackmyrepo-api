import os
from datetime import datetime, timezone

import httpx


GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2026-03-10"


class RepositoryNotFoundError(Exception):
    pass


class GitHubAPIError(Exception):
    pass


def parse_github_datetime(
    value: str | None,
) -> datetime | None:
    if value is None:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def fetch_repository(
    owner: str,
    repository_name: str,
) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }

    github_token = os.getenv("GITHUB_TOKEN")

    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository_name}"
    )

    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(
                url,
                headers=headers,
            )

    except httpx.RequestError as error:
        raise GitHubAPIError(
            "Não foi possível conectar à API do GitHub."
        ) from error

    if response.status_code == 404:
        raise RepositoryNotFoundError()

    if response.status_code == 403:
        raise GitHubAPIError(
            "O GitHub recusou a requisição. "
            "O limite de requisições pode ter sido atingido."
        )

    if not response.is_success:
        raise GitHubAPIError(
            "A API do GitHub retornou "
            f"o status {response.status_code}."
        )

    data = response.json()

    return {
        "github_id": data["id"],
        "owner": data["owner"]["login"],
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data["description"],
        "language": data["language"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues_count": data["open_issues_count"],
        "default_branch": data["default_branch"],
        "archived": data["archived"],
        "visibility": data["visibility"],
        "html_url": data["html_url"],
        "github_updated_at": parse_github_datetime(
            data["updated_at"]
        ),
        "github_pushed_at": parse_github_datetime(
            data["pushed_at"]
        ),
        "last_synced_at": datetime.now(timezone.utc),
    }