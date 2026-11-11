import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.jobs import db
from scripts.jobs.models import Job


def make_job(url="https://example.com/job/1", **overrides):
    data = {
        "source": "test",
        "url": url,
        "company": "Acme GmbH",
        "title": "Software Engineer",
        "location": "Milan",
    }
    data.update(overrides)
    return Job(**data)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "jobs.db"
        self.conn = db.connect(self.path)
        db.migrate(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_schema_version(self):
        self.assertEqual(db.schema_version(self.conn), db.SCHEMA_VERSION)

    def test_insert_and_read(self):
        job_id, created = db.upsert_job(self.conn, make_job())
        self.assertTrue(created)
        stored = db.get_job(self.conn, job_id)
        self.assertEqual(stored.company, "Acme GmbH")
        self.assertEqual(stored.status, "discovered")

    def test_upsert_is_idempotent_by_url(self):
        first_id, created = db.upsert_job(self.conn, make_job())
        second_id, created_again = db.upsert_job(
            self.conn, make_job("https://example.com/job/1?utm_source=x")
        )
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first_id, second_id)
        self.assertEqual(len(db.list_jobs(self.conn)), 1)

    def test_upsert_dedupes_by_company_title_location(self):
        first_id, created = db.upsert_job(self.conn, make_job())
        second_id, created_again = db.upsert_job(
            self.conn, make_job("https://other.example.com/roles/123")
        )
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first_id, second_id)
        self.assertEqual(len(db.list_jobs(self.conn)), 1)

    def test_counts_and_status_update(self):
        job_id, _ = db.upsert_job(self.conn, make_job())
        db.set_status(self.conn, job_id, "scored")
        self.assertEqual(db.counts_by_status(self.conn), {"scored": 1})

    def test_purge_keeps_submitted(self):
        old = (datetime.now(timezone.utc) - timedelta(days=200)).isoformat()
        stale_id, _ = db.upsert_job(self.conn, make_job("https://example.com/job/1"))
        submitted_id, _ = db.upsert_job(
            self.conn, make_job("https://example.com/job/2", title="Other Role")
        )
        with self.conn:
            self.conn.execute("UPDATE jobs SET last_seen=? WHERE id=?", (old, stale_id))
            self.conn.execute(
                "UPDATE jobs SET last_seen=?, status='submitted' WHERE id=?",
                (old, submitted_id),
            )
        removed = db.purge_older_than(self.conn, 90)
        self.assertEqual(removed, 1)
        remaining = [job.id for job in db.list_jobs(self.conn)]
        self.assertEqual(remaining, [submitted_id])

    def test_scan_lifecycle(self):
        scan_id = db.record_scan_start(self.conn)
        db.record_scan_finish(self.conn, scan_id, counts={"fetched": 3, "new": 2})
        row = self.conn.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["fetched"], 3)


if __name__ == "__main__":
    unittest.main()
