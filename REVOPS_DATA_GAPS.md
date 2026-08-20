# RevOps data gaps — what's blocking the cadence agent from learning

**For:** Lewis (Head of Sales) + RevOps · **From:** Pablo · **Date:** 2026-07-17

The GTM Cadence Agent is built and grounded in real intel. But four pieces of data that would let it
**improve on actual outcomes** (instead of playbook assumptions) aren't being logged today. Each is a
small, one-time hygiene fix with a compounding payoff. Fix them and the agent has a real feedback loop
within ~2 quarters.

---

## The four gaps

### 1. No sequence performance data — Gong Engage is off
- **Impact:** we can't see reply / open / meeting-booked rates by step, so we can't tell which emails or
  cadences actually work. Cadence length/rhythm is currently a best-practice *hypothesis*.
- **Fix:** re-enable **Gong Engage** with sequence-level reporting, **or** pull a HubSpot sequence report.
- **Payoff:** know which touch converts and where sequences die → tune every cadence on evidence.

### 2. Compelling-event (CE) fields are blank — can't correlate signals to wins
- **Impact:** most closed-won deals have empty CE fields, so we can't confirm which buying signal
  (leadership hire, funding, new location, contract expiry) actually predicts a win. Signal weights are
  playbook guesses. (Notably: **funding has zero support in the deal data** despite being a "Tier-1" signal.)
- **Fix:** make **CE a required field on every closed-won**, populated at close (pick from a set list:
  contract expiry / new site / new leadership / funding / other).
- **Payoff:** real signal→win correlation → the agent scores accounts on what actually converts.

### 3. Contact-role fields unpopulated — can't see which persona converts
- **Impact:** we can see roles on individual deals but not rolled-up (first-touch vs economic buyer vs
  champion), so "which persona converts best in the US" is directional only.
- **Fix:** a **structured contact-role field** on deal contacts (Champion / Economic buyer / First touch).
- **Payoff:** confirm the buying committee (today's read: Ops opens → Finance validates → Owner decides)
  and target the right seat first.

### 4. No published US / coffee case-study numbers
- **Impact:** the proof library has quantified wins for UKI/EU but **US proof is logos-only**, and
  **coffee has no hard numbers at all** — reps improvise generic %.
- **Fix (marketing):** publish two US case studies first — **Ark Restaurants** (NYC, multi-concept) and
  **Grand Traverse Pie Co.** (clean XtraChef displacement); pull the **Black Sheep Coffee** numbers.
- **Payoff:** US outbound can quote a real US/coffee outcome instead of a UKI stat.

---

## Also: one definition to confirm
- **Segment bands** are now set (**SMB 2–9 · MM 10–29 · ENT 30+**). Please confirm this is the single
  definition RevOps/HubSpot will use, so scoring, routing, and cadence length all agree.

## The ask
Owners + a date for gaps 1–3 (RevOps) and gap 4 (marketing). None is large; together they turn the
agent's learning loop from "assumed" to "measured."
