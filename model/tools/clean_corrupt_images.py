"""
Utility script to scan dataset directories for unreadable images and optionally
delete them. Useful when TensorFlow raises `jpeg::Uncompress failed` errors
during training.
"""

import argparse
import os
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import TRAIN_DIR, VAL_DIR, TEST_DIR  # noqa: E402

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}


def iter_image_files(directory: Path):
    for path in directory.rglob("*"):
        if path.is_file() and path.suffix.lower() in VALID_IMAGE_EXTENSIONS:
            yield path


def find_corrupt_images(directories):
    corrupt_files = []

    for directory in directories:
        directory = Path(directory)
        if not directory.exists():
            continue

        for file_path in iter_image_files(directory):
            try:
                with Image.open(file_path) as img:
                    img.verify()
                with Image.open(file_path) as img:
                    img.load()
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                corrupt_files.append((file_path, str(exc)))

    return corrupt_files


def main():
    parser = argparse.ArgumentParser(
        description="Detect (and optionally delete) corrupt images in the dataset."
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete corrupt files after listing them.",
    )
    parser.add_argument(
        "--extra-dir",
        action="append",
        default=[],
        help="Additional directory to scan (can be used multiple times).",
    )
    args = parser.parse_args()

    directories = [TRAIN_DIR, VAL_DIR, TEST_DIR]
    directories.extend(Path(p) for p in args.extra_dir)

    corrupt_images = find_corrupt_images(directories)

    if not corrupt_images:
        print("✓ No corrupt images detected.")
        return

    print("⚠ Found unreadable image files:")
    for file_path, error in corrupt_images:
        print(f"  - {file_path}: {error}")

    if args.delete:
        deleted = 0
        for file_path, _ in corrupt_images:
            try:
                Path(file_path).unlink()
                deleted += 1
            except OSError as exc:
                print(f"    Failed to delete {file_path}: {exc}")
        print(f"\n✓ Deleted {deleted} corrupt files.")
    else:
        print("\nRun with --delete to remove these files automatically.")


if __name__ == "__main__":
    main()

