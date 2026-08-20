# Output — local staging only

**Real deliverables go to Google Drive**, not here:

```
Google Drive / US Cadence Agent/    ← CREATED 2026-07-17 (id 1f0d-62p2kSSXPis8Bb8owAV1Dg-zkUvt)
├── <rep-email>/                 ← one folder per rep (rep sees only their own) — created per rep from the sheet
│   ├── 2026-07-17_Blank-Street-Coffee.pdf
│   └── ...
└── _weekly/                     ← per-rep weekly digest (create when the digest ships)
```
Folder: https://drive.google.com/drive/folders/1f0d-62p2kSSXPis8Bb8owAV1Dg-zkUvt

This `output/` folder is local staging for a run in progress (drafts before upload). It is
**gitignored** — see `.gitignore`. The folder skeleton (`accounts/`, `weekly/`, `state/`) is kept so the
structure is visible; contents are not committed (may contain real prospect data).

`state/` holds the **Stage-1 delta/state snapshots** (`<domain>.json`) — the per-account detection memory
that makes signals detect *change*, not static facts. Schema + run cycle: `directives/signals/_delta_state.md`.
