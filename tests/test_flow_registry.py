"""lib/flow_registry.py — the build-to-lookup rewiring (open question #11, 2026-09-17).

Synthetic registry fixtures; the real registries change with every survey reply, so behaviour is
pinned here, not against live data. Python 3.9 stdlib unittest, like the rest of tests/.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

import _paths  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from flow_registry import find_entry, registry_flow_names, resolve_flow  # noqa: E402


def entry(name, layer="personal", live=None, vertical=(), persona=(), motion="outbound",
          reason=None, folder="Personal flows", created="2026-06-01", suite=None):
    return {"id": name, "name": name, "folder": folder, "layer": layer, "created": created,
            "confidence": "high", "live": live,
            "tags": {"vertical": list(vertical), "persona": list(persona), "motion": motion,
                     "suite": suite, **({"reactivation_reason": reason} if reason else {})}}


class FlowRegistryTest(unittest.TestCase):
    def setUp(self):
        self.rd = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.rd, "drafts"))
        json.dump({"flows": [
            entry("Resto Finance - Agentic AI", "company", None, ("fsr",), ("finance",), folder="Outbound"),
            entry("Coffee CEO - Agentic AI", "company", None, ("coffee_cafe",), ("csuite",), folder="Outbound"),
            entry("Reactivation - Timing", "company", None, motion="reactivation", reason="timing", folder="Outbound"),
            entry("Reactivation - No show", "company", None, motion="reactivation", reason="no_show", folder="Outbound"),
            entry("FSR × Finance (IM · Tier 1)", "company", None, ("fsr",), ("finance",), folder="US Flows"),
            entry("USA Reactivation", "company", None, motion="reactivation", folder="US Flows"),
        ]}, open(os.path.join(self.rd, "_company.json"), "w"))
        json.dump({"rep": "ana@nory.ai", "status": "CONFIRMED", "personal": [
            entry("Ana Finance Flow", live=True, vertical=("fsr",), persona=("finance",)),
            entry("Ana Old Finance", live=False, vertical=("fsr",), persona=("finance",)),
            entry("Ana Founder Flow", live=None, persona=("csuite",)),          # wildcard vertical
            entry("Ana Reactivation", live=True, motion="reactivation", reason="timing"),
            entry("Tech Expo 2026", live=True, motion="event"),
        ], "shared_with_rep": [
            entry("Lead Shared Ops", "shared", live=True, vertical=("fsr",), persona=("operations",)),
            entry("Someone Elses Ops", "shared", live=None, vertical=("fsr",), persona=("operations",)),
        ]}, open(os.path.join(self.rd, "ana.json"), "w"))
        json.dump({"rep": "ben@nory.ai", "status": "DRAFT", "personal": [
            entry("Ben Coffee Owners", live=None, vertical=("coffee_cafe",), persona=("founder",)),
        ], "shared_with_rep": []}, open(os.path.join(self.rd, "drafts", "ben.json"), "w"))

    def tearDown(self):
        shutil.rmtree(self.rd)

    def r(self, email, v, p, **kw):
        return resolve_flow(email, v, p, registry_dir=self.rd, **kw)

    def test_confirmed_personal_beats_company(self):
        r = self.r("ana@nory.ai", "fsr", "finance")
        self.assertEqual((r["flow"], r["flow_status"], r["layer"]),
                         ("Ana Finance Flow", "confirmed", "personal"))

    def test_rejected_flow_never_returns(self):
        names = [self.r("ana@nory.ai", "fsr", "finance")["flow"] for _ in range(3)]
        self.assertNotIn("Ana Old Finance", names)

    def test_us_folder_never_eligible(self):
        self.assertNotEqual(self.r("nobody@nory.ai", "fsr", "finance")["flow"],
                            "FSR × Finance (IM · Tier 1)")
        r = self.r("nobody@nory.ai", "fsr", "finance", motion="reactivation", reactivation_reason="timing")
        self.assertNotEqual(r["flow"], "USA Reactivation")

    def test_unknown_rep_falls_to_company_as_suggestion(self):
        r = self.r("nobody@nory.ai", "fsr", "finance")
        self.assertEqual((r["flow"], r["flow_status"], r["layer"]),
                         ("Resto Finance - Agentic AI", "suggested", "company"))

    def test_founder_bridges_to_csuite(self):
        r = self.r("ana@nory.ai", "fsr", "founder")
        self.assertEqual(r["flow"], "Ana Founder Flow")   # csuite-tagged, bridge match
        self.assertEqual(r["flow_status"], "suggested")   # live: null

    def test_event_flow_never_routes(self):
        names = registry_flow_names("ana@nory.ai", registry_dir=self.rd)
        self.assertIn("Tech Expo 2026", names)            # exists (guard set)…
        for v in ("fsr", "coffee_cafe"):
            for p in ("finance", "csuite", "founder", "operations"):
                self.assertNotEqual(self.r("ana@nory.ai", v, p)["flow"], "Tech Expo 2026")

    def test_shared_only_when_live(self):
        r = self.r("ana@nory.ai", "fsr", "operations")
        self.assertEqual((r["flow"], r["layer"]), ("Lead Shared Ops", "shared"))
        # the unconfirmed shared flow must never be the answer
        self.assertNotEqual(r["flow"], "Someone Elses Ops")

    def test_reactivation_matches_reason_and_prefers_own(self):
        r = self.r("ana@nory.ai", "fsr", "finance", motion="reactivation", reactivation_reason="timing")
        self.assertEqual((r["flow"], r["flow_status"]), ("Ana Reactivation", "confirmed"))
        r = self.r("ana@nory.ai", "fsr", "finance", motion="reactivation", reactivation_reason="no_show")
        self.assertEqual(r["flow"], "Reactivation - No show")  # her timing flow must not answer no_show

    def test_reactivation_without_reason_is_empty(self):
        r = self.r("ana@nory.ai", "fsr", "finance", motion="reactivation")
        self.assertEqual(r["flow"], "")
        self.assertIn("reason not classified", r["note"])

    def test_no_match_is_empty_with_note(self):
        r = self.r("ben@nory.ai", "qsr", "operations")  # ben's draft has nothing for qsr/ops…
        # …but the company layer has nothing for qsr/ops either in this fixture → empty
        self.assertEqual((r["flow"], r["flow_status"]), ("", ""))
        self.assertIn("registry", r["note"])

    def test_draft_registry_suggests(self):
        r = self.r("ben@nory.ai", "coffee_cafe", "founder")
        self.assertEqual((r["flow"], r["flow_status"]), ("Ben Coffee Owners", "suggested"))
        self.assertIn("draft", r["note"])

    def test_find_entry_and_guard_set(self):
        e = find_entry("ana@nory.ai", "Ana Reactivation", registry_dir=self.rd)
        self.assertEqual(e["tags"]["motion"], "reactivation")
        self.assertIsNone(find_entry("ana@nory.ai", "Invented Flow", registry_dir=self.rd))
        self.assertIn("Resto Finance - Agentic AI", registry_flow_names("ben@nory.ai", registry_dir=self.rd))

    def test_suite_from_entry_tag_overrides_persona(self):
        json.dump({"rep": "cat@nory.ai", "status": "CONFIRMED", "personal": [
            entry("Cat Ops IMplus", live=True, vertical=("fsr",), persona=("operations",), suite="Full Suite"),
        ], "shared_with_rep": []}, open(os.path.join(self.rd, "cat.json"), "w"))
        r = self.r("cat@nory.ai", "fsr", "operations")
        self.assertEqual(r["suite"], "Full Suite")


if __name__ == "__main__":
    unittest.main()
