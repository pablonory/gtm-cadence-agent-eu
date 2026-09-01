"""The delta layer — set differences and date arithmetic, pinned.

This is the code that decides whether an observation is a *signal* or just a *fact*, so the behaviour
worth pinning hardest is the negative case: an unchanged account must produce nothing. Before this
existed, output/state/ was never written, so every run re-reported the same static facts.

Uses a temp STATE_DIR so tests never touch real prospect snapshots.
"""
import datetime
import json
import os
import shutil
import tempfile
import unittest

import _paths  # noqa: F401
import state_snapshot

TODAY = datetime.date(2026, 8, 24)


def days_ago(n):
    return (TODAY - datetime.timedelta(days=n)).isoformat()


class StateTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig = state_snapshot.STATE_DIR
        state_snapshot.STATE_DIR = self.tmp

    def tearDown(self):
        state_snapshot.STATE_DIR = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def seed(self, domain, baseline):
        os.makedirs(self.tmp, exist_ok=True)
        with open(os.path.join(self.tmp, domain + ".json"), "w") as fh:
            json.dump(baseline, fh)

    def diff(self, domain, observation):
        return state_snapshot.compute(domain, observation, TODAY)


class TestFirstRun(StateTestCase):
    def test_does_not_flag_the_whole_history(self):
        """The rule that matters most on run 1: an account with 40 existing sites is not 40 signals."""
        obs = {"locations": {"count": 40, "sites": ["S%d" % i for i in range(40)]}}
        out = self.diff("new.com", obs)
        self.assertTrue(out["first_run"])
        self.assertFalse(out["signals"]["new_location"]["present"])
        self.assertEqual(out["signals"]["new_location"]["new_sites_count"], 0)

    def test_dated_recent_opening_still_fires(self):
        """Intrinsic dates work without a baseline — that is the point of the two-kinds split."""
        obs = {"locations": {"count": 3, "sites": [
            {"name": "Austin-Domain", "date": days_ago(20)},
            {"name": "Old-One", "date": days_ago(900)},
        ]}}
        sig = self.diff("new.com", obs)["signals"]["new_location"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["new_sites_count"], 1)
        self.assertEqual(sig["locations"], ["Austin-Domain"])
        self.assertEqual(sig["recency_days"], 20)

    def test_first_run_window_is_tighter_than_expiry(self):
        """180d on run 1 vs 365d thereafter — otherwise run 1 flags a year of history."""
        obs = {"locations": {"count": 1, "sites": [{"name": "X", "date": days_ago(300)}]}}
        self.assertFalse(self.diff("new.com", obs)["signals"]["new_location"]["present"])
        self.assertEqual(state_snapshot.FIRST_RUN_DAYS["new_location"], 180)
        self.assertEqual(state_snapshot.EXPIRY_DAYS["new_location"], 365)


class TestNewLocation(StateTestCase):
    def test_unchanged_account_is_not_a_signal(self):
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 9, "sites": ["A", "B"]}})
        sig = self.diff("a.com", {"locations": {"count": 9, "sites": ["A", "B"]}})["signals"]["new_location"]
        self.assertFalse(sig["present"])
        self.assertEqual(sig["new_sites_count"], 0)

    def test_new_site_is_a_signal(self):
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 2, "sites": ["A", "B"]}})
        sig = self.diff("a.com", {"locations": {"count": 3, "sites": ["A", "B", "C"]}})["signals"]["new_location"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["locations"], ["C"])
        self.assertEqual(sig["count_delta"], 1)

    def test_reformatted_site_name_is_not_an_opening(self):
        """Observers phrase names inconsistently between runs; a formatting change must not fire."""
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 1, "sites": ["Austin - Domain"]}})
        sig = self.diff("a.com", {"locations": {"count": 1, "sites": ["austin_domain"]}})["signals"]["new_location"]
        self.assertFalse(sig["present"])

    def test_closure_is_visible_as_negative_count_delta(self):
        """Contraction is not scored yet, but it must at least be observable rather than looking like
        an absence of signal (see _signal_stack.md 'Still open')."""
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 3, "sites": ["A", "B", "C"]}})
        sig = self.diff("a.com", {"locations": {"count": 2, "sites": ["A", "B"]}})["signals"]["new_location"]
        self.assertFalse(sig["present"])
        self.assertEqual(sig["count_delta"], -1)

    def test_dict_sites_compare_against_stored_names(self):
        """REGRESSION (found by smoke test, 2026-08-24): the subagent writes sites as
        {name,date,stage} dicts, the baseline stores bare names. Comparing a dict's repr against a
        stored name reported every known site as new on every run — the exact failure this layer
        exists to prevent. The unit tests missed it because they used bare strings; the real shape
        is the dict."""
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 2, "sites": ["Austin-Domain", "Houston-Heights"]}})
        obs = {"locations": {"count": 2, "sites": [
            {"name": "Austin-Domain", "date": days_ago(200), "stage": "opened"},
            {"name": "Houston-Heights", "date": days_ago(400), "stage": "opened"},
        ]}}
        sig = self.diff("a.com", obs)["signals"]["new_location"]
        self.assertFalse(sig["present"], "unchanged account must be silent even in dict form")
        self.assertEqual(sig["new_sites_count"], 0)

    def test_dict_site_new_is_reported_by_name(self):
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 1, "sites": ["Austin-Domain"]}})
        obs = {"locations": {"count": 2, "sites": [
            {"name": "Austin-Domain", "date": days_ago(300), "stage": "opened"},
            {"name": "Charlotte-South", "date": days_ago(3), "stage": "announced"},
        ]}}
        sig = self.diff("a.com", obs)["signals"]["new_location"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["locations"], ["Charlotte-South"], "emit the name, never a dict repr")

    def test_omitted_key_yields_no_signal_object(self):
        """'I did not look' must be distinguishable from 'I looked and found nothing'."""
        self.seed("a.com", {"last_run": days_ago(30), "locations": {"count": 2, "sites": ["A", "B"]}})
        self.assertNotIn("new_location", self.diff("a.com", {"execs": []})["signals"])


class TestLeadershipHire(StateTestCase):
    def test_new_exec_in_window_fires(self):
        self.seed("a.com", {"last_run": days_ago(30), "execs": [{"name": "Old Boss", "role": "CEO"}]})
        sig = self.diff("a.com", {"execs": [
            {"name": "Old Boss", "role": "CEO"},
            {"name": "New COO", "role": "COO", "start_date": days_ago(40)},
        ]})["signals"]["leadership_hire"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["person_name"], "New COO")
        self.assertEqual(sig["recency_days"], 40)

    def test_already_flagged_exec_never_refires(self):
        """flagged_run is what stops the same hire being a 'signal' every week forever."""
        self.seed("a.com", {"last_run": days_ago(7), "execs": [
            {"name": "New COO", "role": "COO", "start_date": days_ago(40), "flagged_run": days_ago(7)},
        ]})
        sig = self.diff("a.com", {"execs": [
            {"name": "New COO", "role": "COO", "start_date": days_ago(47)},
        ]})["signals"]["leadership_hire"]
        self.assertFalse(sig["present"])

    def test_hire_outside_180d_does_not_fire(self):
        self.seed("a.com", {"last_run": days_ago(30), "execs": []})
        sig = self.diff("a.com", {"execs": [
            {"name": "Stale", "role": "CFO", "start_date": days_ago(400)},
        ]})["signals"]["leadership_hire"]
        self.assertFalse(sig["present"])

    def test_announced_but_not_yet_started_fires(self):
        """REGRESSION (Portillo's, 2026-08-24): a CFO announced Aug 4 effective Sep 7 has a FUTURE
        start date, so dating from it gave age -14 and zeroed a strength-5 signal 8 days old. The
        announcement opens the buying window, and an exec who has not yet arrived has not yet chosen
        their tools — the sharpest window there is, not a data error."""
        self.seed("a.com", {"last_run": days_ago(30), "execs": []})
        future = (TODAY + datetime.timedelta(days=14)).isoformat()
        sig = self.diff("a.com", {"execs": [
            {"name": "Kevin Kalicak", "role": "CFO & Treasurer", "start_date": future},
        ]})["signals"]["leadership_hire"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["recency_days"], 0, "incoming exec scores as maximally fresh")
        self.assertEqual(sig["incoming"], ["Kevin Kalicak"])

    def test_announced_date_wins_over_start_date(self):
        """When both are known, measure from the announcement — that is when the market learned."""
        self.seed("a.com", {"last_run": days_ago(30), "execs": []})
        sig = self.diff("a.com", {"execs": [
            {"name": "X", "role": "COO", "announced_date": days_ago(20),
             "start_date": (TODAY + datetime.timedelta(days=14)).isoformat()},
        ]})["signals"]["leadership_hire"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["recency_days"], 20)
        self.assertIsNone(sig["incoming"], "announced_date present, so no need to clamp")

    def test_window_matches_the_scorer(self):
        """180d was set 2026-08-12. _delta_state.md still documented 90; the code must not."""
        self.assertEqual(state_snapshot.EXPIRY_DAYS["leadership_hire"], 180)

    def test_undated_exec_on_first_run_is_ignored_by_default(self):
        """The guard that must survive the newly_appointed fix.

        With no baseline every exec is unknown, so a blanket undated pass would fire on every
        long-tenured founder who has no start_date. Measured case: Stokes Adobe's Ops Director was
        confirmed in-seat but left no external trace at all, so her tenure could not be established —
        'confirmed seat, no date' must NOT be reported as 'new seat'.
        """
        sig = self.diff("a.com", {"execs": [
            {"name": "Kat Cannon", "role": "Director of Operations"},
            {"name": "Sarah Orr", "role": "Owner"},
        ]})["signals"]["leadership_hire"]
        self.assertTrue(sig["first_run"])
        self.assertFalse(sig["present"], "undated and unproven on a first run is not a hire")

    def test_undated_exec_fires_on_first_run_when_observer_proves_it_is_new(self):
        """REGRESSION (Backal Hospitality, batch 3/6, 2026-08-24): a real new seat was invisible FOREVER.

        The hunter proved a new SVP of Operations by diffing the company's own leadership page against a
        dated Wayback capture (absent 2024-11-19, present today) but no source published a start date.
        Run 1 dropped him for being undated; commit() then seeded him into the baseline UNFLAGGED, so
        from run 2 he was `was_known` and could never fire. `newly_appointed` is the observer asserting
        positive evidence of change, which is the one thing a date was standing in for.
        """
        sig = self.diff("a.com", {"execs": [
            {"name": "Arthur Backal", "role": "CEO"},
            {"name": "Sebastien Lefavre", "role": "SVP Operations & Development",
             "newly_appointed": True},
        ]})["signals"]["leadership_hire"]
        self.assertTrue(sig["first_run"])
        self.assertTrue(sig["present"])
        self.assertEqual(sig["person_name"], "Sebastien Lefavre")
        self.assertIsNone(sig["recency_days"], "no date was ever established; do not invent one")

    def test_observer_proven_hire_does_not_refire_after_commit(self):
        """The other half of the fix: firing once is right, firing every week is the bug it replaced."""
        obs = {"execs": [
            {"name": "Sebastien Lefavre", "role": "SVP Operations & Development",
             "newly_appointed": True},
        ]}
        first = self.diff("a.com", obs)["signals"]["leadership_hire"]
        self.assertTrue(first["present"])
        state_snapshot.commit("a.com", obs, TODAY, {"leadership_hire": first})
        again = self.diff("a.com", obs)["signals"]["leadership_hire"]
        self.assertFalse(again["first_run"])
        self.assertFalse(again["present"], "flagged_run must stop the re-fire")


class TestFunding(StateTestCase):
    def test_newer_round_fires(self):
        self.seed("a.com", {"last_run": days_ago(200),
                            "funding": {"round": "Seed", "date": days_ago(700), "flagged_run": days_ago(200)}})
        sig = self.diff("a.com", {"funding": {"round": "Series A", "date": days_ago(30), "amount": "$12m"}})["signals"]["funding"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["round"], "Series A")

    def test_same_round_already_flagged_does_not_refire(self):
        self.seed("a.com", {"last_run": days_ago(20),
                            "funding": {"round": "Series A", "date": days_ago(50), "flagged_run": days_ago(20)}})
        sig = self.diff("a.com", {"funding": {"round": "Series A", "date": days_ago(50)}})["signals"]["funding"]
        self.assertFalse(sig["present"])

    def test_undated_round_does_not_fire_when_we_already_knew_one(self):
        """The measured 0/80 was partly agents correctly rejecting undated and unsourced raises. An
        undated round must not override a dated baseline."""
        self.seed("a.com", {"last_run": days_ago(20), "funding": {"round": "Series A", "date": days_ago(50)}})
        sig = self.diff("a.com", {"funding": {"round": "Series B"}})["signals"]["funding"]
        self.assertFalse(sig["present"])

    def test_explicit_empty_means_looked_and_found_nothing(self):
        self.seed("a.com", {"last_run": days_ago(20), "funding": {}})
        sig = self.diff("a.com", {"funding": {}})["signals"]["funding"]
        self.assertFalse(sig["present"])
        self.assertIn("no funding event", sig["evidence"])

    def test_undated_round_on_first_run_is_ignored_by_default(self):
        """An undated 2019 round must not score just because there is no baseline to compare it to."""
        sig = self.diff("a.com", {"funding": {"round": "Seed", "amount": "$2m"}})["signals"]["funding"]
        self.assertTrue(sig["first_run"])
        self.assertFalse(sig["present"])

    def test_undated_round_fires_on_first_run_when_observer_proves_it_is_new(self):
        """Same first-run hole as leadership_hire, closed the same way — see diff_funding's comment.
        Not measured on batch 3/6 (all five funding runs were clean negatives), fixed because the
        defect is identical: without this, an undated round found on run 1 is seeded into the baseline
        unflagged and can never fire again."""
        sig = self.diff("a.com", {"funding": {
            "round": "growth facility", "amount": "$8m", "newly_disclosed": True}})["signals"]["funding"]
        self.assertTrue(sig["first_run"])
        self.assertTrue(sig["present"])
        self.assertIsNone(sig["recency_days"], "no date was established; do not invent one")


class TestOpenJobs(StateTestCase):
    def test_current_state_signal_fires_on_any_open_role(self):
        """open_jobs is not a delta gate: a role is open or it is not (see score_accounts.py WINDOWS)."""
        self.seed("a.com", {"last_run": days_ago(7),
                            "open_roles": [{"title": "Head of Ops", "location": "NYC", "posted": days_ago(30)}]})
        sig = self.diff("a.com", {"open_roles": [
            {"title": "Head of Ops", "location": "NYC", "posted": days_ago(37)},
        ]})["signals"]["open_jobs"]
        self.assertTrue(sig["present"])
        self.assertEqual(sig["new_since_last_run"], 0)

    def test_disappeared_role_is_reported(self):
        """A vanished posting may mean the hire happened — pairs with leadership_hire per _delta_state.md."""
        self.seed("a.com", {"last_run": days_ago(30),
                            "open_roles": [{"title": "Head of Ops", "location": "NYC"}]})
        sig = self.diff("a.com", {"open_roles": []})["signals"]["open_jobs"]
        self.assertFalse(sig["present"])
        self.assertEqual(sig["disappeared_since_last_run"], ["Head of Ops"])


class TestMultiSignal(StateTestCase):
    """The reason four subagents exist rather than one. A brief like Portillo's carries new_location +
    leadership_hire + open_jobs at once, and the score only reaches 100/high when they stack — with
    new_location alone the same account scores 86 and, more to the point, loses the CFO hook entirely.
    hot_account (3+ signals inside 30 days) is also structurally unreachable with a single signal."""

    def test_merged_signals_all_survive(self):
        obs = {
            "locations": {"count": 3, "sites": [{"name": "New-Site", "date": days_ago(65)}]},
            "execs": [{"name": "New CFO", "role": "CFO", "announced_date": days_ago(8)}],
            "open_roles": [{"title": "Lead Architect, Data", "location": "HQ", "posted": days_ago(44)}],
            "funding": {},
        }
        out = self.diff("a.com", obs)
        self.assertTrue(out["multi_signal"])
        self.assertEqual(out["present_signals"], ["leadership_hire", "new_location", "open_jobs"])
        self.assertFalse(out["signals"]["funding"]["present"])

    def test_single_signal_is_not_flagged_multi(self):
        out = self.diff("a.com", {"open_roles": [{"title": "Head of Ops", "location": "HQ"}]})
        self.assertFalse(out["multi_signal"])
        self.assertEqual(out["present_signals"], ["open_jobs"])


class TestCommit(StateTestCase):
    def test_commit_seeds_then_diffs_from_run_two(self):
        obs1 = {"locations": {"count": 2, "sites": ["A", "B"]}}
        out1 = state_snapshot.compute("a.com", obs1, TODAY)
        state_snapshot.commit("a.com", obs1, TODAY, out1["signals"])
        self.assertFalse(out1["signals"]["new_location"]["present"])

        obs2 = {"locations": {"count": 3, "sites": ["A", "B", "C"]}}
        out2 = state_snapshot.compute("a.com", obs2, TODAY)
        self.assertFalse(out2["first_run"])
        self.assertTrue(out2["signals"]["new_location"]["present"])
        self.assertEqual(out2["signals"]["new_location"]["locations"], ["C"])

    def test_omitted_key_does_not_erase_what_we_knew(self):
        """'I did not look at execs' must not wipe the exec baseline."""
        state_snapshot.commit("a.com", {"execs": [{"name": "X", "role": "COO"}],
                                        "locations": {"count": 1, "sites": ["A"]}}, TODAY, {})
        state_snapshot.commit("a.com", {"locations": {"count": 2, "sites": ["A", "B"]}}, TODAY, {})
        saved = state_snapshot.read_state("a.com")
        self.assertEqual(len(saved["execs"]), 1)
        self.assertEqual(saved["locations"]["count"], 2)

    def test_commit_stamps_flagged_run_so_the_signal_does_not_repeat(self):
        obs = {"execs": [{"name": "New COO", "role": "COO", "start_date": days_ago(40)}]}
        out = state_snapshot.compute("a.com", obs, TODAY)
        self.assertTrue(out["signals"]["leadership_hire"]["present"])
        state_snapshot.commit("a.com", obs, TODAY, out["signals"])

        again = state_snapshot.compute("a.com", obs, TODAY)
        self.assertFalse(again["signals"]["leadership_hire"]["present"])

    def test_domain_is_normalised_on_disk(self):
        state_snapshot.commit("WWW.Foo.com/", {"locations": {"count": 1, "sites": ["A"]}}, TODAY, {})
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "foo.com.json")))
        self.assertEqual(state_snapshot.read_state("foo.com")["domain"], "foo.com")


if __name__ == "__main__":
    unittest.main()
