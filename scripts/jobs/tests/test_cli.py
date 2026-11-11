import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from scripts.jobs import cli

REPO = Path(__file__).resolve().parents[3]


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.env = {
            **os.environ,
            "CAREER_JOBS_DB": str(root / "jobs.db"),
            "CAREER_JOBS_LOCK": str(root / "jobs.lock"),
            "CAREER_STOP_FILE": str(root / "STOP"),
            "CAREER_DISCOVERIES_DIR": str(root / "discoveries"),
            "CAREER_SECRETS_DIR": str(root / "secrets"),
        }
        self.root = root

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "scripts.jobs.cli", *args],
            cwd=str(REPO),
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_no_submit_or_apply_subcommand(self):
        parser = cli.build_parser()
        choices = set()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                choices.update(action.choices.keys())
        self.assertFalse(
            {"submit", "apply"} & choices,
            "submit/apply must stay out of the CLI wildcard allow rule",
        )

    def test_status_reports_paths_and_schema(self):
        result = self.run_cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertFalse(payload["disabled"])
        self.assertEqual(payload["total"], 0)

    def test_scan_refuses_when_stop_file_present(self):
        (self.root / "STOP").write_text("stop", encoding="utf-8")
        result = self.run_cli("scan")
        self.assertEqual(result.returncode, 3)
        self.assertIn("disabled", result.stderr)

    def test_scan_refuses_when_lock_held(self):
        (self.root / "jobs.lock").write_text(
            f"{os.getpid()} {time.time()}", encoding="utf-8"
        )
        result = self.run_cli("scan")
        self.assertEqual(result.returncode, 4)
        self.assertIn("another run", result.stderr)

    def test_scan_dry_run(self):
        result = self.run_cli("scan", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["sources_registered"], [])
        self.assertFalse((self.root / "jobs.lock").exists())

    def test_purge(self):
        result = self.run_cli("purge", "--days", "90")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["removed"], 0)


if __name__ == "__main__":
    unittest.main()
