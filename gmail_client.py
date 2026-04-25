"""Gmail API client para creación de borradores."""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_service(client_id: str, client_secret: str) -> object:
    """Inicia OAuth2 flow y retorna servicio Gmail autenticado.

    Abre el browser del usuario para autorización en primera ejecución.
    """
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)
    return build("gmail", "v1", credentials=creds)


def build_gmail_message(to: str, subject: str, body_html: str) -> dict:
    """Construye mensaje MIME codificado en base64url para Gmail API."""
    msg = MIMEMultipart("alternative")
    msg["to"] = to
    msg["subject"] = subject
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def create_draft(service: object, to: str, subject: str, body_html: str) -> dict:
    """Crea un borrador en Gmail del usuario autenticado.

    Args:
        service: Servicio Gmail autenticado (de get_gmail_service).
        to: Email del destinatario.
        subject: Asunto del email.
        body_html: Cuerpo HTML del email.

    Returns:
        Dict con 'id' del draft creado.
    """
    message = build_gmail_message(to, subject, body_html)
    draft = (
        service.users()
        .drafts()
        .create(
            userId="me",
            body={"message": message},
        )
        .execute()
    )
    return draft
