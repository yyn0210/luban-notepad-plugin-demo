# Luban Notepad plugin demo

Example plugins and catalog fixtures used to exercise the Luban Notepad plugin
store end to end.

The repository hosts two catalog snapshots:

```text
https://raw.githubusercontent.com/yyn0210/luban-notepad-plugin-demo/main/catalog/v1/index.json
https://raw.githubusercontent.com/yyn0210/luban-notepad-plugin-demo/main/catalog/v2/index.json
```

- `v1` lists `com.luban.demo.hello` 1.0.0 plus the platform and API fixtures.
- `v2` adds `com.luban.demo.hello` 1.1.0 (update test) and a deliberately
  corrupted hash entry (download verification test).

Plugin packages are published as GitHub Release assets. Every catalog entry
carries the SHA-256 and byte size of its package.

## Layout

```text
plugins/<plugin-id>/<version>/   plugin source, one directory per version
scripts/package.py               build dist/<id>-<version>.zip deterministically
scripts/build_catalog.py         generate catalog/v1 and catalog/v2 from dist/
catalog/v1/index.json            first snapshot (hello 1.0.0)
catalog/v2/index.json            second snapshot (hello 1.1.0, bad hash)
```

## Fixtures

| Plugin | Purpose |
| --- | --- |
| `com.luban.demo.hello` | Install, permission approval, command run, data persistence, update |
| `com.luban.demo.linux` | Exact `linux-x64` artifact match |
| `com.luban.demo.windows` | `windows-x64` only; must be hidden on other platforms |
| `com.luban.demo.newer-api` | `api_version` 99; listed but not installable |
| `com.luban.demo.badhash` | v2 only; SHA-256 mismatch must abort installation |

## Build packages

```bash
python3 scripts/package.py
```

Packages are written to `dist/` and are not committed.

## Regenerate catalogs

```bash
python3 scripts/build_catalog.py
```

The script reads the packages in `dist/`, so run `package.py` first. Catalog
files are committed because the editor reads them directly over HTTPS.

## Manual test flow

1. Point `plugin_store_url` at the `v1` catalog.
2. Install `com.luban.demo.hello` 1.0.0, approve `filesystem`, run
   `demo.hello.run` twice.
3. Switch the URL to the `v2` catalog, update to 1.1.0, run the command again;
   the run counter must continue instead of restarting.
4. Select `com.luban.demo.badhash` and install; the download must be rejected
   before anything is written to the plugin directory.

The plugins only write inside their own data directory and log markers prefixed
with `DEMO_`.
