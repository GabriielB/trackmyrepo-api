from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    repository: str = Field(
        min_length=3,
        max_length=255,
        examples=["flutter/flutter"],
    )

    display_name: str | None = None
    notes: str | None = None
    favorite: bool = False


class ProjectUpdate(BaseModel):
    display_name: str | None = None
    notes: str | None = None
    favorite: bool | None = None


class GitHubRepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    github_id: int

    owner: str
    name: str
    full_name: str

    description: str | None
    language: str | None

    stars: int
    forks: int
    open_issues_count: int

    default_branch: str | None
    archived: bool
    visibility: str | None

    html_url: str

    github_updated_at: datetime | None
    github_pushed_at: datetime | None
    last_synced_at: datetime


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str | None
    notes: str | None
    favorite: bool

    created_at: datetime
    updated_at: datetime

    repository: GitHubRepositoryResponse