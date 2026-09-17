"""Resolve a Gong flow for a rep — by LOOKUP in their registry, never by building a name.

UKI runs two flow layers (cadences/UKI_FLOWS.md): each rep's own flows plus a shared company layer.
So `cadence_template` is not derived from vertical × persona the way the US matrix allows; it is
looked up in cadences/registry/<rep>.json (confirmed) or registry/drafts/<rep>.json (proposed tags),
falling back to the company layer, else EMPTY with a note. Rewired 2026-09-17 (open question #11).

The tri-state `live` contract (UKI_FLOWS.md):
    live: true   -> the rep confirmed it       -> flow_status "confirmed"
    live: null   -> not asked / not answered   -> flow_status "suggested" (name is verbatim from
                                                  their own Gong, so a suggestion, not an invention)
    live: false  -> the rep said no            -> never eligible again

Eligibility rules, in order of what they protect against:
- US flows are NEVER eligible for a UKI account: company entries in the US folders are skipped
  (the Gong instance is shared, so they appear in every pull).
- Only motions `outbound` and `reactivation` are resolvable. event / inbound / unclassified flows
  are campaign or one-off material — a brief must not route an account into them.
- `shared_with_rep` entries are eligible only at live:true — suggesting another person's flow is
  exactly the mistake the registry exists to avoid. (Team leads' own flows appear as Shared, which
  is why confirmed-live shared entries are allowed at all.)
- Reactivation resolves by REASON (no_show · non_responsive · product_gaps · timing — the four
  company flows, or the rep's own reason-tagged flow). No classified reason -> EMPTY + note: the
  reactivation analysis must say why the deal died before a flow can be named.

Ranking among eligible candidates (highest wins, ties broken by newest `created`):
    confirmed live > suggested   ·   personal > shared > company   ·   tighter tag match > wildcard
The founder/csuite bridge (UKI_FLOWS.md taxonomy): Gong's company layer has one CEO persona, so a
`founder` account matches `csuite`-tagged flows at reduced specificity, and vice versa.

Requires only stdlib. Pure file reads — no HubSpot, no Gong (doctrine: judgment observes, CODE maps).
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY_DIR = os.path.join(HERE, "..", "cadences", "registry")

US_FOLDERS = {"us flows", "usa flows", "usa  flows"}  # the double-space variant exists in Gong
PERSONA_BRIDGE = {"founder": "csuite", "csuite": "founder"}
SUITE = {"csuite": "Full Suite", "founder": "Full Suite", "finance": "IM", "operations": "IM"}
RESOLVABLE_MOTIONS = {"outbound", "reactivation"}


def _slug(rep_email):
    return (rep_email or "").split("@")[0].lower()


def load_registry(rep_email, registry_dir=None):
    """The rep's registry: confirmed file if it exists, else the draft. Returns (data, confirmed)."""
    rd = registry_dir or DEFAULT_REGISTRY_DIR
    slug = _slug(rep_email)
    if not slug:
        return None, False
    confirmed_path = os.path.join(rd, f"{slug}.json")
    draft_path = os.path.join(rd, "drafts", f"{slug}.json")
    if os.path.isfile(confirmed_path):
        with open(confirmed_path) as f:
            return json.load(f), True
    if os.path.isfile(draft_path):
        with open(draft_path) as f:
            return json.load(f), False
    return None, False


def load_company(registry_dir=None):
    rd = registry_dir or DEFAULT_REGISTRY_DIR
    path = os.path.join(rd, "_company.json")
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return json.load(f).get("flows", [])


def _candidates(rep_email, registry_dir):
    """(entry, layer_rank) for everything potentially eligible, before motion/tag filters."""
    reg, confirmed = load_registry(rep_email, registry_dir)
    out = []
    if reg:
        for e in reg.get("personal", []) or []:
            out.append((e, 3))
        for e in reg.get("shared_with_rep", []) or []:
            if e.get("live") is True:  # shared flows only when the rep confirmed them as theirs/used
                out.append((e, 2))
    for e in load_company(registry_dir):
        if (e.get("folder") or "").strip().lower() in US_FOLDERS:
            continue  # the US matrix — never for a UKI account
        out.append((e, 1))
    return out, confirmed


def _tag_specificity(tags, vertical, persona):
    """None = tags exclude this account. Otherwise a specificity score (higher = tighter fit)."""
    verts, pers = tags.get("vertical") or [], tags.get("persona") or []
    if verts and vertical not in verts:
        return None
    if pers and persona not in pers:
        if PERSONA_BRIDGE.get(persona) in pers:
            return (2 if vertical in verts else 0) + 1  # bridge match, reduced credit
        return None
    return (2 if vertical in verts else 0) + (2 if persona in pers else 0)


def resolve_flow(rep_email, vertical, persona, motion="outbound",
                 reactivation_reason=None, registry_dir=None):
    """The one entry point. Returns:
    {"flow": str ("" = leave cadence_template EMPTY), "flow_status": "confirmed"|"suggested"|"",
     "suite": str, "layer": "personal"|"shared"|"company"|None, "note": str|None}
    """
    suite_default = SUITE.get(persona, "IM")
    if motion not in RESOLVABLE_MOTIONS:
        return {"flow": "", "flow_status": "", "suite": suite_default, "layer": None,
                "note": f"motion '{motion}' is not resolvable to a flow"}
    if motion == "reactivation" and not reactivation_reason:
        return {"flow": "", "flow_status": "", "suite": suite_default, "layer": None,
                "note": "reactivation reason not classified — the deal analysis must set it "
                        "(no_show | non_responsive | product_gaps | timing) before a flow is named"}

    cands, registry_confirmed = _candidates(rep_email, registry_dir)
    ranked = []
    for e, layer_rank in cands:
        tags = e.get("tags") or {}
        if e.get("live") is False:
            continue
        if tags.get("motion") not in RESOLVABLE_MOTIONS or tags.get("motion") != motion:
            continue
        if motion == "reactivation":
            reason = tags.get("reactivation_reason")
            if reason and reason != reactivation_reason:
                continue  # a no-show flow must never be proposed for a product-gaps deal
            spec = 2 if reason == reactivation_reason else 1
        else:
            spec = _tag_specificity(tags, vertical, persona)
            if spec is None:
                continue
        live_rank = 2 if e.get("live") is True else 1
        ranked.append(((live_rank, layer_rank, spec, e.get("created") or ""), e, layer_rank))

    if not ranked:
        return {"flow": "", "flow_status": "", "suite": suite_default, "layer": None,
                "note": f"no matching flow in {_slug(rep_email)}'s registry — cadence_template left empty"}

    ranked.sort(key=lambda x: x[0], reverse=True)
    _, best, layer_rank = ranked[0]
    status = "confirmed" if best.get("live") is True else "suggested"
    suite = (best.get("tags") or {}).get("suite") or suite_default
    note = None
    if status == "suggested":
        note = ("suggested from the rep's own Gong flows (registry "
                + ("confirmed but this flow unasked" if registry_confirmed else "still a draft")
                + ") — the rep should correct it if wrong")
    return {"flow": best["name"], "flow_status": status, "suite": suite,
            "layer": {3: "personal", 2: "shared", 1: "company"}[layer_rank], "note": note}


def find_entry(rep_email, flow_name, registry_dir=None):
    """The registry entry behind an exact flow name visible to this rep, or None. Used by
    map_contacts.py to learn whether a brief's cadence_template is a reactivation flow — the brief
    object has no motion property, and the name IS the registry key."""
    for e, layer_rank in _candidates(rep_email, registry_dir)[0]:
        if e.get("name") == flow_name:
            e = dict(e)
            e["_layer"] = {3: "personal", 2: "shared", 1: "company"}[layer_rank]
            return e
    return None


def registry_flow_names(rep_email, registry_dir=None):
    """Every flow name visible to this rep (their registry + non-US company layer) — the guard set
    for `cadence_template must exist verbatim` (upsert_brief.py)."""
    cands, _ = _candidates(rep_email, registry_dir)
    return {e["name"] for e, _ in cands}
