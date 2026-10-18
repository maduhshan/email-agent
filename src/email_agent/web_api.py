from pathlib import Path

from fastapi import  FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from email_agent.agent import email_agent
from email_agent.config import BASE_DIR

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
