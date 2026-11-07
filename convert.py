#!/usr/bin/env python3
"""
WebM to MP4 Bulk Converter
Converts WebM video files to MP4 using FFmpeg (libx264 + aac).
Preserves directory structure, skips existing files, logs results,
and shows progress via tqdm.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

try:
    from tqdm import tqdm
except ImportError:
    print(
        "Error: 'tqdm' library is not installed.\n"
        "Please install requirements using: pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


def check_ffmpeg() -> bool:
    """Check if ffmpeg executable is available in system PATH."""
    return shutil.which("ffmpeg") is not None


class ConversionLogger:
    """Handles logging of conversion operations to file and console."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create parent directory of log file if necessary."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def write_header(self, input_dir: Path, output_dir: Path, total_files: int, preset: str, crf: int) -> None:
        """Write session start header to log file."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        divider = "=" * 80
        header = (
            f"\n{divider}\n"
            f"WebM to MP4 Bulk Conversion Session - {now}\n"
            f"Input Directory  : {input_dir.resolve()}\n"
            f"Output Directory : {output_dir.resolve()}\n"
            f"FFmpeg Preset    : {preset}\n"
            f"CRF (Quality)    : {crf}\n"
            f"Total WebM Files : {total_files}\n"
            f"{divider}\n"
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(header)

    def log_entry(self, status: str, rel_path: Path, message: str = "") -> None:
        """Append a single conversion log entry."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f" - {message}" if message else ""
        entry = f"[{now}] [{status:<7}] {rel_path.as_posix()}{msg}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def write_summary(
        self,
        total: int,
        converted: int,
        skipped: int,
        failed: int,
        elapsed_seconds: float,
    ) -> None:
        """Write session completion summary to log file."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        divider = "-" * 80
        summary = (
            f"{divider}\n"
            f"Session Finished : {now}\n"
            f"Elapsed Time     : {elapsed_seconds:.2f} seconds\n"
            f"Total Processed  : {total}\n"
            f"  - Converted    : {converted}\n"
            f"  - Skipped      : {skipped} (already existed)\n"
            f"  - Failed       : {failed}\n"
            f"{'=' * 80}\n"
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(summary)


def discover_webm_files(input_dir: Path) -> List[Path]:
    """
    Recursively discover all WebM files in input directory (case-insensitive).
    Returns list of paths sorted alphabetically.
    """
    webm_files = []
    for path in input_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".webm":
            webm_files.append(path)
    return sorted(webm_files)


def convert_file(
    input_file: Path,
    output_file: Path,
    preset: str = "medium",
    crf: int = 23,
) -> Tuple[bool, str]:
    """
    Convert a single WebM file to MP4 using FFmpeg.
    - libx264 video codec
    - aac audio codec (192 kbps)
    - movflags +faststart for optimized web streaming
    - No fixed-length assumption (handles arbitrary video durations)
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output without asking (pre-flight checks handle skip logic)
        "-i",
        str(input_file),
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        str(crf),
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_file),
    ]

    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if process.returncode == 0:
            return True, ""
        else:
            # Clean up potentially corrupt/partial output file
            if output_file.exists():
                try:
                    output_file.unlink()
                except OSError:
                    pass
            # Extract last few meaningful error lines from stderr
            err_lines = [
                line.strip()
                for line in process.stderr.splitlines()
                if line.strip() and not line.startswith("frame=")
            ]
            error_summary = err_lines[-1] if err_lines else "Unknown FFmpeg error"
            return False, error_summary
    except Exception as exc:
        if output_file.exists():
            try:
                output_file.unlink()
            except OSError:
                pass
        return False, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk convert WebM video files to MP4 using FFmpeg while preserving folder structure.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Path to input directory containing .webm files (searches subfolders recursively)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="./converted",
        type=str,
        help="Path to output directory where converted .mp4 files will be saved",
    )
    parser.add_argument(
        "-p",
        "--preset",
        type=str,
        default="medium",
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
        help="FFmpeg x264 encoding preset to balance conversion speed vs compression efficiency",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=23,
        help="Constant Rate Factor for x264 quality (0-51, lower = higher quality, 23 is default)",
    )
    parser.add_argument(
        "-f",
        "--overwrite",
        action="store_true",
        help="Overwrite output file even if it already exists (by default, existing files are skipped)",
    )
    parser.add_argument(
        "--log",
        type=str,
        default="conversion_log.txt",
        help="Path to conversion log file",
    )

    args = parser.parse_args()

    # Pre-flight check: FFmpeg installation
    if not check_ffmpeg():
        print(
            "\n[ERROR] FFmpeg was not found in your system's PATH.\n\n"
            "FFmpeg is required to perform video conversions.\n"
            "Installation instructions:\n"
            "  - Windows: winget install Gyan.FFmpeg   (or choco install ffmpeg)\n"
            "  - macOS:   brew install ffmpeg\n"
            "  - Ubuntu:  sudo apt install ffmpeg\n"
            "Please install FFmpeg and make sure it is added to your PATH.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    log_file = Path(args.log).resolve()

    if not input_dir.exists():
        print(f"[ERROR] Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"[ERROR] Input path is not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Discover files
    print(f"\nScanning for WebM files in: {input_dir} ...")
    webm_files = discover_webm_files(input_dir)
    total_files = len(webm_files)

    if total_files == 0:
        print("[INFO] No .webm files found in the specified directory.")
        sys.exit(0)

    print(f"Found {total_files} WebM file(s) to process.")
    print(f"Output directory : {output_dir}")
    print(f"Encoding preset  : {args.preset}")
    print(f"CRF quality      : {args.crf}")
    print(f"Logging to       : {log_file}\n")

    logger = ConversionLogger(log_file)
    logger.write_header(input_dir, output_dir, total_files, args.preset, args.crf)

    converted_count = 0
    skipped_count = 0
    failed_count = 0
    start_time = time.time()

    try:
        with tqdm(
            webm_files,
            desc="Converting",
            unit="file",
            dynamic_ncols=True,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        ) as pbar:
            for webm_path in pbar:
                # Compute relative path to preserve directory structure
                rel_path = webm_path.relative_to(input_dir)
                out_path = output_dir / rel_path.with_suffix(".mp4")

                display_name = rel_path.name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                pbar.set_postfix_str(f"Processing: {display_name}")

                # Check if output already exists (skip check)
                if out_path.exists() and not args.overwrite:
                    skipped_count += 1
                    logger.log_entry("SKIPPED", rel_path, "Output .mp4 already exists")
                    continue

                # Perform conversion
                success, err_msg = convert_file(
                    input_file=webm_path,
                    output_file=out_path,
                    preset=args.preset,
                    crf=args.crf,
                )

                if success:
                    converted_count += 1
                    logger.log_entry("SUCCESS", rel_path, f"-> {out_path.name}")
                else:
                    failed_count += 1
                    logger.log_entry("FAILED", rel_path, f"Error: {err_msg}")

    except KeyboardInterrupt:
        print("\n\n[WARNING] Process interrupted by user. Finalizing logs...")
        logger.log_entry("ABORTED", Path("SESSION"), "Process interrupted by user (Ctrl+C)")

    elapsed = time.time() - start_time
    logger.write_summary(total_files, converted_count, skipped_count, failed_count, elapsed)

    # Print summary
    print("\n" + "=" * 50)
    print("           CONVERSION SUMMARY")
    print("=" * 50)
    print(f"Total files detected : {total_files}")
    print(f"Successfully converted: {converted_count}")
    print(f"Skipped (already converted): {skipped_count}")
    print(f"Failed conversions   : {failed_count}")
    print(f"Total time elapsed   : {elapsed:.2f} seconds")
    print(f"Detailed log saved to: {log_file}")
    print("=" * 50 + "\n")

    if failed_count > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
