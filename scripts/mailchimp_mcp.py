#!/usr/bin/env python3
"""Small dependency-free Mailchimp MCP server for the ROCA plugin."""

import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


TOOLS = [
    ("connection_status", "Verify the Mailchimp connection and return account identity.", {}),
    ("list_audiences", "List Mailchimp audiences.", {}),
    ("get_member", "Get one audience member by email.", {"list_id": "string", "email": "string"}),
    ("upsert_member", "Create or update a member. status_if_new must be subscribed, transactional, or pending.", {"list_id": "string", "email": "string", "status_if_new": "string", "merge_fields": "object?"}),
    ("set_member_tags", "Add or remove tags for an audience member.", {"list_id": "string", "email": "string", "tags": "array"}),
    ("list_campaigns", "List recent campaigns, optionally filtered by status.", {"status": "string?", "count": "integer?"}),
    ("get_campaign", "Get campaign settings and status.", {"campaign_id": "string"}),
    ("create_campaign", "Create a regular campaign draft for an audience and optional saved segment.", {"list_id": "string", "subject_line": "string", "from_name": "string", "reply_to": "string", "preview_text": "string?", "segment_id": "integer?", "title": "string?"}),
    ("set_campaign_content", "Set HTML content for a campaign draft.", {"campaign_id": "string", "html": "string"}),
    ("send_test", "Send a campaign test email after explicit user approval.", {"campaign_id": "string", "test_emails": "array"}),
    ("schedule_campaign", "Schedule a campaign after explicit user approval; timestamp must be ISO 8601.", {"campaign_id": "string", "schedule_time": "string"}),
    ("send_campaign", "Send a campaign immediately after explicit user approval.", {"campaign_id": "string"}),
    ("campaign_report", "Get delivery and engagement report for a sent campaign.", {"campaign_id": "string"}),
]


def schema(fields):
    props, required = {}, []
    for name, kind in fields.items():
        optional = kind.endswith("?")
        kind = kind.rstrip("?")
        props[name] = {"type": {"string": "string", "integer": "integer", "object": "object", "array": "array"}[kind]}
        if not optional:
            required.append(name)
    out = {"type": "object", "properties": props, "additionalProperties": False}
    if required:
        out["required"] = required
    return out


def request(method, path, body=None, query=None):
    key = os.environ.get("MAILCHIMP_API_KEY", "")
    prefix = os.environ.get("MAILCHIMP_SERVER_PREFIX", "") or (key.rsplit("-", 1)[1] if "-" in key else "")
    if not key or not prefix:
        raise RuntimeError("Set MAILCHIMP_API_KEY (and MAILCHIMP_SERVER_PREFIX if the key has no suffix).")
    url = f"https://{prefix}.api.mailchimp.com/3.0{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(body).encode() if body is not None else None
    auth = base64.b64encode(("codex:" + key).encode()).decode()
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization": "Basic " + auth, "Content-Type": "application/json", "User-Agent": "ROCA-Mailchimp-Codex/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Mailchimp API {exc.code}: {detail[:2000]}") from exc


def member_hash(email):
    return hashlib.md5(email.strip().lower().encode()).hexdigest()


def call(name, a):
    if name == "connection_status": return request("GET", "/")
    if name == "list_audiences": return request("GET", "/lists", query={"count": 100, "fields": "lists.id,lists.name,lists.stats.member_count,lists.stats.unsubscribe_count,total_items"})
    if name == "get_member": return request("GET", f"/lists/{a['list_id']}/members/{member_hash(a['email'])}")
    if name == "upsert_member":
        allowed = {"subscribed", "transactional", "pending"}
        if a["status_if_new"] not in allowed: raise ValueError("status_if_new must be subscribed, transactional, or pending")
        body = {"email_address": a["email"], "status_if_new": a["status_if_new"]}
        if a.get("merge_fields"): body["merge_fields"] = a["merge_fields"]
        return request("PUT", f"/lists/{a['list_id']}/members/{member_hash(a['email'])}", body)
    if name == "set_member_tags": return request("POST", f"/lists/{a['list_id']}/members/{member_hash(a['email'])}/tags", {"tags": a["tags"]})
    if name == "list_campaigns":
        q = {"count": a.get("count", 20), "sort_field": "create_time", "sort_dir": "DESC"}
        if a.get("status"): q["status"] = a["status"]
        return request("GET", "/campaigns", query=q)
    if name == "get_campaign": return request("GET", f"/campaigns/{a['campaign_id']}")
    if name == "create_campaign":
        recipients = {"list_id": a["list_id"]}
        if a.get("segment_id") is not None: recipients["segment_opts"] = {"saved_segment_id": a["segment_id"]}
        settings = {k: a[k] for k in ("subject_line", "from_name", "reply_to")}
        for k in ("preview_text", "title"):
            if a.get(k): settings[k] = a[k]
        return request("POST", "/campaigns", {"type": "regular", "recipients": recipients, "settings": settings})
    if name == "set_campaign_content": return request("PUT", f"/campaigns/{a['campaign_id']}/content", {"html": a["html"]})
    if name == "send_test": return request("POST", f"/campaigns/{a['campaign_id']}/actions/test", {"test_emails": a["test_emails"], "send_type": "html"})
    if name == "schedule_campaign": return request("POST", f"/campaigns/{a['campaign_id']}/actions/schedule", {"schedule_time": a["schedule_time"]})
    if name == "send_campaign": return request("POST", f"/campaigns/{a['campaign_id']}/actions/send")
    if name == "campaign_report": return request("GET", f"/reports/{a['campaign_id']}")
    raise ValueError("Unknown tool")


def respond(msg):
    sys.stdout.write(json.dumps(msg, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
            method, rid = req.get("method"), req.get("id")
            if method == "initialize":
                result = {"protocolVersion": req.get("params", {}).get("protocolVersion", "2025-03-26"), "capabilities": {"tools": {}}, "serverInfo": {"name": "mailchimp-roca", "version": "0.1.0"}}
            elif method == "tools/list":
                result = {"tools": [{"name": n, "description": d, "inputSchema": schema(s)} for n, d, s in TOOLS]}
            elif method == "tools/call":
                p = req.get("params", {})
                result = {"content": [{"type": "text", "text": json.dumps(call(p["name"], p.get("arguments", {})), ensure_ascii=False)}]}
            elif method in ("notifications/initialized", "ping"):
                if rid is None: continue
                result = {}
            else:
                if rid is None: continue
                raise ValueError(f"Unsupported method: {method}")
            if rid is not None: respond({"jsonrpc": "2.0", "id": rid, "result": result})
        except Exception as exc:
            rid = locals().get("req", {}).get("id") if isinstance(locals().get("req"), dict) else None
            if rid is not None: respond({"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": str(exc)}})


if __name__ == "__main__":
    main()
