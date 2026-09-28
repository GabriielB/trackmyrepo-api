from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.github import (
    GitHubAPIError,
    RepositoryNotFoundError,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.projects import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    create_project,
    delete_project,
    get_project_by_id,
    list_projects,
    refresh_project,
    update_project,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projetos"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona um repositório para monitoramento",
)
def create(
    data: ProjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_project(
            db,
            data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except RepositoryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Repositório não encontrado no GitHub.",
        )

    except ProjectAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Este repositório já está sendo monitorado.",
        )

    except GitHubAPIError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        )


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Lista os projetos monitorados",
)
def get_all(
    favorite: bool | None = None,
    db: Session = Depends(get_db),
):
    return list_projects(
        db,
        favorite,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Busca um projeto pelo ID",
)
def get_by_id(
    project_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_project_by_id(
            db,
            project_id,
        )

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado.",
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Atualiza informações do projeto",
)
def update(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_project(
            db,
            project_id,
            data,
        )

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado.",
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um projeto monitorado",
)
def delete(
    project_id: int,
    db: Session = Depends(get_db),
):
    try:
        delete_project(
            db,
            project_id,
        )

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado.",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/{project_id}/refresh",
    response_model=ProjectResponse,
    summary="Atualiza os dados do repositório no GitHub",
)
def refresh(
    project_id: int,
    db: Session = Depends(get_db),
):
    try:
        return refresh_project(
            db,
            project_id,
        )

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado.",
        )

    except RepositoryNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="O repositório não existe mais no GitHub.",
        )

    except GitHubAPIError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        )