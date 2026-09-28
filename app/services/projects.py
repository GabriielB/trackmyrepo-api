from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.integrations.github import fetch_repository
from app.models.project import GitHubRepository, TrackedProject
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectAlreadyExistsError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


def get_project_by_id(
    db: Session,
    project_id: int,
) -> TrackedProject:
    statement = (
        select(TrackedProject)
        .options(joinedload(TrackedProject.repository))
        .where(TrackedProject.id == project_id)
    )

    project = db.scalar(statement)

    if project is None:
        raise ProjectNotFoundError()

    return project


def list_projects(
    db: Session,
    favorite: bool | None = None,
):
    statement = (
        select(TrackedProject)
        .options(joinedload(TrackedProject.repository))
        .order_by(TrackedProject.created_at.desc())
    )

    if favorite is not None:
        statement = statement.where(
            TrackedProject.favorite == favorite
        )

    return db.scalars(statement).all()


def create_project(
    db: Session,
    data: ProjectCreate,
) -> TrackedProject:
    repository_identifier = (
        data.repository
        .strip()
        .strip("/")
    )

    parts = repository_identifier.split("/")

    if len(parts) != 2 or not all(parts):
        raise ValueError(
            "O repositório deve estar no formato owner/repositorio."
        )

    owner, repository_name = parts

    github_data = fetch_repository(
        owner,
        repository_name,
    )

    existing_repository = db.scalar(
        select(GitHubRepository).where(
            GitHubRepository.github_id
            == github_data["github_id"]
        )
    )

    if existing_repository:
        raise ProjectAlreadyExistsError()

    repository = GitHubRepository(
        **github_data
    )

    project = TrackedProject(
        repository=repository,
        display_name=(
            data.display_name
            or github_data["name"]
        ),
        notes=data.notes,
        favorite=data.favorite,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def update_project(
    db: Session,
    project_id: int,
    data: ProjectUpdate,
) -> TrackedProject:
    project = get_project_by_id(
        db,
        project_id,
    )

    changes = data.model_dump(
        exclude_unset=True
    )

    if "display_name" in changes:
        project.display_name = changes["display_name"]

    if "notes" in changes:
        project.notes = changes["notes"]

    if "favorite" in changes:
        project.favorite = changes["favorite"]

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project_id: int,
) -> None:
    project = get_project_by_id(
        db,
        project_id,
    )

    repository = project.repository

    db.delete(repository)
    db.commit()


def refresh_project(
    db: Session,
    project_id: int,
) -> TrackedProject:
    project = get_project_by_id(
        db,
        project_id,
    )

    repository = project.repository

    github_data = fetch_repository(
        repository.owner,
        repository.name,
    )

    for field, value in github_data.items():
        setattr(
            repository,
            field,
            value,
        )

    db.commit()
    db.refresh(project)

    return project