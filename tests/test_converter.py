"""Unit tests for webm-to-mp4-converter."""

import shutil
import tempfile
import unittest
from pathlib import Path

from convert import (
    ConversionLogger,
    check_ffmpeg,
    convert_file,
    discover_webm_files,
)


class TestWebMConverter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_ffmpeg_detected(self):
        """Verify FFmpeg detection function."""
        has_ffmpeg = shutil.which("ffmpeg") is not None
        self.assertEqual(check_ffmpeg(), has_ffmpeg)

    def test_discover_webm_files(self):
        """Test recursive discovery of webm files (case-insensitive) and ignore non-webm."""
        sub_dir = self.base_path / "subfolder" / "deep"
        sub_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy test files
        (self.base_path / "video1.webm").write_text("dummy")
        (self.base_path / "video2.WEBM").write_text("dummy")
        (self.base_path / "not_video.txt").write_text("dummy")
        (sub_dir / "nested_video.webm").write_text("dummy")

        discovered = discover_webm_files(self.base_path)
        discovered_names = [f.name.lower() for f in discovered]

        self.assertEqual(len(discovered), 3)
        self.assertIn("video1.webm", discovered_names)
        self.assertIn("video2.webm", discovered_names)
        self.assertIn("nested_video.webm", discovered_names)

    def test_conversion_logger(self):
        """Test logger outputs headers, entries, and summary."""
        log_file = self.base_path / "test_log.txt"
        logger = ConversionLogger(log_file)

        logger.write_header(
            input_dir=self.base_path,
            output_dir=self.base_path / "out",
            total_files=2,
            preset="fast",
            crf=23,
        )
        logger.log_entry("SUCCESS", Path("clip.webm"), "-> clip.mp4")
        logger.log_entry("SKIPPED", Path("old.webm"), "Already exists")
        logger.write_summary(total=2, converted=1, skipped=1, failed=0, elapsed_seconds=1.5)

        self.assertTrue(log_file.exists())
        content = log_file.read_text(encoding="utf-8")
        self.assertIn("WebM to MP4 Bulk Conversion Session", content)
        self.assertIn("[SUCCESS] clip.webm - -> clip.mp4", content)
        self.assertIn("[SKIPPED] old.webm - Already exists", content)
        self.assertIn("Session Finished", content)


if __name__ == "__main__":
    unittest.main()
