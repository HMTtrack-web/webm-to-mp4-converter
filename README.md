# WebM to MP4 Bulk Converter 🎬➡️🎥

A high-performance Python-based command-line tool that recursively batch-converts `.webm` video files to `.mp4` using FFmpeg. It preserves nested directory structures, skips already converted files, provides real-time progress bars with `tqdm`, and generates detailed conversion audit logs.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Powered-007808.svg)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **Bulk & Recursive Conversion**: Recursively scans input directories including deeply nested subfolders.
- **Preserves Folder Hierarchy**: Mirrors the original directory layout perfectly in the output folder.
- **Industry Standard Codecs**: Encodes with `libx264` (H.264) video and `aac` audio with `-movflags +faststart` for instant web streaming and maximum player compatibility.
- **Any Video Length/Duration**: Transcodes entire video streams dynamically with zero duration restrictions.
- **Smart Skip Mechanism**: Automatically skips files that have already been converted to avoid redundant processing.
- **Live Progress Bar**: Displays conversion progress, ETA, and current file via `tqdm`.
- **Conversion Audit Log**: Keeps a record of every successful, skipped, or failed file in `conversion_log.txt`.
- **Customizable Speed/Quality Presets**: Choose encoding presets from `ultrafast` to `veryslow` and adjust Constant Rate Factor (`--crf`).

---

## 📋 Prerequisites

### 1. Install FFmpeg

FFmpeg is a system binary requirement and must be installed and accessible in your system's `PATH`.

#### Windows
You can install FFmpeg using any of the following package managers:

- **Using Windows Package Manager (winget)**:
  ```powershell
  winget install Gyan.FFmpeg
  ```
- **Using Chocolatey**:
  ```powershell
  choco install ffmpeg
  ```
- **Using Scoop**:
  ```powershell
  scoop install ffmpeg
  ```
- **Manual Installation**:
  1. Download the latest build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/).
  2. Extract the archive (e.g., to `C:\ffmpeg`).
  3. Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your system's **Environment Variables** -> **Path**.

#### macOS
Install via [Homebrew](https://brew.sh/):
```bash
brew install ffmpeg
```
Or via MacPorts:
```bash
sudo port install ffmpeg
```

#### Linux
Install using your distribution's package manager:

- **Debian / Ubuntu / Linux Mint**:
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```
- **Fedora / RHEL / CentOS**:
  ```bash
  sudo dnf install ffmpeg
  ```
- **Arch Linux / Manjaro**:
  ```bash
  sudo pacman -S ffmpeg
  ```

#### Verify FFmpeg Installation
Verify that FFmpeg is accessible from your terminal:
```bash
ffmpeg -version
```

---

### 2. Install Python Dependencies

Clone this repository and install the required Python packages:

```bash
git clone https://github.com/HMTtrack-web/webm-to-mp4-converter.git
cd webm-to-mp4-converter
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Basic Usage

Convert all `.webm` files in a folder and output them to a designated directory:

```bash
python convert.py --input ./videos --output ./converted
```

*Note: If `--output` is omitted, converted files default to `./converted`.*

### Example with Preset & CRF Quality

Control the balance between encoding speed and file compression using `--preset` and `--crf`:

```bash
python convert.py --input ./videos --output ./converted --preset fast --crf 22
```

### Force Overwrite

To re-convert files even if the output `.mp4` already exists:

```bash
python convert.py --input ./videos --output ./converted --overwrite
```

### Custom Log Location

Specify a custom path for the conversion log file:

```bash
python convert.py --input ./videos --output ./converted --log ./my_logs/run1.log
```

---

## ⚙️ CLI Options & Flags

| Flag | Short | Default | Description |
| :--- | :---: | :---: | :--- |
| `--input` | `-i` | *Required* | Path to input directory containing `.webm` files (recursively searched) |
| `--output` | `-o` | `./converted` | Path to destination directory for `.mp4` outputs |
| `--preset` | `-p` | `medium` | FFmpeg x264 preset (`ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`) |
| `--crf` | | `23` | Constant Rate Factor (0–51). Lower values mean higher visual quality (18–28 is typical) |
| `--overwrite` | `-f` | `False` | Force re-conversion of files that already exist in the output directory |
| `--log` | | `conversion_log.txt` | Path to the text log file recording conversion results |
| `--help` | `-h` | | Show help message and exit |

---

## 📁 Directory Structure Preservation

The converter maintains your existing directory tree structure. Subdirectories are replicated in the output folder:

```text
videos/
├── intro.webm
├── tutorials/
│   ├── lesson1.webm
│   └── lesson2.webm
└── archived/2026/
    └── recording.webm

converted/
├── intro.mp4
├── tutorials/
│   ├── lesson1.mp4
│   └── lesson2.mp4
└── archived/2026/
    └── recording.mp4
```

---

## 📝 Conversion Log Format

Every execution appends to `conversion_log.txt` (or custom log path). Example:

```text
================================================================================
WebM to MP4 Bulk Conversion Session - 2026-11-07 10:15:00
Input Directory  : /path/to/videos
Output Directory : /path/to/converted
FFmpeg Preset    : medium
CRF (Quality)    : 23
Total WebM Files : 3
================================================================================
[2026-11-07 10:15:02] [SUCCESS] intro.webm -> intro.mp4
[2026-11-07 10:15:05] [SKIPPED] tutorials/lesson1.webm - Output .mp4 already exists
[2026-11-07 10:15:08] [SUCCESS] tutorials/lesson2.webm -> lesson2.mp4
--------------------------------------------------------------------------------
Session Finished : 2026-11-07 10:15:08
Elapsed Time     : 6.25 seconds
Total Processed  : 3
  - Converted    : 2
  - Skipped      : 1 (already existed)
  - Failed       : 0
================================================================================
```

---

## 🏎️ Encoding Presets Explained

The `--preset` option configures FFmpeg's `libx264` encoder:
- **`ultrafast` / `superfast`**: Fastest conversion rate, larger file size. Great for rapid previews or batch drafting.
- **`fast` / `medium` (default)**: Great balance of conversion speed, file size, and visual quality.
- **`slow` / `slower`**: Maximum compression and highest quality per bit, at the cost of slower encoding times.

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE).
