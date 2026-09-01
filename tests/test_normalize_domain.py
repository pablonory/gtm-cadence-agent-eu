"""normalize_domain — the upsert key. One table, covering a defect that touched four files.

Why this test earns its place: HubSpot stores 69 of 38,124 company domains with a `www.` prefix, and
three live cadence briefs were affected — two of them the only briefs with no company association at
all. Before this function existed, upsert_brief.py did no normalisation, map_contacts.py lowercased,
and jobs_probe.py / reactivation_bundle.py stripped scheme+www differently.
"""
import unittest

import _paths  # noqa: F401
from gtm_common import normalize_domain


class TestNormalizeDomain(unittest.TestCase):
    def test_table(self):
        cases = [
            # (input, expected, why)
            ("machapresso.com", "machapresso.com", "already canonical"),
            ("www.machapresso.com", "machapresso.com", "THE live bug: HubSpot stores the www form"),
            ("WWW.MachaPresso.COM", "machapresso.com", "case"),
            ("https://www.foo.co.uk/careers?x=1", "foo.co.uk", "scheme + www + path + query"),
            ("http://foo.com", "foo.com", "plain scheme"),
            ("foo.com/", "foo.com", "trailing slash"),
            ("foo.com/careers", "foo.com", "path"),
            ("foo.com?utm=1", "foo.com", "query with no path"),
            ("foo.com#frag", "foo.com", "fragment"),
            ("user@foo.com", "foo.com", "an email pasted into a domain column"),
            ("foo.com:8080", "foo.com", "port"),
            ("  foo.com  ", "foo.com", "surrounding whitespace"),
            ("foo.com.", "foo.com", "trailing dot (fully-qualified form)"),
            ("", "", "empty in, empty out — caller decides if that is fatal"),
            (None, "", "None must not raise"),
        ]
        for raw, expected, why in cases:
            with self.subTest(raw=raw, why=why):
                self.assertEqual(normalize_domain(raw), expected)

    def test_only_www_is_stripped(self):
        """Other subdomains must survive: jobs_probe.py resolves ATS boards by hostname, so losing
        `jobs.` would break board detection."""
        self.assertEqual(normalize_domain("jobs.lever.co"), "jobs.lever.co")
        self.assertEqual(normalize_domain("boards.greenhouse.io"), "boards.greenhouse.io")
        self.assertEqual(normalize_domain("shop.foo.com"), "shop.foo.com")
        self.assertEqual(normalize_domain("wwwfoo.com"), "wwwfoo.com", )

    def test_strips_exactly_one_www(self):
        """A double prefix is a typo worth keeping visible, not silently cleaning away."""
        self.assertEqual(normalize_domain("www.www.foo.com"), "www.foo.com")

    def test_idempotent(self):
        for raw in ("https://WWW.Foo.com/x?y=1", "user@www.bar.co.uk:443/"):
            once = normalize_domain(raw)
            self.assertEqual(normalize_domain(once), once)


if __name__ == "__main__":
    unittest.main()
