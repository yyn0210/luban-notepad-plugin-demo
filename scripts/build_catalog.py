#!/usr/bin/env python3
"""Generate catalog/v1/index.json and catalog/v2/index.json from dist/.

Run scripts/package.py first: artifact hashes and sizes come from the built
packages. Release asset URLs are derived from the version tag.

No third-party dependencies.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
REPOSITORY = {
    "id": "luban-notepad-plugin-demo",
    "name": "Luban Notepad Plugin Demo",
    "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
}
RELEASE_BASE = (
    "https://github.com/yyn0210/luban-notepad-plugin-demo/releases/download"
)
GENERATED_AT = "2026-11-01T00:00:00Z"
BAD_HASH = "0" * 64

METADATA: dict[str, dict[str, Any]] = {
    "com.luban.demo.hello": {
        "name": "Hello Demo",
        "description": "Inserts a greeting and records every run in the plugin data directory.",
        "publisher": "yyn0210",
        "tags": ["demo", "text"],
        "permissions": ["filesystem"],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo/tree/main/plugins/com.luban.demo.hello",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "localizations": {
            "zh-CN": {
                "name": "你好示例",
                "description": "插入问候语，并把每次运行记录到插件数据目录。",
            }
        },
        "versions": {
            "1.0.0": {
                "release_notes": "Initial demo release.",
                "targets": ["universal"],
            },
            "1.1.0": {
                "release_notes": "Adds configurable punctuation and keeps existing run data.",
                "targets": ["universal"],
            },
        },
    },
    "com.luban.demo.linux": {
        "name": "Linux Exact",
        "description": "Published only for linux-x64 to exercise exact target matching.",
        "publisher": "yyn0210",
        "tags": ["demo", "platform"],
        "permissions": [],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo/tree/main/plugins/com.luban.demo.linux",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "versions": {
            "1.0.0": {
                "release_notes": "linux-x64 only.",
                "targets": ["linux-x64"],
            }
        },
    },
    "com.luban.demo.windows": {
        "name": "Windows Only",
        "description": "Published only for windows-x64; hidden on every other platform.",
        "publisher": "yyn0210",
        "tags": ["demo", "platform"],
        "permissions": [],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo/tree/main/plugins/com.luban.demo.windows",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "versions": {
            "1.0.0": {
                "release_notes": "windows-x64 only.",
                "targets": ["windows-x64"],
            }
        },
    },
    "com.luban.demo.newer-api": {
        "name": "Newer API",
        "description": "Requires host API 99; listed but not installable.",
        "publisher": "yyn0210",
        "tags": ["demo", "api"],
        "permissions": [],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo/tree/main/plugins/com.luban.demo.newer-api",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "versions": {
            "1.0.0": {
                "release_notes": "Requires API 99.",
                "targets": ["universal"],
            }
        },
    },
    "com.luban.demo.badhash": {
        "name": "Bad Hash",
        "description": "Catalog hash does not match the package; installation must fail.",
        "publisher": "yyn0210",
        "tags": ["demo", "error"],
        "permissions": [],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo/tree/main/plugins/com.luban.demo.badhash",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "versions": {
            "1.0.0": {
                "release_notes": "Deliberately corrupted hash.",
                "targets": ["universal"],
            }
        },
    },
    "com.luban.demo.badsize": {
        "name": "Bad Size",
        "description": "Catalog size is smaller than the package; download must be rejected.",
        "publisher": "yyn0210",
        "tags": ["demo", "error"],
        "permissions": [],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo/tree/main/plugins/com.luban.demo.badsize",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "versions": {
            "1.0.0": {
                "release_notes": "Declared size is 100 bytes.",
                "targets": ["universal"],
                "size_override": 100,
            }
        },
    },
    "com.luban.demo.invalid": {
        "name": "Invalid Entry",
        "description": "Artifact URL is not HTTPS; the catalog parser must skip this entry.",
        "publisher": "yyn0210",
        "tags": ["demo", "error"],
        "permissions": [],
        "license": "MIT",
        "source": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "homepage": "https://github.com/yyn0210/luban-notepad-plugin-demo",
        "versions": {
            "1.0.0": {
                "release_notes": "Deliberately invalid artifact URL.",
                "targets": ["universal"],
                "url_override": "http://example.com/com.luban.demo.invalid-1.0.0.zip",
            }
        },
    },
}

# hello 1.0.0 exists in both snapshots; 1.1.0 and the bad-hash fixture are
# introduced by v2 so the update and failure paths can be tested separately.
V1_PLUGINS = [
    "com.luban.demo.hello",
    "com.luban.demo.linux",
    "com.luban.demo.windows",
    "com.luban.demo.newer-api",
]
V2_PLUGINS = [
    "com.luban.demo.hello",
    "com.luban.demo.linux",
    "com.luban.demo.windows",
    "com.luban.demo.newer-api",
    "com.luban.demo.badhash",
]
V3_PLUGINS = [
    "com.luban.demo.hello",
    "com.luban.demo.linux",
    "com.luban.demo.windows",
    "com.luban.demo.newer-api",
    "com.luban.demo.badsize",
    "com.luban.demo.invalid",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package(plugin_id: str, version: str) -> Path:
    path = DIST_DIR / f"{plugin_id}-{version}.zip"
    if not path.is_file():
        raise SystemExit(f"missing {path}; run scripts/package.py first")
    return path


def entry(plugin_id: str, versions: list[str], corrupt_hash: bool) -> dict[str, Any]:
    meta = METADATA[plugin_id]
    version_entries = []
    for version in versions:
        spec = meta["versions"][version]
        url_override = spec.get("url_override")
        if url_override:
            artifact_url = url_override
            artifact_hash = BAD_HASH
            artifact_size = 1000
        else:
            path = package(plugin_id, version)
            artifact_url = f"{RELEASE_BASE}/v{version}/{plugin_id}-{version}.zip"
            artifact_hash = BAD_HASH if corrupt_hash else sha256(path)
            artifact_size = spec.get("size_override", path.stat().st_size)
        version_entries.append(
            {
                "version": version,
                "api_version": 99 if plugin_id == "com.luban.demo.newer-api" else 1,
                "released_at": GENERATED_AT,
                "release_notes": spec["release_notes"],
                "artifacts": [
                    {
                        "target": target,
                        "url": artifact_url,
                        "sha256": artifact_hash,
                        "size": artifact_size,
                    }
                    for target in spec["targets"]
                ],
            }
        )
    latest = max(versions, key=version_key)
    result: dict[str, Any] = {
        "id": plugin_id,
        "name": meta["name"],
        "description": meta["description"],
        "publisher": meta["publisher"],
        "verified": False,
        "tags": meta["tags"],
        "permissions": meta["permissions"],
        "source": meta["source"],
        "homepage": meta["homepage"],
        "license": meta["license"],
        "latest_version": latest,
        "versions": version_entries,
    }
    if "localizations" in meta:
        result["localizations"] = meta["localizations"]
    return result


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def catalog(
    plugin_ids: list[str],
    corrupt: set[str],
    versions_by_plugin: dict[str, list[str]],
) -> dict[str, Any]:
    plugins = []
    for plugin_id in plugin_ids:
        versions = versions_by_plugin.get(
            plugin_id, list(METADATA[plugin_id]["versions"])
        )
        plugins.append(entry(plugin_id, versions, plugin_id in corrupt))
    plugins.sort(key=lambda item: item["id"])
    return {
        "catalog_version": 1,
        "repository": REPOSITORY,
        "generated_at": GENERATED_AT,
        "plugins": plugins,
    }


def main() -> int:
    snapshots = {
        "v1": catalog(V1_PLUGINS, set(), {"com.luban.demo.hello": ["1.0.0"]}),
        "v2": catalog(V2_PLUGINS, {"com.luban.demo.badhash"}, {}),
        "v3": catalog(V3_PLUGINS, set(), {}),
        "bad-version": {
            "catalog_version": 2,
            "repository": REPOSITORY,
            "generated_at": GENERATED_AT,
            "plugins": [],
        },
    }
    for name, value in snapshots.items():
        path = ROOT / "catalog" / name / "index.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {path.relative_to(ROOT)} ({len(value['plugins'])} plugins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
