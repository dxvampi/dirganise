# Dirganise

> Organize any folder in seconds by file type.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()

---

## Features

- **Automatic sorting** — moves files into categories: Images, Videos, Audio, Documents, Code, Compressed, Installers, Fonts, and Others
- **Custom rules** — define your own extension-to-folder mappings via a JSON file
- **Dry-run mode** — preview what would happen without touching the filesystem
- **Undo** — revert the last organization with a single command
- **Conflict handling** — appends a timestamp automatically if a file with the same name already exists

---

## Installation

```bash
pip install dirganise
```

Or clone and install locally:

```bash
git clone https://github.com/yourusername/dirganise.git
cd dirganise
pip install -e .
```

---

## Usage

```bash
# Organize a folder
dirganise /path/to/folder

# Preview changes without moving anything
dirganise . --dry-run

# Undo the last organization
dirganise . --undo

# Use custom rules from a JSON file
dirganise . --rules custom_rules.json
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--dry-run` | `-n` | Preview changes without modifying the filesystem |
| `--undo` | | Revert the last `dirganise` operation in this folder |
| `--rules FILE` | | Path to a JSON file with custom extension-to-folder rules |

---

## Default Organization Rules

| Category | Extensions |
|----------|------------|
| **Images** | `.jpg` `.jpeg` `.png` `.gif` `.webp` `.svg` `.bmp` `.tiff` `.heic` |
| **Videos** | `.mp4` `.mov` `.avi` `.mkv` `.wmv` `.flv` |
| **Audio** | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` |
| **Documents** | `.pdf` `.docx` `.xlsx` `.pptx` `.txt` `.odt` `.rtf` |
| **Code** | `.py` `.js` `.ts` `.html` `.css` `.json` `.csv` `.xml` `.sh` `.bat` `.ps1` |
| **Compressed** | `.zip` `.rar` `.7z` `.tar` `.gz` `.bz2` |
| **Installers** | `.exe` `.msi` `.dmg` `.pkg` `.deb` `.rpm` |
| **Fonts** | `.ttf` `.otf` `.woff` `.woff2` |
| **Others** | Everything else |

---

## Custom Rules

Create a `.json` file mapping extensions to folder names:

```json
{
  ".psd": "Design",
  ".ai": "Design",
  ".blend": "3D",
  ".csv": "Data"
}
```

Custom rules **override** the defaults for any matching extension. All other defaults remain active.

```bash
dirganise ~/Downloads --rules my_rules.json
```

---

## Undo

After every organization, `dirganise` saves a log file (`.dirganise_op.json`) in the target folder. Use it to restore the original state:

```bash
dirganise /path/to/folder --undo
```

> The log file is automatically deleted after a successful undo.

---

## Example

```
$ dirganise ~/Downloads --dry-run

 dirganise  >  /home/user/Downloads

Images/
  photo_2024.jpg
  screenshot.png

Documents/
  report.pdf
  notes.txt

Code/
  script.py

Total files to move: 5

[Preview] No changes have been made to the file system.
```

---

## Development

```bash
git clone https://github.com/yourusername/dirganise.git
cd dirganise
pip install -e .
```

Contributions, issues, and feature requests are highly welcome. Feel free to open a issue or submit a pull request.

---

## Compatibility

`dirganise` relies only on the Python standard library and has no external dependencies, so it runs on any platform that supports Python 3.10+.

| OS | Minimum version |
|----|-----------------|
| **Windows** | 8.1 |
| **macOS** | 10.9 (Mavericks) |
| **Linux** | Any modern distribution |
| **FreeBSD** | 12.0 |
| **OpenBSD** | 7.0 |
| **NetBSD** | 9.0 |
| **DragonFlyBSD** | 6.0 |
| **Solaris / illumos** | Solaris 11.4 / OpenIndiana 2021+ |
| **AIX** | 7.2 |
| **Android** | Via Termux (Python 3.10+) |
| **iOS / iPadOS** | Via Pythonista or similar (limited) |

> [!NOTE]
> It is not recommended for its use on Android or iOS for stability reasons.

---

## License

[MIT](LICENSE) © 2026
