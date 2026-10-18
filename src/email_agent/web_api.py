from pathlib import Path

import secrets
import base64
import binascii

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from email_agent.agent import email_agent
from email_agent.config import BASE_DIR, USERNAME, PASSWORD

app = FastAPI(title="Gmail AI Agent")

print(BASE_DIR)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

if not USERNAME or not PASSWORD:
    raise RuntimeError(
        "APP_USERNAME and APP_PASSWORD must be configured"
    )

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "emails": None,
            "error": None
        }
    )

@app.middleware("http")
async def basic_auth(request: Request, call_next):

    authorization = request.headers.get("Authorization", "")

    authenticated = False

    if authorization.startswith("Basic "):
        try:
            encoded = authorization[6:]
            decoded = base64.b64decode(
                encoded, validate=True
            ).decode("utf-8")

            username, password = decoded.split(":", 1)

            username_valid = secrets.compare_digest(
                username.encode("utf-8"),
                USERNAME.encode("utf-8"),
            )

            password_valid = secrets.compare_digest(
                password.encode("utf-8"),
                PASSWORD.encode("utf-8"),
            )

            authenticated = username_valid and password_valid

        except (ValueError, UnicodeDecodeError, binascii.Error):
            authenticated = False

    if not authenticated:
        return Response(
            status_code=401,
            headers={
                "WWW-Authenticate": 'Basic realm="Gmail Agent"',
                "Cache-Control": "no-store",
            },
            content="Authentication required",
        )

    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_emails(request: Request):

    try:
        result = await email_agent.run(
            """
            Read my latest 5 Gmail emails.

            Analyze each email and determine:
            1. Whether it requires a reply
            2. Its priority (low, medium, high)
            3. A suggested professional reply

            Do not send emails.
            """
        )

        emails = result.output.emails

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "emails": emails,
                "error": None
            }
        )

    except Exception:
        # Log detailed errors server-side in a production application.
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "emails": None,
                "error": (
                    "Unable to analyze emails. "
                    "Check Gmail and AI configuration."
                )
            },
            status_code=500
        )
