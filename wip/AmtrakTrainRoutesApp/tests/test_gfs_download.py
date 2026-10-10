import os
import time
import shutil
import unittest
from pathlib import Path
from AmtrakTrainRoutesApp.GtfsParser import GtfsParser


class TestGtfsDownload(unittest.TestCase):
    def setUp(self):
        """Set up a clean sandbox directory structure for test separation."""
        self.test_dir = Path(__file__).resolve().parent / "test_sandbox"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.parser = GtfsParser(base_dir=self.test_dir)

    def tearDown(self):
        """Clean up the test sandbox directory after test execution."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_baseline_download_when_missing(self):
        """Ensure a download is triggered if the zip archive doesn't exist."""
        self.assertFalse(self.parser.zip_path.exists())

        # This will hit the network to verify connection and stream processing
        downloaded = self.parser.ensure_fresh_gtfs()

        self.assertTrue(downloaded)
        self.assertTrue(self.parser.zip_path.exists())
        self.assertGreater(self.parser.zip_path.stat().st_size, 0)

    def test_cache_skips_when_valid(self):
        """Ensure it skips network requests if the file is fresh."""
        # Create a mock zip file to simulate a fresh cache item
        self.parser.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.parser.zip_path, "wb") as f:
            f.write(b"mock_zip_content")

        downloaded = self.parser.ensure_fresh_gtfs()
        self.assertFalse(downloaded)

    def test_cache_expires_after_24_hours(self):
        """Ensure a fresh download happens if the file timestamp is older than 24 hours."""
        self.parser.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.parser.zip_path, "wb") as f:
            f.write(b"old_zip_content")

        # Backdate the file's modification time by 25 hours (90,000 seconds)
        past_time = time.time() - 90000
        os.utime(self.parser.zip_path, (past_time, past_time))

        downloaded = self.parser.ensure_fresh_gtfs()
        self.assertTrue(downloaded)


if __name__ == "__main__":
    unittest.main()
