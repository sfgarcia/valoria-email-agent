# tests/test_gmail_client.py
from unittest.mock import MagicMock
from gmail_client import create_draft, build_gmail_message


def test_build_gmail_message_encodes_correctly():
    import base64

    msg_bytes = build_gmail_message(
        to="test@example.com",
        subject="Test Subject",
        body_html="<p>Hello</p>",
    )
    assert "raw" in msg_bytes
    decoded = base64.urlsafe_b64decode(msg_bytes["raw"] + "==")
    assert b"test@example.com" in decoded
    assert b"Test Subject" in decoded


def test_create_draft_calls_gmail_api():
    mock_service = MagicMock()
    mock_service.users().drafts().create().execute.return_value = {"id": "draft123"}

    result = create_draft(
        service=mock_service,
        to="cliente@ejemplo.cl",
        subject="Email Valoria",
        body_html="<p>Hola</p>",
    )

    mock_service.users().drafts().create.assert_called()
    assert result["id"] == "draft123"
