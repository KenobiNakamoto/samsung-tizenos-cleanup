# Publication validation

Local export checked on 2026-10-26. No TV connection, installation, reboot or feature change was performed while preparing this repository.

- JavaScript syntax, application identity consistency, offline CSP and public-font hashes passed.
- Six mocked DOM/state tests passed: card geometry, remote focus, settings migration, installed-app launch IDs, edit/reorder/undo behavior and layout/catalog filtering.
- Seventeen Python tests passed for guarded SQL apply/restore, unrelated-record preservation, drift/missing-app/trigger rejection, safe quoting, authenticated backup extraction, failed cleanup, wrong identity/hash, truncation, native Home preflight guards and independent app identity initialization. Native guard tests use mocked HTTP/SDB and do not contact a TV.
- An unsigned public-font widget built successfully. This build is ignored by Git; every TV owner must sign their own widget.
- The guarded native helper compiled with .NET SDK 6.0.428, with no warnings/errors. Compilation does not qualify the adapted host runner on another TV.
- A bounded export audit checked candidate file paths/text for private local paths, LAN addresses, MAC addresses, key/token patterns and certificate identity, and checked relative Markdown links. It is not a mathematical guarantee that no possible sensitive value exists.

Historical live results and their limits are in [compatibility](compatibility.md) and [the guide](../GUIDE.md). The new public host adaptations have not undergone a fresh live-TV cycle. There is no claim that the extended cleanup passed cold boot or eliminated all telemetry.

Reproduce local checks:

```sh
npm ci
npm run check
npm test
python3 -m unittest discover -s tests -p 'test_*.py'
npm run build
```

Do not publish private .local files, generated/signed widgets, certificates, raw backups or your device baselines. Review the staged tree and asset notices before any new release.
