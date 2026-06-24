import logging
from typing import Optional

from litestar import Controller, get, post, put, patch, delete
from litestar.exceptions import HTTPException

from app.core.services.curator_service import CuratorService
from app.core.domain.models.curator import Curator, AssignmentHistory
from app.api.schemas.curator_dto import (
    CuratorResponse,
    CuratorCreateRequest,
    CuratorUpdateRequest,
    AssignCuratorRequest,
    TransferRequest,
    AssignmentHistoryResponse,
)

logger = logging.getLogger(__name__)


def _to_curator_response(c: Curator) -> CuratorResponse:
    return CuratorResponse(
        id=c.id,
        full_name=c.full_name,
        login=c.login,
        email=c.email,
        role=c.role.value,
        status=c.status.value,
        avatar_url=c.avatar_url,
        created_at=c.created_at,
        last_activity=c.last_activity,
    )


def _to_assignment_response(e: AssignmentHistory) -> AssignmentHistoryResponse:
    return AssignmentHistoryResponse(
        id=e.id,
        message_id=e.message_id,
        from_curator_id=e.from_curator_id,
        to_curator_id=e.to_curator_id,
        assigned_by=e.assigned_by,
        reason=e.reason,
        created_at=e.created_at,
        metadata=e.metadata,
    )


class CuratorController(Controller):
    path = "/api/curators"

    @get()
    async def list_curators(
        self,
        curator_service: CuratorService,
        status: Optional[str] = None,
    ) -> list[CuratorResponse]:
        curators = await curator_service.get_all_curators(status=status)
        return [_to_curator_response(c) for c in curators]

    @post()
    async def create_curator(
        self,
        curator_service: CuratorService,
        data: CuratorCreateRequest,
    ) -> CuratorResponse:
        curator = await curator_service.create_curator(
            full_name=data.full_name,
            login=data.login,
            email=data.email,
            role=data.role,
            avatar_url=data.avatar_url,
        )
        return _to_curator_response(curator)

    @get("/{curator_id:str}")
    async def get_curator(
        self,
        curator_service: CuratorService,
        curator_id: str,
    ) -> CuratorResponse:
        curator = await curator_service.get_curator(curator_id)
        return _to_curator_response(curator)

    @put("/{curator_id:str}")
    async def update_curator(
        self,
        curator_service: CuratorService,
        curator_id: str,
        data: CuratorUpdateRequest,
    ) -> CuratorResponse:
        updates = {
            k: v
            for k, v in {
                "full_name": data.full_name,
                "login": data.login,
                "email": data.email,
                "role": data.role,
                "status": data.status,
                "avatar_url": data.avatar_url,
            }.items()
            if v is not None
        }
        curator = await curator_service.update_curator(curator_id, updates)
        return _to_curator_response(curator)

    @patch("/{curator_id:str}/status")
    async def set_curator_status(
        self,
        curator_service: CuratorService,
        curator_id: str,
        data: dict,
    ) -> CuratorResponse:
        status = data.get("status")
        if not status or status not in ("active", "inactive"):
            raise HTTPException(
                status_code=400, detail="Status must be 'active' or 'inactive'"
            )
        curator = await curator_service.set_curator_status(curator_id, status)
        return _to_curator_response(curator)

    @delete("/{curator_id:str}", status_code=200)
    async def delete_curator(
        self,
        curator_service: CuratorService,
        curator_id: str,
    ) -> dict:
        await curator_service.delete_curator(curator_id)
        return {"status": "success", "detail": f"Curator {curator_id} deleted"}


class AssignmentController(Controller):
    path = "/api"

    @post("/messages/{message_id:str}/assign")
    async def assign_curator(
        self,
        curator_service: CuratorService,
        message_id: str,
        data: AssignCuratorRequest,
    ) -> dict:
        message = await curator_service.assign_curator_to_message(
            message_id=message_id,
            curator_id=data.curator_id,
            assigned_by=None,
            reason=data.reason,
        )
        return {
            "status": "success",
            "message_id": message.id,
            "curator_id": message.curator_id,
        }

    @post("/messages/{message_id:str}/transfer")
    async def transfer_message(
        self,
        curator_service: CuratorService,
        message_id: str,
        data: TransferRequest,
    ) -> dict:
        message = await curator_service.transfer_message(
            message_id=message_id,
            from_curator_id=data.from_curator_id,
            to_curator_id=data.to_curator_id,
            assigned_by=None,
            reason=data.reason,
        )
        return {
            "status": "success",
            "message_id": message.id,
            "curator_id": message.curator_id,
        }

    @get("/messages/{message_id:str}/assignments")
    async def get_message_assignments(
        self,
        curator_service: CuratorService,
        message_id: str,
    ) -> list[AssignmentHistoryResponse]:
        history = await curator_service.get_message_assignment_history(message_id)
        return [_to_assignment_response(e) for e in history]

    @get("/curators/{curator_id:str}/assignments")
    async def get_curator_assignments(
        self,
        curator_service: CuratorService,
        curator_id: str,
    ) -> list[AssignmentHistoryResponse]:
        history = await curator_service.get_curator_assignment_history(curator_id)
        return [_to_assignment_response(e) for e in history]
