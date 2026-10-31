#!/usr/bin/env python3
"""Build one deterministic zip per plugin version.

Layout: plugins/<plugin-id>/<version>/ holds plugin.json and the Lua sources.
The archive stores those files at its root, which is what the installer
expects. Output goes to dist/<plugin-id>-<version>.zip.

No third-party dependencies.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
DIST_DIR = ROOT / "dist"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package(version_dir: Path, manifest: dict) -> Path:
    plugin_id = manifest["id"]
    version = manifest["version"]
    output = DIST_DIR / f"{plugin_id}-{version}.zip"
    files = sorted(path for path in version_dir.rglob("*") if path.is_file())
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = path.relative_to(version_dir).as_posix()
            info = zipfile.ZipInfo(name, FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return output


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    manifests = sorted(PLUGINS_DIR.glob("*/*/plugin.json"))
    if not manifests:
        print("no plugins found", file=sys.stderr)
        return 1
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        version_dir = manifest_path.parent
        if version_dir.name != manifest.get("version"):
            print(
                f"{manifest_path}: directory '{version_dir.name}' does not match "
                f"version '{manifest.get('version')}'",
                file=sys.stderr,
            )
            return 1
        if not (version_dir / manifest.get("main", "")).is_file():
            print(f"{manifest_path}: main file is missing", file=sys.stderr)
            return 1
        output = package(version_dir, manifest)
        print(
            f"{output.name} size={output.stat().st_size} sha256={sha256(output)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
