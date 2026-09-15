#!/usr/bin/env python3
"""Remote Streamable HTTP MCP entry point for ChatGPT."""

import os
import secrets
from typing import Any
from urllib.parse import parse_qs

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from mailchimp_mcp import call


mcp = FastMCP(
    "ROCA Mailchimp",
    instructions=(
        "Manage the ROCA Ind. Machinery Mailchimp account. Treat send, schedule, "
        "subscription-status changes, and bulk modifications as write actions that "
        "require explicit user approval. Never resubscribe unsubscribed or cleaned members."
    ),
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "roca-mailchimp.onrender.com",
            "roca-mailchimp.onrender.com:*",
            "127.0.0.1:*",
            "localhost:*",
        ],
        allowed_origins=[
            "https://chatgpt.com",
            "https://www.chatgpt.com",
        ],
    ),
)


@mcp.tool()
def connection_status() -> dict[str, Any]:
    """Verify the Mailchimp connection and return account identity."""
    return call("connection_status", {})


@mcp.tool()
def list_audiences() -> dict[str, Any]:
    """List Mailchimp audiences and their high-level member statistics."""
    return call("list_audiences", {})


@mcp.tool()
def get_member(list_id: str, email: str) -> dict[str, Any]:
    """Get one audience member by email address."""
    return call("get_member", {"list_id": list_id, "email": email})


@mcp.tool()
def upsert_member(
    list_id: str,
    email: str,
    status_if_new: str,
    merge_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create or update a member; use subscribed, transactional, or pending only for a new member."""
    return call("upsert_member", {
        "list_id": list_id,
        "email": email,
        "status_if_new": status_if_new,
        "merge_fields": merge_fields,
    })


@mcp.tool()
def set_member_tags(list_id: str, email: str, tags: list[dict[str, str]]) -> dict[str, Any]:
    """Add or remove tags. Each item needs name and status set to active or inactive."""
    return call("set_member_tags", {"list_id": list_id, "email": email, "tags": tags})


@mcp.tool()
def list_campaigns(status: str | None = None, count: int = 20) -> dict[str, Any]:
    """List recent campaigns, optionally filtered by Mailchimp campaign status."""
    return call("list_campaigns", {"status": status, "count": count})


@mcp.tool()
def get_campaign(campaign_id: str) -> dict[str, Any]:
    """Get current settings, recipients, and status for one campaign."""
    return call("get_campaign", {"campaign_id": campaign_id})


@mcp.tool()
def create_campaign(
    list_id: str,
    subject_line: str,
    from_name: str,
    reply_to: str,
    preview_text: str | None = None,
    segment_id: int | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Create a regular Mailchimp campaign draft; this does not send it."""
    return call("create_campaign", locals())


@mcp.tool()
def set_campaign_content(campaign_id: str, html: str) -> dict[str, Any]:
    """Replace the HTML content of an existing campaign draft."""
    return call("set_campaign_content", {"campaign_id": campaign_id, "html": html})


@mcp.tool()
def send_test(campaign_id: str, test_emails: list[str]) -> dict[str, Any]:
    """Send a campaign test email only after the user explicitly approves the recipients."""
    return call("send_test", {"campaign_id": campaign_id, "test_emails": test_emails})


@mcp.tool()
def schedule_campaign(campaign_id: str, schedule_time: str) -> dict[str, Any]:
    """Schedule a campaign only after explicit user approval; time must be ISO 8601."""
    return call("schedule_campaign", {"campaign_id": campaign_id, "schedule_time": schedule_time})


@mcp.tool()
def send_campaign(campaign_id: str) -> dict[str, Any]:
    """Send a campaign immediately only after explicit user approval."""
    return call("send_campaign", {"campaign_id": campaign_id})


@mcp.tool()
def campaign_report(campaign_id: str) -> dict[str, Any]:
    """Get delivery and engagement results for a sent campaign."""
    return call("campaign_report", {"campaign_id": campaign_id})


class QueryTokenMiddleware:
    """Protect a private no-OAuth connector with a token embedded in its endpoint URL."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in {"http", "websocket"}:
            expected = os.environ.get("ROCA_MCP_ACCESS_TOKEN", "")
            supplied = parse_qs(scope.get("query_string", b"").decode()).get("token", [""])[0]
            if not expected or not secrets.compare_digest(supplied, expected):
                await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"text/plain")]})
                await send({"type": "http.response.body", "body": b"Unauthorized"})
                return
        await self.app(scope, receive, send)


app = QueryTokenMiddleware(mcp.streamable_http_app())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
