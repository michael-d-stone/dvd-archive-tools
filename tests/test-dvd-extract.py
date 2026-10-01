#!/usr/bin/env python3

import json
import sys
from pathlib import Path


EXPECTED_TITLES = 9
EXPECTED_MENUS = 16
EXPECTED_FILES = EXPECTED_TITLES + EXPECTED_MENUS

EXPECTED_TITLE_003_DURATION = 0.500


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main():
    if len(sys.argv) != 2:
        print(
            f"Usage: {sys.argv[0]} <dvd-extract-directory>",
            file=sys.stderr,
        )
        return 1

    root = Path(sys.argv[1])
    manifest_path = root / "manifest.json"

    if not manifest_path.is_file():
        return fail(f"manifest not found: {manifest_path}")

    try:
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read manifest: {exc}")

    files = manifest.get("files", [])

    titles = [
        item for item in files
        if item.get("kind") == "title"
    ]

    menus = [
        item for item in files
        if item.get("kind") == "menu"
    ]

    if len(titles) != EXPECTED_TITLES:
        return fail(
            f"expected {EXPECTED_TITLES} titles, got {len(titles)}"
        )

    if len(menus) != EXPECTED_MENUS:
        return fail(
            f"expected {EXPECTED_MENUS} menus, got {len(menus)}"
        )

    if len(files) != EXPECTED_FILES:
        return fail(
            f"expected {EXPECTED_FILES} files, got {len(files)}"
        )

    failed = [
        item for item in files
        if not item.get("verified")
    ]

    if failed:
        return fail(f"{len(failed)} files are not verified")

    title_003 = next(
        (
            item for item in titles
            if item.get("file") == "titles/title_003.mkv"
        ),
        None,
    )

    if title_003 is None:
        return fail("title_003.mkv missing from manifest")

    duration = title_003.get("duration")

    if duration is None:
        return fail("title_003.mkv has no duration")

    if abs(duration - EXPECTED_TITLE_003_DURATION) > 0.01:
        return fail(
            "title_003.mkv duration changed: "
            f"expected {EXPECTED_TITLE_003_DURATION:.3f}, "
            f"got {duration:.3f}"
        )

    summary = manifest.get("summary", {})

    if summary.get("files") != EXPECTED_FILES:
        return fail(
            f"manifest summary expected {EXPECTED_FILES} files, "
            f"got {summary.get('files')}"
        )

    if summary.get("verified") != EXPECTED_FILES:
        return fail(
            f"manifest summary expected {EXPECTED_FILES} verified, "
            f"got {summary.get('verified')}"
        )

    if summary.get("failed") != 0:
        return fail(
            f"manifest summary reports {summary.get('failed')} failures"
        )

    print("PASS: DVD regression fixture")
    print(f"  titles:   {len(titles)}")
    print(f"  menus:    {len(menus)}")
    print(f"  verified: {len(files)}/{EXPECTED_FILES}")
    print(f"  title 003: {duration:.3f} s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
