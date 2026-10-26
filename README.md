# Samsung/TizenOS cleanup

A calmer Samsung TV: fewer unwanted background features, a family-focused home screen, and documented ways to undo the changes.

**[Read the complete guide →](GUIDE.md)** — setup, temporary root, every reviewed repository, the 82-record reference selection, backups, Home-button routing and recovery.

This project combines a real [CleanFrame](https://github.com/nthnclrk/CleanFrame) adaptation with the lessons from cleaning a Samsung S85D. It keeps Tizen underneath. It is not a replacement firmware, a permanent-root installer or a universal debloat button.

## What is here

- **Family Home 0.5.1 source:** Dock/List layouts, local wallpapers and fonts, reordering, large/compact app cards, square Apps and a vertical + control.
- **Family defaults:** Live TV, RTVE Play, Movistar Plus+, Prime Video and Disney+, then compact Apple TV/Plex/Stremio. Customize them for your household.
- **Offline build tools:** create your own stable application identity, validate public assets and build an unsigned widget for your Samsung signing profile.
- **Cleanup reference profiles:** 38 core plus 44 extended app records, exact service-marker mappings and known limitations.
- **Guarded SQL planner:** generate apply/restore SQL from your own consistent registry backup. It never connects to the TV.
- **Native Home helper source:** one-shot, reversible assignment for the exact qualified S85D firmware. No resident daemon.
- **Project-memory templates:** keep your own private facts, source revisions, commands and recovery evidence.

## Start with the launcher

Python 3 and Node.js are needed locally. From a new clone:

```sh
python3 tools/project.py init
npm ci
npm run check
npm test
npm run preview
```

Preview at **http://127.0.0.1:8080**. `init` generates a new app identity for an independent installation; do it once, then keep that identity and author certificate stable. The preview does not control a TV. Build with `npm run build`, then follow the [signing/install recipe](GUIDE.md#4-build-and-install-family-home) using your own Samsung certificate and TV DUID.

Installing the widget alone does **not** replace the physical Home key. Follow the [separate qualified Home recipe](GUIDE.md#5-make-the-physical-home-button-open-family-home) after testing the launcher.

## Evidence and limits

Reference: **TQ65S85DAEXXC**, **T-PTMDDEUC-0090-2130.0**, build **T-PTMDDEUC-0090-REL-202605141701**, Tizen 9 / ARMv7. Evidence cutoff: **2026-10-26**.

The core cleanup passed a real power disconnect and the owner confirmed normal daily functions. Family Home was installed, and the owner confirmed the physical Home key opens it. The extended cleanup is **not fully verified**: Gaming Hub still had a running process, and seven runtime masks disappear on reboot. No package files were deleted. No measured speedup or total telemetry elimination is claimed.

New public host tools have local validation; their publication is not a new live-device test. Read [compatibility](docs/compatibility.md), [validation](docs/validation.md) and the full guide before device writes. Backups are configuration recovery, not a full firmware image.

## Source layout

| Path | Purpose |
| --- | --- |
| `GUIDE.md` | Complete shareable field guide |
| `app/` | Actual offline TV launcher and credited assets |
| `tools/project.py` | Identity, source validation and unsigned build |
| `tools/registry_plan.py` | Offline guarded SQL generation |
| `tools/extract_backup.py` | Verify/decode an authenticated root backup result |
| `profiles/` | Model-specific reference selections |
| `native-home/` | Qualified helper source and explicit-host runner |
| `tests/` | Launcher state, backup validation and SQL recovery tests |
| `memory/` | Private journal/corpus setup templates |
| `.local/`, `dist/` | Ignored private state and generated packages |

## Credits

Visual foundation: **Nathan Clark’s CleanFrame**, MIT, revision `fa537d1892b71d2de2bf94c24cbff3812e9f70d5`. Temporary-root research used **chris-ritsen/samsung-tv-root**, v0.0.12, and cleanup methodology was informed by **quiet-tizen**, independently qualified against this S85D. Every original owner-supplied repo and its actual test status appears in the [repository comparison](GUIDE.md#14-every-original-github-repository).

Original project additions use MIT. Fonts, photography and brand assets retain their own terms in [third-party notices](THIRD_PARTY_NOTICES.md) and the [asset credits](docs/asset-sources.md). Brand owners retain their trademarks. This project is not affiliated with or endorsed by Samsung or the streaming services.
