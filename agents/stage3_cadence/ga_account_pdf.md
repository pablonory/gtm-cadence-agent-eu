# GA — Account PDF (Stage 3, Output B — the deliverable)

## Role
Assemble the **per-account artifact** the rep actually receives: a one-account PDF dropped into the
rep's Google Drive folder. This is the hand-off — the rep reads it, then assembles + activates the
cadence in Gong themselves. Nothing sends automatically.

## Reads
| Source | For |
|---|---|
| Stage 1 output (score, why-now, signals + sources) | the snapshot + signal intel |
| `ga_first_touch_email` output | the CUSTOM first touch + rationale |
| the matching `cadences/<vertical>_<persona>.md` | which Gong template to use |
| HubSpot record | account snapshot (locations, contacts) |

## PDF contents (in order)
1. **Snapshot** — company, vertical, persona, locations/segment, score.
2. **Why now** — the one-liner + each signal with evidence + source link (so the rep trusts it).
3. **The angle** — pain × JTBD in one line.
4. **Your first touch** — the bespoke Email 1 (subject + body) + a 1-line rationale (which signal +
   benefit + proof it used).
5. **The cadence to use** — name of the Gong territory-flow template for this cell + the flow summary.
6. **Provenance** — evidence-backed vs positioning-only; date.

## Output path
Google Drive: `US Cadence Agent/<rep-email>/<YYYY-MM-DD>_<Company>.pdf`. Local staging in `output/accounts/`
before upload (gitignored).

## Tools
- `build_pdf.py` (or render + **Google Drive MCP** `create_file`). Rep-folder isolation: a rep sees
  only their own folder.

## Writes back to the sheet (via the pipeline)
`Status: PDF ready`, `Score`, `Why-now`, `PDF link`, `Last run`.

## Rules
- Never include another rep's accounts in a rep's PDF/folder.
- Every signal in the PDF carries its source link — no unsourced "why now".
- If first touch is positioning-only (thin signals / no Gong evidence), say so in the PDF.

## Applied feedback
<!-- durable learned rules -->
