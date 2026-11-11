import tempfile
import unittest
from pathlib import Path

from scripts.jobs import report
from scripts.jobs.models import Job


class ReportTests(unittest.TestCase):
    def test_redact_hides_email_phone_and_token(self):
        text = "contact hr@example.com or +39 333 1234567 token abcdefabcdefabcdefabcdefabcdef12"
        redacted = report.redact(text)
        self.assertNotIn("hr@example.com", redacted)
        self.assertIn("[email]", redacted)
        self.assertIn("[phone]", redacted)
        self.assertIn("[token]", redacted)

    def test_write_daily_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-01-01.md"
            job = Job(
                source="test",
                url="https://example.com/1",
                company="Acme",
                title="Engineer",
                location="Milan",
                score=8.0,
                score_reasons="matches Python",
            ).prepare()
            written = report.write_daily_report(
                jobs=[job],
                source_health=[],
                counts={"new": 1},
                path=path,
            )
            text = written.read_text(encoding="utf-8")
            self.assertIn("# Job discovery report", text)
            self.assertIn("Engineer at Acme", text)
            self.assertIn("matches Python", text)
            self.assertIn("No sources configured yet.", text)


if __name__ == "__main__":
    unittest.main()
