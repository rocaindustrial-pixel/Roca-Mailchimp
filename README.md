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

## Configuration

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

Development version `0.1.0`.

The plugin package and Mailchimp MCP server are complete. Marketplace registration and local installation are required before use in ChatGPT or Codex.

## Developer

ROCA Ind. Machinery
Industrial automation, conveyors, palletizing systems, and custom machinery.
