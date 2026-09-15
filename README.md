# ROCA Mailchimp Plugin

A Mailchimp integration for ChatGPT and Codex, developed for ROCA Ind. Machinery.

The plugin provides reusable workflows and tools for managing Mailchimp audiences, contacts, tags, campaigns, scheduling, and performance reports.

## Capabilities

* List Mailchimp audiences
* Find and inspect audience members
* Add or update contacts
* Manage contact tags
* List and inspect campaigns
* Create campaign drafts
* Add HTML campaign content
* Send test messages
* Schedule approved campaigns
* Send approved campaigns
* Retrieve delivery and engagement reports

## Safety rules

* API keys and credentials are never stored in this repository.
* Existing unsubscribed, cleaned, or pending contacts are not automatically changed to subscribed.
* Campaigns are created as drafts before scheduling or sending.
* Sending and scheduling require explicit user approval.
* Mailchimp status is verified after every modification.

## Repository structure

```text
.codex-plugin/
└── plugin.json

scripts/
└── mailchimp_mcp.py

skills/
└── roca-mailchimp/
    └── SKILL.md

.mcp.json
```

## Remote deployment for ChatGPT

The included `render.yaml` deploys a Streamable HTTP MCP endpoint on Render.
Configure `MAILCHIMP_API_KEY` as a secret in Render. Render generates
`ROCA_MCP_ACCESS_TOKEN`; use the private connector endpoint in this form:

```text
https://YOUR-SERVICE.onrender.com/mcp?token=YOUR_GENERATED_TOKEN
```

In ChatGPT developer mode, create an app with **No Authentication**, because the
private endpoint URL already carries the generated access token. Treat that URL
as a secret. For public or multi-user distribution, replace this mechanism with OAuth.

## Local configuration

The plugin requires the following environment variable:

```text
MAILCHIMP_API_KEY
```

The Mailchimp server prefix can usually be derived from the API key. It may also be provided separately:

```text
MAILCHIMP_SERVER_PREFIX
```

Never commit API keys or other credentials to GitHub.

## Status

Development version `0.2.0`.

The plugin package includes both local stdio and remote Streamable HTTP MCP entry points.

## Developer

ROCA Ind. Machinery
Industrial automation, conveyors, palletizing systems, and custom machinery.
