"""
Dirganise - Organizes a certain folder in a few seconds per file type (no AI slop was used in the making of this project btw)
"""
import argparse, json, shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError


@dataclass
class FailedFile:
    name: str
    reason: str

# -----------
# ---RULES---
# -----------

DEFAULT_RULES: dict[str, str] = {

                         # -- MEDIA -- #
                         # ----------- #
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".webp": "Images", ".svg": "Images",
    ".bmp": "Images", ".tiff": "Images", ".heic": "Images",

    # Videos
    ".mp4": "Videos", ".mov": "Videos", ".avi": "Videos",
    ".mkv": "Videos", ".wmv": "Videos", ".flv": "Videos",

    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    ".aac": "Audio", ".ogg": "Audio", ".m4a": "Audio",

                        # -- DOCUMENTS -- #
                        # --------------- #
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents",
    ".xlsx": "Documents", ".xls": "Documents", ".pptx": "Documents",
    ".txt": "Documents", ".odt": "Documents", ".rtf": "Documents",

                           # -- Code -- #
                           # ---------- #
    ".py": "Code", ".js": "Code", ".ts": "Code",
    ".html": "Code", ".css": "Code", ".json": "Code",
    ".csv": "Code", ".xml": "Code", ".sh": "Code",
    ".bat": "Code", ".ps1": "Code",
    
                           # -- Others -- #
                           # ------------ #
    # Compressed
    ".zip": "Compressed", ".rar": "Compressed", ".7z": "Compressed",
    ".tar": "Compressed", ".gz": "Compressed", ".bz2": "Compressed",

    # Executables
    ".exe": "Executables/Programs",
    ".msi": "Executables/Installers", ".dmg": "Executables/Installers",
    ".pkg": "Executables/Installers", ".deb": "Executables/Installers", ".rpm": "Executables/Installers",

    # Fonts
    ".ttf": "Fonts", ".otf": "Fonts", ".woff": "Fonts", ".woff2": "Fonts",

}

UNDO_FILE: str = ".dirganise_op.json"

# ------------------ #
# --- MAIN LOGIC --- #
# ------------------ #

def load_rules(custom_rules_path: Path) -> dict[str, str]:
    """Return custom rules if provided, otherwise return default rules. Custom rules will override default ones if they exist.

    Args:
        custom_rules_path (Path): Path to the custom rules (JSON file).

    Returns:
        dict[str, str]: The rules that are gonna be used.
    """
    rules = DEFAULT_RULES.copy()
    if custom_rules_path and custom_rules_path.exists():
        try:
            with open(custom_rules_path, "r", encoding="utf-8") as f:
                custom = json.load(f)
            rules.update(custom)
            print(f"Loaded custom rules successfully from {custom_rules_path}\n")
        except Exception as e:
            print(f"Error loading custom rules: {e} \nUsing default rules instead.\n")
    return rules

def collect_moves(folder: Path, rules: dict[str, str]) -> list[tuple[Path, Path]]:
    """Collects the moves that need to be made for each file in the folder.

    Args:
        folder (Path): The folder to organize.
        rules (dict[str, str]): The rules to use for organizing.

    Returns:
        list[tuple[Path, Path]]: A list of tuples containing the source and destination paths for each file to be moved.
    """
    moves = []
    for file in sorted(folder.iterdir()):
        if not file.is_file():
            continue
        if file.name.startswith("."):
            continue
        suffix = file.suffix.lower()
        subfolder_name = rules.get(suffix, "Others")
        destination_dir = folder / subfolder_name
        destination_file = destination_dir / file.name
        if destination_dir == folder:
            continue
        moves.append((file, destination_file))
    return moves

def print_preview(moves: list[tuple[Path, Path]]) -> None:
    """Prints a preview of the moves that will be made.

    Args:
        moves (list[tuple[Path, Path]]): A list of tuples containing the source and destination paths for each file to be moved.
    """

    if not moves:
        print("No files to organize. Make your own rules if you think the default ones are not right for your work.")
        return
    by_destination: dict[Path, list[Path]] = {}

    for source, destination in moves:
        by_destination.setdefault(destination.parent, []).append(source)

    for folder_name, files in sorted(by_destination.items()):
        print(f"\n{folder_name.name}/")
        for file in files:
            print(f"  {file.name}")
    print(f"\nTotal files to move: {len(moves)}\n")

def _print_failed_summary(failed: list[FailedFile]) -> None:
    """Prints a grouped summary of files that could not be moved.

    Args:
        failed (list[FailedFile]): Files that failed along with their reasons.
    """
    # Group by reason
    by_reason: dict[str, list[str]] = {}
    for entry in failed:
        by_reason.setdefault(entry.reason, []).append(entry.name)

    total = len(failed)
    print(f"\n{total} file{'s' if total != 1 else ''} failed:\n")
    for reason, names in by_reason.items():
        for name in names:
            print(f"  * {name} -> {reason}")

def organize(moves: list[tuple[Path, Path]], dry_run: bool = False, folder: Path = Path(".")) -> None:
    """Applies the moves to the file system.

    Args:
        moves (list[tuple[Path, Path]]): A list of tuples containing the source and destination paths for each file to be moved.
        dry_run (bool): If True, only previews the moves without applying them.
        folder (Path): The root folder being organized (used for the undo log).
    """

    if not moves:
        return

    if dry_run:
        print("[Preview] No changes have been made to the file system.\n")
        print_preview(moves)
        return

    undo_file = []
    moved_files = 0
    failed: list[FailedFile] = []

    for source, destination in moves:
        # --- Create destination directory ---
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"Skipped: {source.name} (no permission to create '{destination.parent.name}/')")
            failed.append(FailedFile(name=source.name, reason=f"No permission to create '{destination.parent.name}/'"))
            continue
        except OSError as e:
            print(f"Skipped: {source.name} (could not create destination folder: {e.strerror})")
            failed.append(FailedFile(name=source.name, reason=f"Could not create destination folder: {e.strerror or 'Unknown error'}"))
            continue

        # --- Resolve name conflict ---
        if destination.exists():
            stem = destination.stem
            suffix = destination.suffix
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            destination = destination.parent / f"{stem}_{timestamp}{suffix}"

        # --- Move the file ---
        try:
            shutil.move(str(source), str(destination))
        except PermissionError:
            print(f"Skipped: {source.name} (file is in use)")
            failed.append(FailedFile(name=source.name, reason="File is in use"))
            continue
        except shutil.Error as e:
            print(f"Skipped: {source.name} (move error: {e})")
            failed.append(FailedFile(name=source.name, reason=f"Move error: {e}"))
            continue
        except OSError as e:
            print(f"Skipped: {source.name} ({e.strerror})")
            failed.append(FailedFile(name=source.name, reason=e.strerror or "Unknown error"))
            continue

        undo_file.append({"from": str(destination), "to": str(source)})
        print(f"Moved: {source.name} to {destination.parent.name}/")
        moved_files += 1

    # --- Write undo log ---
    if undo_file:
        log_path = folder / UNDO_FILE
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump({"timestamp": datetime.now().isoformat(), "moves": undo_file}, f, indent=2, ensure_ascii=False)
            print(f"\n{moved_files} files organized successfully.")
            print(f"Log saved to {log_path}\nYou can use this log to undo the changes if needed.")
        except OSError as e:
            print(f"\n{moved_files} files organized successfully.")
            print(f"Warning: Could not save undo log ({e.strerror}). You will not be able to undo this operations.")

    if failed:
        _print_failed_summary(failed)

def undo_moves(folder: Path) -> None:
    """Undoes the last organization operations using the log file.

    Args:
        folder (Path): The folder to undo the organization in.
    """
    log_path = folder / UNDO_FILE
    if not log_path.exists():
        print("No undo log found. Cannot undo.")
        return

    # --- Read undo log ---
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Undo log is corrupted and cannot be read.")
        return
    except OSError as e:
        print(f"Could not read undo log: {e.strerror}")
        return

    moves = data.get("moves", [])
    if not moves:
        print("No moves found in the log. Cannot undo.")
        return

    print(f"Undoing {len(moves)} move(s) from {data.get('timestamp', '?')}...\n")
    restored = 0
    failed: list[FailedFile] = []

    for entry in reversed(moves):
        src = Path(entry["from"])
        dst = Path(entry["to"])

        if not src.exists():
            print(f"Not found: {src.name}")
            failed.append(FailedFile(name=src.name, reason="File not found"))
            continue

        # --- Re-create original directory if needed ---
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"Skipped: {src.name} (no permission to restore to '{dst.parent.name}/')")
            failed.append(FailedFile(name=src.name, reason=f"No permission to restore to '{dst.parent.name}/'"))
            continue
        except OSError as e:
            print(f"Skipped: {src.name} (could not recreate folder: {e.strerror})")
            failed.append(FailedFile(name=src.name, reason=f"Could not recreate folder: {e.strerror or 'Unknown error'}"))
            continue

        # --- Restore the file ---
        try:
            shutil.move(str(src), str(dst))
        except PermissionError:
            print(f"Skipped: {src.name} (file is in use)")
            failed.append(FailedFile(name=src.name, reason="File is in use"))
            continue
        except shutil.Error as e:
            print(f"Skipped: {src.name} (move error: {e})")
            failed.append(FailedFile(name=src.name, reason=f"Move error: {e}"))
            continue
        except OSError as e:
            print(f"Skipped: {src.name} ({e.strerror})")
            failed.append(FailedFile(name=src.name, reason=e.strerror or "Unknown error"))
            continue

        print(f"{src.name}  >  Parent folder")
        restored += 1

    # --- Delete undo log ---
    try:
        log_path.unlink()
    except OSError as e:
        print(f"Warning: Could not delete undo log ({e.strerror}). Remove it manually: {log_path}")

    print(f"\n{restored} file(s) restored.")

    if failed:
        _print_failed_summary(failed)

# ----------- #
# --- CLI --- #
# ----------- #

def build_parser(__version__=None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirganise",
        description="Organizes files in a folder by classifying them by type.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        examples:
        dirganise ~/Downloads              organizes the Downloads folder
        dirganise . --dry-run              preview without moving anything
        dirganise . --undo                 undoes the last dirganise
        dirganise . --rules my_rules.json  use custom rules
        """,
    )
    parser.add_argument("folder", type=Path, nargs="?", default=Path("."), help="Folder to organize")
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Shows what would happen without moving any files",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Reverts the last dirganise in this folder",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        metavar="FILE.json",
        help="JSON with custom rules {'.ext': 'Folder'}",
    )
    parser.add_argument(
        "--v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    return parser

def main() -> None:
    try:
        __version__ = version("dirganise")
    except PackageNotFoundError:
        __version__ = "unknown"
    parser = build_parser(__version__)
    args = parser.parse_args()

    folder: Path = args.folder.expanduser().resolve()

    if not folder.exists():
        parser.error(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        parser.error(f"Not a folder: {folder}")

    print(f"\n dirganise  >  {folder}\n")

    if args.undo:
        undo_moves(folder)
        return

    rules = load_rules(args.rules)
    moves = collect_moves(folder, rules)
    organize(moves, dry_run=args.dry_run, folder=folder)
    print()

if __name__ == "__main__":
    main()