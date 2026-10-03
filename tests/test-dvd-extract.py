#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_json(path, description):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"FAIL: cannot read {description}: {exc}",
            file=sys.stderr,
        )
        return None


def main():
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} <fixture.json> <dvd-extract-directory>",
            file=sys.stderr,
        )
        return 1

    fixture_path = Path(sys.argv[1])
    root = Path(sys.argv[2])
    manifest_path = root / "manifest.json"

    fixture = load_json(fixture_path, "fixture")
    if fixture is None:
        return 1

    manifest = load_json(manifest_path, "manifest")
    if manifest is None:
        return 1

    name = fixture.get("name", fixture_path.stem)
    expected = fixture.get("expected", {})
    files = manifest.get("files", [])

    titles = [
        item for item in files
        if item.get("kind") == "title"
    ]

    menus = [
        item for item in files
        if item.get("kind") == "menu"
    ]

    expected_titles = expected.get("titles")
    expected_menus = expected.get("menus")
    expected_files = expected.get("files")
    expected_verified = expected.get("verified")
    expected_failed = expected.get("failed")

    if expected_titles is not None and len(titles) != expected_titles:
        return fail(
            f"expected {expected_titles} titles, got {len(titles)}"
        )

    if expected_menus is not None and len(menus) != expected_menus:
        return fail(
            f"expected {expected_menus} menus, got {len(menus)}"
        )

    if expected_files is not None and len(files) != expected_files:
        return fail(
            f"expected {expected_files} files, got {len(files)}"
        )

    failed = [
        item for item in files
        if not item.get("verified")
    ]

    verified_count = len(files) - len(failed)

    if expected_verified is not None and verified_count != expected_verified:
        return fail(
            f"expected {expected_verified} verified files, "
            f"got {verified_count}"
        )

    if expected_failed is not None and len(failed) != expected_failed:
        return fail(
            f"expected {expected_failed} failed files, got {len(failed)}"
        )

    manifest_files = {
        item.get("file"): item
        for item in files
        if item.get("file")
    }

    for filename, rules in fixture.get("files", {}).items():
        item = manifest_files.get(filename)

        if item is None:
            return fail(f"expected file missing: {filename}")

        if "duration" in rules:
            actual = item.get("duration")

            if actual is None:
                return fail(f"{filename} has no duration")

            expected_duration = float(rules["duration"])
            tolerance = float(rules.get("duration_tolerance", 0.01))

            if abs(actual - expected_duration) > tolerance:
                return fail(
                    f"{filename} duration changed: "
                    f"expected {expected_duration:.3f} "
                    f"+/- {tolerance:.3f}, got {actual:.3f}"
                )

        if "chapters" in rules:
            actual_chapters = item.get("chapter_count")
            expected_chapters = int(rules["chapters"])

            if actual_chapters != expected_chapters:
                return fail(
                    f"{filename} chapter count changed: "
                    f"expected {expected_chapters}, "
                    f"got {actual_chapters}"
                )

        if "streams" in rules:
            actual_streams = {}

            for stream in item.get("streams", []):
                stream_type = stream.get("codec_type")

                if stream_type is None:
                    continue

                actual_streams[stream_type] = (
                    actual_streams.get(stream_type, 0) + 1
                )

            for stream_type, expected_count in rules["streams"].items():
                actual_count = actual_streams.get(stream_type, 0)

                if actual_count != expected_count:
                    return fail(
                        f"{filename} {stream_type} stream count changed: "
                        f"expected {expected_count}, got {actual_count}"
                    )

    summary = manifest.get("summary", {})

    if expected_files is not None:
        if summary.get("files") != expected_files:
            return fail(
                f"manifest summary expected {expected_files} files, "
                f"got {summary.get('files')}"
            )

    if expected_verified is not None:
        if summary.get("verified") != expected_verified:
            return fail(
                f"manifest summary expected {expected_verified} verified, "
                f"got {summary.get('verified')}"
            )

    if expected_failed is not None:
        if summary.get("failed") != expected_failed:
            return fail(
                f"manifest summary expected {expected_failed} failures, "
                f"got {summary.get('failed')}"
            )

    print(f"PASS: {name}")
    print(f"  titles:   {len(titles)}")
    print(f"  menus:    {len(menus)}")
    print(f"  verified: {verified_count}/{len(files)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
