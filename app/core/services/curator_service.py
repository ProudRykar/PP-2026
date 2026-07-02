import logging
import re
from typing import Optional, List
from uuid import uuid4

from app.core.domain.models.curator import Curator, AssignmentHistory
from app.core.domain.models.channel_type import CuratorRole, CuratorStatus
from app.core.domain.models.message import Message
from app.core.domain.models.client import Client
from app.core.ports.curator_repository import (
    CuratorRepository,
    AssignmentHistoryRepository,
)
from app.core.ports.message_repository import MessageRepository
from app.core.ports.client_repository import ClientRepository
from app.core.errors.curator import (
    CuratorNotFoundError,
    CuratorValidationError,
    CuratorAssignmentError,
    CuratorAlreadyAssignedError,
)
from app.events import broadcast_message

logger = logging.getLogger(__name__)


def _extract_external_id(raw: str) -> str:
    match = re.search(r"<([^>]+)>", raw)
    return match.group(1) if match else raw


class CuratorService:
    def __init__(
        self,
        curator_repository: CuratorRepository,
        assignment_repository: AssignmentHistoryRepository,
        message_repository: MessageRepository,
        client_repository: ClientRepository,
    ):
        self._curator_repo = curator_repository
        self._assignment_repo = assignment_repository
        self._message_repo = message_repository
        self._client_repo = client_repository

    async def create_curator(
        self,
        full_name: str,
        login: str,
        email: str,
        role: str = "agent",
        avatar_url: Optional[str] = None,
    ) -> Curator:
        if not full_name or not full_name.strip():
            raise CuratorValidationError("ФИО не может быть пустым")
        if not login or not login.strip():
            raise CuratorValidationError("Логин не может быть пустым")
        if not email or not email.strip():
            raise CuratorValidationError("Email не может быть пустым")

        existing = await self._curator_repo.get_by_login(login)
        if existing:
            raise CuratorValidationError(f"Куратор с логином '{login}' уже существует")

        try:
            parsed_role = CuratorRole(role)
        except ValueError:
            parsed_role = CuratorRole.AGENT

        curator = Curator(
            id=f"curator:{uuid4().hex}",
            full_name=full_name.strip(),
            login=login.strip(),
            email=email.strip(),
            role=parsed_role,
            avatar_url=avatar_url,
        )
        await self._curator_repo.save(curator)
        logger.info(f"Curator created: {curator.id} ({curator.login})")
        return curator

    async def get_curator(self, curator_id: str) -> Curator:
        curator = await self._curator_repo.get_by_id(curator_id)
        if not curator:
            raise CuratorNotFoundError(curator_id)
        return curator

    async def get_all_curators(self, status: Optional[str] = None) -> List[Curator]:
        return await self._curator_repo.get_all(status=status)

    async def update_curator(
        self,
        curator_id: str,
        updates: dict,
    ) -> Curator:
        curator = await self._curator_repo.get_by_id(curator_id)
        if not curator:
            raise CuratorNotFoundError(curator_id)

        if "full_name" in updates:
            curator.full_name = updates["full_name"]
        if "login" in updates:
            existing = await self._curator_repo.get_by_login(updates["login"])
            if existing and existing.id != curator_id:
                raise CuratorValidationError(f"Логин '{updates['login']}' уже занят")
            curator.login = updates["login"]
        if "email" in updates:
            curator.email = updates["email"]
        if "role" in updates:
            curator.role = CuratorRole(updates["role"])
        if "status" in updates:
            curator.status = CuratorStatus(updates["status"])
        if "avatar_url" in updates:
            curator.avatar_url = updates["avatar_url"]

        await self._curator_repo.update(curator)
        logger.info(f"Curator updated: {curator.id}")
        return curator

    async def set_curator_status(self, curator_id: str, status: str) -> Curator:
        curator = await self._curator_repo.get_by_id(curator_id)
        if not curator:
            raise CuratorNotFoundError(curator_id)
        curator.status = CuratorStatus(status)
        await self._curator_repo.update(curator)
        logger.info(f"Curator {curator.id} status set to {status}")
        return curator

    async def delete_curator(self, curator_id: str) -> None:
        await self._curator_repo.delete(curator_id)
        logger.info(f"Curator deleted: {curator_id}")

    async def _find_client_for_message(self, message: Message) -> Optional[Client]:
        external_id = _extract_external_id(message.sender_id)
        client = await self._client_repo.find_by_channel(message.channel, external_id)
        if not client and "@" in external_id:
            client = await self._client_repo.find_by_email(external_id)
        return client

    async def _update_client_curator(self, message: Message, curator_id: Optional[str]) -> None:
        client = await self._find_client_for_message(message)
        if client and client.curator_id != curator_id:
            client.curator_id = curator_id
            await self._client_repo.update(client)
            logger.info(f"Client {client.id} curator updated to {curator_id}")

    async def assign_curator_to_message(
        self,
        message_id: str,
        curator_id: str,
        assigned_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Message:
        curator = await self._curator_repo.get_by_id(curator_id)
        if not curator:
            raise CuratorNotFoundError(curator_id)
        if curator.status != CuratorStatus.ACTIVE:
            raise CuratorAssignmentError("Нельзя назначить неактивного куратора")

        message = await self._message_repo.get_message_by_id(message_id)
        if not message:
            from app.core.errors.message import MessageNotFoundError

            raise MessageNotFoundError(message_id)

        if message.curator_id == curator_id:
            raise CuratorAlreadyAssignedError()

        prev_curator_id = message.curator_id

        entry = AssignmentHistory(
            id=f"assign:{uuid4().hex}",
            message_id=message_id,
            from_curator_id=prev_curator_id,
            to_curator_id=curator_id,
            assigned_by=assigned_by,
            reason=reason,
        )
        await self._assignment_repo.save(entry)

        message.curator_id = curator_id
        await self._message_repo.update_curator(message_id, curator_id)
        await self._update_client_curator(message, curator_id)
        logger.info(f"Message {message_id} assigned to curator {curator_id}")

        await broadcast_message(
            {
                "type": "curator_assigned",
                "message_id": message_id,
                "curator_id": curator_id,
                "assigned_by": assigned_by,
                "assignment_id": entry.id,
                "timestamp": entry.created_at.isoformat(),
            }
        )
        return message

    async def transfer_message(
        self,
        message_id: str,
        from_curator_id: str,
        to_curator_id: str,
        assigned_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Message:
        target_curator = await self._curator_repo.get_by_id(to_curator_id)
        if not target_curator:
            raise CuratorNotFoundError(to_curator_id)
        if target_curator.status != CuratorStatus.ACTIVE:
            raise CuratorAssignmentError("Нельзя передать неактивному куратору")

        message = await self._message_repo.get_message_by_id(message_id)
        if not message:
            from app.core.errors.message import MessageNotFoundError

            raise MessageNotFoundError(message_id)

        entry = AssignmentHistory(
            id=f"transfer:{uuid4().hex}",
            message_id=message_id,
            from_curator_id=from_curator_id,
            to_curator_id=to_curator_id,
            assigned_by=assigned_by,
            reason=reason,
        )
        await self._assignment_repo.save(entry)

        message.curator_id = to_curator_id
        await self._message_repo.update_curator(message_id, to_curator_id)
        await self._update_client_curator(message, to_curator_id)
        logger.info(
            f"Message {message_id} transferred from {from_curator_id} to {to_curator_id}"
        )

        await broadcast_message(
            {
                "type": "curator_transferred",
                "message_id": message_id,
                "from_curator_id": from_curator_id,
                "to_curator_id": to_curator_id,
                "assigned_by": assigned_by,
                "reason": reason,
                "assignment_id": entry.id,
                "timestamp": entry.created_at.isoformat(),
            }
        )
        return message

    async def get_message_assignment_history(
        self, message_id: str
    ) -> List[AssignmentHistory]:
        return await self._assignment_repo.get_by_message(message_id)

    async def get_curator_assignment_history(
        self, curator_id: str
    ) -> List[AssignmentHistory]:
        return await self._assignment_repo.get_by_curator(curator_id)

    async def get_messages_by_curator(
        self,
        curator_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        return await self._message_repo.get_messages(
            curator_id=curator_id,
            limit=limit,
            offset=offset,
        )
