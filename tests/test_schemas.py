from datetime import datetime, timezone

from app.api.schemas.message_dto import MessageResponse, ReplyRequest


def test_message_response_creation():
    now = datetime.now(timezone.utc)
    resp = MessageResponse(
        id="msg:1",
        channel="telegram",
        sender="user1",
        content="hello",
        timestamp=now,
        metadata={"k": "v"},
    )

    assert resp.id == "msg:1"
    assert resp.channel == "telegram"
    assert resp.sender == "user1"
    assert resp.content == "hello"
    assert resp.timestamp == now
    assert resp.metadata == {"k": "v"}
    assert resp.recipient is None
    assert resp.subject is None


def test_message_response_with_optionals():
    now = datetime.now(timezone.utc)
    resp = MessageResponse(
        id="msg:2",
        channel="email",
        sender="a@b.com",
        content="body",
        timestamp=now,
        metadata={},
        recipient="c@d.com",
        subject="hi",
    )

    assert resp.recipient == "c@d.com"
    assert resp.subject == "hi"


def test_reply_request():
    req = ReplyRequest(message_id="orig:1", content="reply text")
    assert req.message_id == "orig:1"
    assert req.content == "reply text"
