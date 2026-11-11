import unittest
from datetime import date, timedelta

from scripts.jobs import filters
from scripts.jobs.models import Job


def job(**overrides):
    data = {
        "source": "test",
        "url": "https://example.com/1",
        "company": "Acme",
        "title": "Software Engineer",
        "location": "Milan",
        "remote_type": "onsite",
    }
    data.update(overrides)
    return Job(**data).prepare()


class HardFilterTests(unittest.TestCase):
    def test_location_filter_blocks_other_city(self):
        result = filters.apply_hard_filters(
            job(location="Warsaw"), filters.FilterConfig(locations=("milan",))
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "location")

    def test_remote_passes_location_filter(self):
        result = filters.apply_hard_filters(
            job(location="Warsaw", remote_type="remote"),
            filters.FilterConfig(locations=("milan",)),
        )
        self.assertTrue(result.allowed)

    def test_language_filter(self):
        result = filters.apply_hard_filters(
            job(language="de"), filters.FilterConfig(languages=("en", "it"))
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "language")

    def test_seniority_filter(self):
        result = filters.apply_hard_filters(
            job(title="Senior Software Engineer"), filters.FilterConfig()
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "seniority")

    def test_graduate_title_is_allowed(self):
        result = filters.apply_hard_filters(
            job(title="Junior Software Engineer"), filters.FilterConfig()
        )
        self.assertTrue(result.allowed)

    def test_stale_posting_filter(self):
        old = (date.today() - timedelta(days=100)).isoformat()
        result = filters.apply_hard_filters(
            job(posted_at=old), filters.FilterConfig(max_age_days=45)
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "stale")

    def test_blocklist(self):
        result = filters.apply_hard_filters(
            job(company="Acme GmbH"), filters.FilterConfig(blocklist=("acme",))
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "company_blocklist")

    def test_scam_filter(self):
        result = filters.apply_hard_filters(
            job(description="Pay a fee to start immediately"),
            filters.FilterConfig(),
        )
        self.assertFalse(result.allowed)
        self.assertTrue(result.reason.startswith("scam_phrase"))


if __name__ == "__main__":
    unittest.main()
