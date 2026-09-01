# Gong evidence — sequence & channel performance (shared)

> The honest state of "what converts" at the **sequence** level — answers Q4/Q5. Sources:
> sales-intelligence app (2026-07-17) + **SMB Outbound Bi-Weekly Sync, 3 Jun 2026** (Phil Green,
> SMB Team Lead + team).
>
> **No owner on refresh, deliberately (2026-08-24).** There is no sequence-analytics agent and there
> should not be one until the data exists — see the data gap below. `scripts/gong_pull.py` retrieves
> calls and transcripts, not sequence analytics.

## ⚠️ The data gap (read this first)
**No reply / open / meeting-booked rates are tracked centrally.** Gong Engage is **not enabled** (no
active flows) → no sequence-level analytics. Performance data is fragmented across individual rep
inboxes. **We cannot quote a reply or meeting rate — do not fabricate one.**

To get real numbers: (a) re-enable **Gong Engage** with sequence reporting, or (b) pull a **HubSpot**
sequence/email performance report via RevOps — plus **tag the source email on every booked meeting**.
The SMB team is already trying to build this manually (Phil asks reps to log the exact email that booked
each meeting), so with tagging it's ~1 quarter to real data. **Raise with Phil / Lewis / RevOps.**

## Documented US approach (unmeasured)
**US Outreach Templates** — a 3-touch, **value-first, podcast-led** sequence ("What's Cooking?"): the
door-opener is inviting the operator onto Nory's podcast; touches 1–2 carry no pitch; the "meeting" is
framed as a briefing call with the podcast producer. Subject lines:
- **Touch 1:** *"Join us on What's Cooking? (NYC recordings)"*
- **Touch 2:** *"Re: What's Cooking? – NYC recordings"* (reply-chain)
- **Touch 3:** *"Final check-in – NYC podcast"*

**No conversion data attached.** A distinct play from our vertical×persona cadences — keep it as an
alternative **angle** (esp. for C-suite / hard-to-reach), not the default flow.

## What the SMB team is actually doing (3 Jun sync)
- **Concise, mobile-first, one CTA** — three lines, fits a phone screen. → `context/outbound_voice.md`.
- **Consistency > blitz** — a bit each day beats one big blocked day; team target was 2,000 activities/week.
- **Multi-thread — ≥3 contacts per account.** Cited stat: booking rate jumps **8% → 39%** when ~4
  stakeholders are engaged. Strong justification for our multi-contact cadences.
- **Channel reality:** **email is the hardest channel now**; **phone** = get a fast yes/no (pattern
  interrupt, book & get off); **LinkedIn** (esp. MM/ENT, Sales Navigator, profile-view + DM); **WhatsApp**
  emerging post-demo; **events + Sendoso gifting + charity-donation** as tactical door-openers.
- **Log the source email** on every booked meeting (the data-building habit above).

## Implications for our cadences
- **Multi-channel, multi-touch is validated** — no channel runs alone (email × call × LinkedIn +
  voicemail), and "1–2 touches won't cut it" holds up against the multithread stat and the team's own
  stated principles. Our pre-Gong prior was **14–16 touches, up from an old 8** — useful now only as a
  sanity check that a Gong flow isn't under-touched. The Gong flows themselves are the structure (UKI set unconfirmed — `cadences/UKI_FLOWS.md`).
- Until real rate data exists, cadence **length/rhythm is a best-practice hypothesis, not evidence-tuned**
  — flag this on every Output A deliverable.
- **Decision (Pablo):** cadence channels stay **email · call · LinkedIn** (+ voicemail) for v1. WhatsApp
  and Sendoso gifting are in team use but **out of scope** here — reps can still use them ad hoc, they're
  just not part of the designed cadence.

## Still needed
- Reply / meeting / open rates **per step** (Gong Engage or HubSpot).
- Which subject lines / first lines actually book meetings (currently anecdotal, not measured).
- Whether the US podcast sequence outperforms a standard cadence (no data either way yet).
