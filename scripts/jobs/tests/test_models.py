import unittest

from scripts.jobs.models import (
    IllegalTransition,
    Job,
    Status,
    can_transition,
    transition,
)


class JobModelTests(unittest.TestCase):
    def test_prepare_fills_norms_and_dedup(self):
        job = Job(
            source="test",
            url="https://example.com/job/1?utm_source=x",
            company="Acme GmbH",
            title="Software Engineer (m/f/d)",
            location="Milan, Italy",
        ).prepare()
        self.assertEqual(job.canonical_url, "https://example.com/job/1")
        self.assertEqual(job.company_norm, "acme")
        self.assertEqual(job.title_norm, "software engineer")
        self.assertEqual(job.location_norm, "milan italy")
        self.assertEqual(len(job.dedup_key), 64)
        self.assertTrue(job.first_seen)
        self.assertTrue(job.last_seen)


class StatusMachineTests(unittest.TestCase):
    def test_legal_transition(self):
        self.assertTrue(can_transition("discovered", "scored"))
        self.assertTrue(can_transition("scored", "shortlisted"))

    def test_illegal_transition(self):
        self.assertFalse(can_transition("discovered", "submitted"))
        job = Job(status="discovered")
        with self.assertRaises(IllegalTransition):
            transition(job, "submitted", approval_token="token")

    def test_submitted_requires_token(self):
        self.assertFalse(can_transition("awaiting_approval", "submitted"))
        self.assertTrue(
            can_transition("awaiting_approval", "submitted", approval_token="token")
        )

    def test_shortlisted_to_prepared(self):
        job = Job(status="shortlisted")
        transition(job, "prepared")
        self.assertEqual(job.status, Status.PREPARED.value)


if __name__ == "__main__":
    unittest.main()
