from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
import os
from dotenv import load_dotenv

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ✅ TEMPORARY FIX for local dev
load_dotenv()

router = APIRouter()
USER_TOKENS = {}
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

@router.get("/auth/google")
def auth_google():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        return {"error": "Missing Google OAuth environment variables."}

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    return RedirectResponse(auth_url)

@router.get("/auth/google/callback")
def auth_callback(request: Request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    USER_TOKENS["demo-user"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return JSONResponse({"message": "Gmail connected successfully."})

# ✅ NEW REUSABLE INTERNAL FUNCTION

def send_email_internal(to: str, subject: str, body: str) -> str:
    creds_data = USER_TOKENS.get("demo-user")
    if not creds_data:
        raise Exception("User not authenticated")

    creds = Credentials(**creds_data)
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = {"raw": raw}

    result = service.users().messages().send(userId="me", body=send_message).execute()
    return result["id"]

# MCP-compatible route (still works externally)
@router.post("/mcp/gmail/send")
def send_email_via_gmail(payload: dict):
    try:
        email_id = send_email_internal(
            to=payload.get("to"),
            subject=payload.get("subject"),
            body=payload.get("body", "")
        )
        return {"message": "Email sent!", "id": email_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
