---
name: roca-mailchimp
description: Manage ROCA Ind. Machinery Mailchimp audiences, permission status, tags, segments, campaign drafts, scheduling, sending, deliverability, and reports. Use for Mailchimp contacts, newsletters, campaign performance, bounces, unsubscribes, or list health.
---

# ROCA Mailchimp

Use the `mailchimp` MCP tools for live Mailchimp data. Start with `connection_status` when authentication or account identity is uncertain.

## Operating rules

- Read live state before reporting counts, campaign status, or performance.
- Treat the email address as the contact key and avoid duplicates.
- Preserve existing opt-out state. Never change `unsubscribed`, `cleaned`, or `pending` to `subscribed` without documented consent supplied by the user.
- A prior inbound email, commercial relationship, or the user's instruction alone is not proof of marketing consent. When consent is absent, use `transactional` where appropriate or keep the record outside the subscribed audience.
- Use one recipient per direct sales email; do not infer Mailchimp eligibility from this sales rule.
- Create campaigns as drafts first. Show the audience/segment, subject, preview text, sender, and recipient estimate before scheduling or sending.
- Scheduling and sending are external mutations. Require the user's explicit approval for the exact campaign and time immediately before calling the corresponding tool.
- Do not send test or live email to an address not explicitly supplied or verified in the current task.
- After mutations, read back the affected member or campaign and report the resulting Mailchimp status.

## Typical workflow

For audience work, list audiences, locate the member by email, inspect current status and tags, then make the smallest authorized change.

For campaigns, identify the target audience and segment, create the draft, set content, verify the draft, then request approval for test, schedule, or send. Use reports to compare opens, clicks, bounces, unsubscribes, and successful deliveries; do not present opens as perfectly reliable because privacy features can inflate them.

Authentication requires `MAILCHIMP_API_KEY`; `MAILCHIMP_SERVER_PREFIX` is optional because the server prefix can be derived from a standard Mailchimp key.
