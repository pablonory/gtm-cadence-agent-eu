# Rep-facing UI prototypes

Interactive HTML prototypes for how a **US AE** consumes what this agent produces (score, why-now
signals, the bespoke first touch, and the Gong cadence hand-off). Self-contained — open any file in a
browser, no build step. Sample data is **fictional** (invented prospects), not real HubSpot data.

| File | What it shows |
|---|---|
| `cockpit_standalone.html` | North-star experience: a full-brand, standalone "Cadence Cockpit" — owner-scoped account queue │ per-account brief │ agent chat panel. The richest UI, but would mean owning a separate app + its auth/security surface. |
| `hubspot_card.html` | The brief rendered as a HubSpot **UI-extension card** on a company record, in HubSpot's own design system. Shows the fidelity trade vs the standalone. |
| `hubspot_cadence_object.html` | **The chosen direction.** The brief built around a dedicated **Cadence Brief custom object**: an owner-scoped "My cadence targets" list view, the agent card on the object record, and an annotated **Access & permissions** view. |

## Chosen build direction (HubSpot-embedded)

- **Surface:** a **Cadence Brief custom object** (not properties on Company), with a UI-extension card
  (`@hubspot/ui-extensions`) + serverless function. Queue = a saved list view filtered `owner = me`.
- **Agent → HubSpot:** a **Private App** token (scopes: `crm.objects.custom.read/write` + companies/
  contacts read) hitting the CRM API. The agent sets `hubspot_owner_id` per brief from the input
  sheet's Rep column. *Not* an MCP Auth App — the remote MCP server doesn't expose custom objects.
- **Access (US-reps-only, two layers, enforced server-side):**
  1. **Object gate** — permission set `US Cadence — AE`, assigned only to US AEs. Everyone else: no access.
  2. **Record scope** — team `US Sales — AE`, **Owned only**. Manager (Lewis) gets team-wide *read*.
- **Prerequisite:** custom objects + permission sets require **Enterprise**; teams require Pro+. Confirm portal tier.

> Auth ≠ access control: the agent's single service credential can write briefs for all reps; the
> per-rep + US-only isolation is enforced on the **human** users via the permission set + team.
