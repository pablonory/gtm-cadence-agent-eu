# Reactivation deal analysis — how to write the "why it died / what to say now" fields

> Runbook for the agent step that follows `scripts/reactivation_bundle.py`. That script does the
> deterministic fetch: HubSpot deal history + confirmed Gong calls (title-matched, then confirmed by
> participant email domain — never trust title alone, see the script's docstring) + logged emails where
> they exist. **This step is the reasoning**: read the bundle, decide what actually happened, and write
> one specific recommendation for the re-engagement first touch. Same split as every other stage of this
> pipeline — Python fetches and scores, the agent reasons and writes prose.

## The one thing this is NOT for
This is **not** a general "how to sell to this account" brief — Stage 1/2/3 already do that. This tab
exists for one narrower question: **the deal has died once before — what does the first re-engagement
email need to do differently so it doesn't just repeat what already failed?** Everything you write should
serve that question. If a finding doesn't change what the first touch should say, it doesn't belong here.

## 0. Read first
- `scripts/reactivation_bundle.py`'s docstring — the exact shape of `output/reactivation/<domain>.json`
- `context/outbound_voice.md` — the first-touch skeleton (problem-they'll-nod-at → we-solve-it → binary CTA)
- `context/anti_ai_writing_style.md` — the anti-AI gate, still applies to anything you draft here

## 1. Run the bundle
```bash
python3 scripts/reactivation_bundle.py <domain> --company "<name>"
```
Read the printed summary (`deals`, `contacts`, `logged_emails`, `gong_calls_confirmed`, `warnings`) before
opening the JSON — the warnings tell you plainly what's missing (no company match, no deals, no confirmed
calls, no logged emails). **Every warning is real signal, not noise** — report the gap in the relevant
field rather than skip it silently.

## 2. Set `reactivation_evidence_basis` first — before writing anything else
This gates how confident the rest of your writing is allowed to sound:
- `none` — no dead deal found at all. Say so in `reactivation_deal_history` and leave the other three
  fields empty or explicitly "not applicable — no prior deal to reactivate." **Do not invent a reason.**
- `deal_only` — a deal exists but zero Gong calls confirmed. Your `reactivation_call_analysis` must say
  plainly "no confirmed call history" — not silence, an explicit statement (silence reads as "not
  checked", which is worse than "checked, found nothing").
- `deal_calls` / `deal_calls_emails` / `calls_only` — set accordingly.

## 2b. A "wrong contact" disqualification needs a verified check, not a title shortcut
If a deal's closed-lost reason is some version of "contact isn't in the restaurant business" (real-estate
agent, unrelated profession, etc.), don't launder that into your write-up as fact unless the reason *itself*
says the connection was actually checked and came back empty (e.g. "no info on restaurants" / "no
hospitality activity found"). **A day job outside hospitality does not by itself mean no hospitality
tie** — real-estate operators in particular often hold restaurant brands as investments (Food Franchise
Group's contact was a real-estate development COO who legitimately ran two franchise restaurant units —
see batch 2 run notes). If the original disqualification reason doesn't show its work, say that plainly
("assumed a mismatch, not independently verified") rather than repeating the profession-based assumption
as if it were confirmed.

## 3. `reactivation_deal_history` — the facts, not your interpretation
For each dead deal in the bundle: name, stage, amount, close date, owner, and the closed-lost reason
**verbatim from whichever `hubspot.deals[].*` property actually held text** (property names vary by
pipeline — the bundle already gathered every property whose name matched `reason|lost|disqualif`; quote
the one that's populated). If none of them are populated, say **"no closed-lost reason recorded in
HubSpot"** — do not paraphrase a reason from the Gong calls into this field; that belongs in the call
analysis below, kept separate so a rep can tell "what HubSpot says" from "what we inferred from calls."

## 4. `reactivation_call_analysis` — read the transcripts, don't skim the tracker counts
The bundle includes Gong's own tracker hits (Pricing, Objections, Budget, Competition, Champion, etc.) —
useful as a pointer to *which* calls matter, never as a substitute for reading them. A call with zero
tracker hits and a 12,000-character transcript can still hold the real reason it died; a voicemail-only
"call" (check `duration_sec` and whether the transcript reads like an automated greeting — Gong logs
unanswered dial attempts as calls too) holds nothing and should be noted as noise, not analysed as if it
were a conversation.

For each call worth analysing, extract only what's **actually said**, attributed to the right speaker
(`REP (Name):` vs `PROSPECT (Name):` — the bundle labels this):
- The specific objection or hesitation, in the prospect's own words where you can quote it
- Who the champion/blocker was, by name and title
- Any concrete "next step" that was promised and whether it happened (a call that ends "I'll get back to
  you" and is never followed by another call is itself a finding)
- Competitor or incumbent-tool mentions
- Anything that reads as a **timing** problem (budget cycle, a renewal elsewhere, a hiring freeze) versus
  a **fit** problem (wrong persona on the call, price objection, feature gap) — these need opposite
  re-engagement strategies (timing → "has that passed now?"; fit → "here's what's different")

**If multiple calls exist, read them in order** — a deal that goes quiet after call 3 tells a different
story than one where the prospect explicitly says no on call 1. Note the gap between the last call and
today; a deal cold for 18 months needs a different opener than one cold for 6 weeks.

## 5. `reactivation_email_analysis` — usually thin, say so
Most outbound in this org runs through a sequence tool that doesn't log to HubSpot, so an empty result is
the **expected** case, not a failure. When logged emails do exist, note subject lines, whether they were
opened/replied to, and whether the *content* of a past email reveals what angle was already tried (so the
new one doesn't repeat it).

## 6. `reactivation_recommendation` — the field that matters
One tight paragraph, not a list of options. It must do three things, in this order:
1. **Name what changed since the deal died** — a new signal if one exists (check the account's own
   `signals_json`/`why_now` on this same brief), a conjunctural fact (`knowledge/conjunctural/`) if
   nothing account-specific fired, or — if genuinely nothing has changed — say that plainly rather than
   invent urgency. A reactivation opener with no real "why now" should say so and lean on the *relationship*
   ("last time we spoke about X — following up now that...") rather than fabricate a new trigger.
2. **Say what NOT to repeat** — the specific angle, proof point, or framing that was already tried and
   didn't land, sourced from step 4. Repeating a failed pitch verbatim is the single most avoidable mistake
   this tab exists to prevent.
3. **Give the precise opener** — not "focus on ROI" but the actual sentence-level angle, grounded in what
   was found. If the evidence is too thin to support a specific angle (evidence_basis = `none` or
   `deal_only` with an empty reason), say exactly that instead of manufacturing a recommendation: *"Not
   enough evidence to recommend a specific angle — the deal record has no reason and no calls were
   confirmed. Treat this as a genuine cold re-approach, not an informed reactivation."*

Anti-AI gate applies if you draft any actual copy here (not just advice) — run it before finishing.

## 6b. Write `reactivation_json` — this is what the card actually renders
**Short, structured fields. Not prose.** The first version of this feature stored long paragraphs and the
card rendered each as one `<Text>` block; reps got unreadable walls of text and said so (2026-08-13). The
card now renders structured components, so the analysis must arrive structured:

```json
{
  "verdict": "reactivate | do_not_reactivate | insufficient_evidence",
  "verdict_reason": "ONE sentence, the answer to 'do I work this?'",
  "lead_with": {"name": "...", "title": "...", "why": "one short clause"},
  "hook":  "one sentence — the dated thing that changed",
  "ask":   "one sentence — the specific low-friction next step",
  "do_not_repeat": ["short imperative", "short imperative"],
  "why_it_died": {"headline": "2–4 words, e.g. 'Decision access, not price'", "detail": "≤2 sentences"},
  "cycles": [{"label":"Cycle 1","dates":"Jun–Jul 2025","amount":"$9,000",
              "picklist":"Timing","reason":"≤1 sentence"}],
  "evidence": {"calls":6,"substantive_calls":1,"emails":43,"last_contact":"2026-06-23",
               "current_tools":["Sling (workforce mgmt)","Manual Excel inventory"]},
  "flags": ["only things a rep must know BEFORE sending"]
}
```

The detail sections (rendered inside the collapsed accordions) are **also bullets, not paragraphs** —
rep feedback 2026-08-13 was that prose in the accordions was still unreadable:

```json
{
  "call_detail": {
    "summary": "one line that frames it, e.g. '6 calls found — but only one was a real conversation.'",
    "points": ["one fact per bullet, ≤2 lines each"],
    "quote": {"text":"the prospect's actual words","who":"Name, Title","when":"which call"}
  },
  "deal_detail": {"summary":"...","points":["..."]},
  "email_detail": {
    "summary":"...",
    "timeline":[{"period":"Jun–Jul 2025","count":34,"note":"cycle 1"}],
    "points":["..."]
  }
}
```
- **One fact per bullet.** If a bullet needs a semicolon or "and also", split it.
- `email_detail.timeline` renders as a small table — use it for the burst/gap pattern rather than
  describing the pattern in a sentence. A visible gap row (`count: 0`) is more legible than "then an
  8-month silence".
- `call_detail.quote` renders as a pull-quote. Use it for the single most revealing thing the prospect
  actually said — verbatim from the transcript, never paraphrased into quotation marks.

Length discipline, because the card has no room for essays:
- `verdict_reason`, `hook`, `ask` — **one sentence each**, no semicolon-chaining.
- `do_not_repeat` / `flags` — **max 3 items**, one line each, imperative voice.
- `why_it_died.headline` — a label, not a sentence. It renders as a tag.
- `cycles[].reason` — one sentence. The verbatim closed-lost text goes in the long field, not here.
- If a field would be empty or padding, **omit it** — the card hides absent fields cleanly.

The four long `reactivation_*` textareas are still written (they hold the full narrative and any verbatim
quotes, and render inside collapsed accordions for reps who want the depth) — but they are no longer the
primary display path, so don't try to make them readable-at-a-glance. Put the scannable version in
`reactivation_json` and the evidence trail in the textareas.

## 7. Write back
Set all seven properties via the same upsert path as the rest of the pipeline
(`hubspot-app/scripts/upsert_brief.py` accepts arbitrary properties — pass these alongside the usual
brief fields, or PATCH them directly if the brief already exists and only the reactivation fields are new).
Set `reactivation_analysis_date` to today. Set `reactivation_last_deal_url` to
`https://app.hubspot.com/contacts/<portal-id>/record/0-3/<deal-id>` for the most recent dead deal.

## Dedup / refresh
Re-run when a new deal on the account closes lost, or on request — this is not part of the regular
per-account scoring cadence. There is no automatic trigger yet; that is a fair v2 addition once the tab is
in use (e.g., a HubSpot workflow that flags the cadence_brief when an associated deal's stage changes to
a dead stage).
