from typing import Literal

from pydantic import BaseModel

class EmailAnalysis(BaseModel):
    sender: str
    subject: str
    requires_reply: bool
    priority: Literal["low", "medium", "high"]
    suggested_reply: str


class AgentResponse(BaseModel):
    emails: list[EmailAnalysis]
