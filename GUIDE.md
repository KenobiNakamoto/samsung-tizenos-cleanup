# Samsung/TizenOS cleanup — the complete field guide

A quieter Samsung TV, a family-focused home screen, and a way back.

**Project:** [KenobiNakamoto/samsung-tizenos-cleanup](https://github.com/KenobiNakamoto/samsung-tizenos-cleanup)  
**Evidence cutoff:** 26 October 2026. This guide describes one real S85D project and the source revisions actually reviewed. It does not promise compatibility with every Samsung TV or future firmware.

You can send this file on its own. The linked repository supplies the launcher, small local tools, reference profiles and native Home helper source. It deliberately excludes the original household’s device identifiers, credentials, signed packages, backups and raw logs. Your television needs its **own** inventory, signing certificates and recovery baseline.

## Contents

1. [What we achieved, and what is unfinished](#1-what-we-achieved-and-what-is-unfinished)
2. [Choose your route](#2-choose-your-route)
3. [Prepare the TV and computer](#3-prepare-the-tv-and-computer)
4. [Build and install Family Home](#4-build-and-install-family-home)
5. [Make the physical Home button open Family Home](#5-make-the-physical-home-button-open-family-home)
6. [Get temporary root and inventory the TV](#6-get-temporary-root-and-inventory-the-tv)
7. [Back up before cleanup](#7-back-up-before-cleanup)
8. [Disable selected apps without deleting their files](#8-disable-selected-apps-without-deleting-their-files)
9. [Voice, ads, recognition and service controls](#9-voice-ads-recognition-and-service-controls)
10. [The complete reference target list](#10-the-complete-reference-target-list)
11. [Verify after a real power cycle](#11-verify-after-a-real-power-cycle)
12. [Undo and recovery](#12-undo-and-recovery)
13. [Problems we hit and how we diagnosed them](#13-problems-we-hit-and-how-we-diagnosed-them)
14. [Every original GitHub repository](#14-every-original-github-repository)
15. [Other projects and replacement-OS limits](#15-other-projects-and-replacement-os-limits)
16. [Keep a local project memory](#16-keep-a-local-project-memory)
17. [What a future maintainer should do next](#17-what-a-future-maintainer-should-do-next)

## 1. What we achieved, and what is unfinished

This is a **Tizen cleanup and launcher replacement**, not a new operating system. Samsung’s kernel, drivers, DRM, tuner, audio and app platform still run underneath. We retained native streaming apps, conventional broadcast TV, HDMI, settings, accessibility, casting and OLED panel-care functions.

| Layer | Observed result on the reference TV | Important boundary |
| --- | --- | --- |
| Developer connection | Official Samsung SDB connected over the LAN | A reachable network port alone did not establish usable SDB |
| Temporary root | Repeated authenticated UID/EUID 0 sessions through the archive route | Root was temporary; SMACK remained `User`; ordinary retail SDB shell stayed disabled |
| First cleanup | 38 app records across 31 packages disabled; four voice preferences off; nine vendor stop markers; ten units inactive; no selected processes in two samples after cold boot | Package files were retained. The owner confirmed normal picture, sound, remote, Live TV and usual streaming apps after this batch |
| Additional cleanup | 44 further app records across 41 packages disabled; three more vendor markers; seven runtime masks; app preloading and TV Plus auto-start disabled | Gaming Hub still had one running process. A separate cold-boot verification is pending; runtime masks will disappear at reboot |
| Latest combined audit | All 82 selected app records disabled; all 505 nonselected records matched the incremental backup | This is a dated registry/runtime audit, not proof that every form of telemetry was removed |
| Family Home | Version 0.5.1 installed and launched; based directly on CleanFrame | New public packaging/host tools are adapted for sharing; they have local tests, not a new live-TV qualification |
| Physical Home button | Owner confirmed pressing Home from a streaming app opens Family Home | Undocumented native assignment, qualified on the exact reference build; not achieved merely by installing a widget |
| Rollback | Original Home assignment was restored and reapplied successfully; launcher version rollback was exercised | Incremental cleanup inverse SQL was tested locally; that whole live restoration was not exercised |
| Permanent root | Not installed | Explicitly stopped as a project direction |
| Full replacement OS | None installed or qualified | There is no verified general-purpose alternative OS image for this S85D in this project |

The reference TV was **TQ65S85DAEXXC (S85D)**, firmware **T-PTMDDEUC-0090-2130.0**, build **T-PTMDDEUC-0090-REL-202605141701**, Tizen **9.0**, **ARMv7/32-bit**. Host tools included official SDB **4.2.36** and Tizen Studio **10** on an Apple Silicon Mac. The SDK version does not upgrade the TV’s firmware.

There is no measured “3× faster” result or “one-second cold boot” result here. There is no packet-capture proof of zero telemetry. Permissions, package names and strings establish capabilities or likely roles; they do not alone prove that a service sends recordings or screenshots anywhere.

## 2. Choose your route

**A. New home screen only:** prepare Developer Mode, create your own Samsung signing profile, build/sign/install Family Home, test every app. No root is needed for this route. The physical Home button initially still opens Samsung Home.

**B. New home screen plus physical Home routing:** finish A, then qualify the one-shot native Home helper against your model, firmware, architecture and native libraries. Capture your own original settings, test restoration, then make the assignment. Our helper refuses other firmware/builds.

**C. Privacy cleanup:** qualify temporary root, take a consistent backup, review app/service dependencies, disable a small selected batch, verify twice, then cold boot and verify again. Add further groups separately. Do not begin by running every repository’s removal list.

A practical order for a friend is **A → test → B → test recovery → C in small batches**. Our original development mixed these stages while researching; you do not need to repeat that detour. If your model differs, finish A while investigating B/C independently.

Commands below are for a POSIX terminal such as macOS or Linux. Execute code blocks in order within their section. Lines outside code blocks are explanation, not terminal commands. Windows users need the corresponding SDK paths, Python invocation and shell quoting.

## 3. Prepare the TV and computer

### Record the starting point

Save the exact model, firmware/build, current TV IP, wired/Wi-Fi identity, normal input, installed family apps and any settings you change. Keep device identifiers private. Reserve the TV’s address in the router if possible; ours changed after a later power-on, and the old address produced misleading connection failures.

Check picture, sound, volume, remote buttons, broadcast channels, HDMI, subtitles, accessibility and a DRM-protected stream before changing anything. Record the features your family actually uses. Ambient mode, Bixby, cloud gaming and hotel features are useful to some people; they are not universally “bloat.”

### Built-in privacy and performance controls

On the TV, inspect Settings for Device Care/storage management, Viewing Information Services or ACR consent, interest-based advertising, voice wake-up, assistant activation and Smart Hub auto-start. Names and menu paths vary by model/region/firmware. Record the actual values and turn off unwanted optional features. Device Care is separate from root access and does not prove telemetry is disabled.

If your TV has a physical microphone switch, use the manual to locate it and confirm its off indication. A microphone in the remote can be a separate input path. We found the switch on the reference TV but did not instrument the audio hardware to prove its state. Software voice disabling is not a substitute for checking the physical control.

### Install Samsung development tools

Use Samsung/Tizen’s official downloads and documentation:

- [Samsung TV SDK installation](https://developer.samsung.com/smarttv/develop/getting-started/setting-up-sdk/installing-tv-sdk.html)
- [Connecting the TV to the SDK](https://developer.samsung.com/smarttv/develop/getting-started/using-sdk/tv-device.html)
- [Samsung TV certificate profile](https://developer.samsung.com/smarttv/develop/getting-started/setting-up-sdk/creating-certificates.html)
- [Tizen command-line interface](https://docs.tizen.org/application/web/get-started/cli/)

Install Tizen Studio, the Samsung TV extension/web tools and the Samsung Certificate Extension through Package Manager. An SDK installer completing does not mean its optional TV/signing extensions are installed; check Package Manager’s installed-package view.

### The exact certificate-software setup we used on the Mac

These were Samsung’s official development/signing tools, not a custom certificate authority or the earlier general-purpose certificate setup. A friend should create their own Samsung profile through this workflow.

1. Download the **Tizen SDK 10.0 web IDE for macOS** from the official [SDK installer directory](https://download.tizen.org/sdk/Installer/tizen-sdk_10.0/). Our recorded filename was `web-ide_Tizen_SDK_10.0_macos-64.dmg`. Choose the supported installer for your own host; this filename records our installation, not a promise of compatibility with every Mac.
2. Open the downloaded disk image in **Finder**, then double-click **installer**. In our session, automation did not expose the setup window; the owner opened it manually and saw the installer/license screen.
3. Review the license and complete the installer. Record the SDK location you choose; examples below use `$HOME/tizen-studio`. Installing this software changes the computer, not the TV firmware.
4. Open **Tizen Studio Package Manager**. The first screen can be **Main SDK**, showing platform versions such as 9.0 and 8.0. Seeing that screen does not mean Samsung’s certificate tools are installed. At our first check the base SDK was installed, but Samsung Certificate Extension and the full Certificate Manager product were missing.
5. Close other Tizen IDE/tool windows if Package Manager requests it. Open the **Extension SDK** tab and install **TV Extensions**, including the web-app development tools, and **Samsung Certificate Extension**. Allow downloads and installation to finish; use the Progress view, then the installed-package view to check completion. Review the component licenses.
6. Our successful manifest contained **TV Extensions 10.0.0**, **Samsung Certificate Extension 2.0.75** and **Certificate Manager product 1.3.11**. These are historical working versions, not an instruction to downgrade a newer supported installation. The earlier official guidance we reviewed required Certificate Extension 2.0.73 or newer; use the current supported Samsung extension rather than an old bundled certificate plugin.
7. Open **Tools → Certificate Manager**, or launch the installed Certificate Manager application. An empty profile list at this point is normal: installing the certificate software does not create your certificates.
8. Follow the [profile-creation steps below](#create-your-own-samsung-tv-signing-profile). Complete both author and distributor steps, click **Finish**, and verify that the profile appears in Certificate Manager with both certificates and their validity dates. Our original profile label was `FamilyHomeTV`; the friend-facing examples use `MyFamilyTV`.
9. Use that same profile label in the SDK signing command. Keep its author identity for updates and protect its private backup. No signing password, certificate private key or household device identifier is included in this guide or repository.

The package count grew from 83 to 131 during our setup. That was corroborating evidence for our install, not a required count for a friend’s different SDK release. We did not need to reboot the TV merely to install the SDK or issue the certificates. TV restart checkpoints are listed separately below.

During our original signing attempt, the automation environment could not write some SDK configuration/log files. The owner then ran the prepared signing command in Terminal successfully. If an automation tool has the same problem, check its access to the selected SDK/data directories or run the reviewed command in your own Terminal; changing the TV’s firmware or recreating a valid certificate is not the remedy. Actual TV installation and launch are later, separate commands.

Use the official `sdb` from your SDK. Do not replace a working SDK binary with an unexplained third-party download.

### Enable Developer Mode on the TV

1. Open the TV’s Apps screen.
2. Enter **12345**. On a small remote without number keys, open its on-screen number pad first; the exact button/menu differs between remotes.
3. Enable Developer Mode and enter **your computer’s LAN IP**, not the TV’s IP or the router gateway.
4. Restart the TV as the Developer Mode dialog requests. A short press on Power may only enter standby.
5. Keep the TV awake and both devices on the same reachable LAN. Allow the requested development connection on the TV. Ordinary remote-control approval is distinct from Developer Mode and signing.

Set paths for **your** machine. `192.0.2.50` below is a documentation placeholder, not an address to discover or use unchanged:

```sh
export TV_IP='192.0.2.50'
export SDB="$HOME/tizen-studio/tools/sdb"
export TIZEN="$HOME/tizen-studio/tools/ide/bin/tizen"
"$SDB" version
"$SDB" connect "$TV_IP:26101"
"$SDB" -s "$TV_IP:26101" get-state
"$SDB" -s "$TV_IP:26101" capability
```

Expected: state `device`. On our retail build, `platform_version: 9.0`, `cpu_arch: armv7`, `intershell_support: disabled` and `rootonoff_support: disabled` were normal. They describe official developer restrictions; they do not prove or disprove the separate archive exploit.

Known externally visible services on the reference configuration were HTTP metadata/remote at **8001**, TLS remote at **8002**, a service endpoint at **9197**, and developer SDB at **26101**. The Mac’s local SDB helper listens on **26099**. These are observations, not a promise that every model exposes the same services. `http://TV_IP:8001/api/v2/` can report identity and developer-host metadata; redact its identifiers before sharing.

## 4. Build and install Family Home

### What is included

The current UI preserves CleanFrame’s wallpapers, public fonts, Dock/List layouts, pre-rendered translucent materials and remote navigation. Our adaptation adds the family app order, compact card group, square Apps tile, vertical + control, card-size settings, reordering and a migration that hides HBO from the initial main view.

Default large cards: **Live TV → RTVE Play → Movistar Plus+ → Prime Video → Disney+**. The compact group contains **Apple TV, Plex and Stremio**; it can accommodate a fourth favorite. Netflix remains available in All apps. Hiding a card does not uninstall its app. HBO can be added again if an installed application is actually detected.

All launcher assets are bundled. Its content security policy blocks network connections. It has no launcher analytics, online microphone service, CDN dependency or Mac server requirement at runtime. Launched streaming apps retain their own network behavior and privacy policies. Browser preview has mocked/no TV APIs and cannot prove launch behavior on hardware.

### Clone, create an independent identity and preview

Install Python 3 and a maintained Node.js version. The local test dependency is pinned in the lockfile. From a new working folder:

```sh
git clone https://github.com/KenobiNakamoto/samsung-tizenos-cleanup.git
cd samsung-tizenos-cleanup
python3 tools/project.py init
npm ci
npm run check
npm test
npm run preview
```

Open `http://127.0.0.1:8080` on the computer. Stop preview with Ctrl-C when finished. The initializer gives an independent installation a new ten-character Tizen package ID and updates the manifest, launcher self-filter, native helper target and tests together. It refuses a second initialization. Keep that identity stable for future updates. Do **not** initialize a checkout intended to update an already installed Family Home with its existing identity.

Preview at a 1920×1080 viewport for the intended TV geometry. Use arrow keys, Enter and Back/Escape, and inspect settings, both layouts, the compact group, Apps and +. Photos and brand marks retain their separate licenses; see `THIRD_PARTY_NOTICES.md` and `docs/asset-sources.md`.

### Create your own Samsung TV signing profile

1. Open Certificate Manager, choose **+ → Samsung → TV**, and create a profile, for example `MyFamilyTV`.
2. Create your own author certificate and keep its password private. Complete Samsung account authentication in the wizard.
3. Create a distributor certificate and add **your television’s DUID**, normally from the connected-device list. A DUID is not an IP address.
4. At the “distributor certificate is complete” screen, click **Finish**. In Certificate Manager, verify the profile is listed, both **Author Certificate** and **Distributor Certificate** are present, their validity dates are current, and the intended profile is selected. These were two separate completion screens in our session.
5. Keep encrypted/private backups of the author certificate, distributor certificate and profile outside the source repository. The original certificate wizard saved them under a `SamsungCertificate/PROFILE_NAME` directory in the owner’s home folder; record the actual destination displayed on your machine rather than assuming a fixed path.
6. If Device Manager offers **Permit to install applications**, follow Samsung’s workflow for that connected TV when required. This is a conditional vendor step, not an action we separately verified as necessary on our TV.

The author identity must remain consistent when updating an app. Our household’s certificate is not included. A general-purpose document-signing certificate is not a substitute for Samsung’s TV author/distributor chain. Do not put certificate passwords in command history or the journal; let the SDK prompt or use its configured credential store.

### Build, sign, install and launch

From the repository root, with `TV_IP`, `SDB` and `TIZEN` set as above:

```sh
npm run build
mkdir -p dist/signed
"$TIZEN" package -t wgt -s MyFamilyTV -o dist/signed -- dist/FamilyHome-unsigned.wgt
```

Confirm the SDK reports successful creation. The resulting signed filename is normally `dist/signed/FamilyHome-unsigned.wgt`; use the actual SDK output if it differs. Our local development additionally verified XML signatures, all referenced payload hashes, author/distributor identity and tamper rejection. This public build tool produces an unsigned ZIP; it does not perform independent XML cryptographic verification. Do not describe the mere presence of signature XML files as cryptographic validation.

```sh
"$TIZEN" install -s "$TV_IP:26101" -n FamilyHome-unsigned.wgt -- dist/signed
python3 tools/project.py check
```

The last command prints your application ID. Use that exact ID for launching:

```sh
export APP_ID='PASTE_THE_APPLICATION_ID_PRINTED_ABOVE'
"$TIZEN" run -s "$TV_IP:26101" -p "$APP_ID"
```

Confirm the actual screen on the TV. Test D-pad navigation and every required streaming app, Live TV, Apps, settings, reordering and returning from a stream. Do not change native Home until this works. Preserve the previous signed build and its matching source before updating. The official installer validates the certificate chain/device authorization during installation, but that is separate from your own release review.

App IDs differ by region, version and installation. `app/device.js` maps known reference IDs and uses `tizen.application.getAppsInfo()` to discover installed consumer apps. If your app is missing, inspect your real app list and update the mapping; do not invent an ID from its brand name. The default manifest targets Tizen 9.0. Lowering that number alone does not establish compatibility with older TVs.

## 5. Make the physical Home button open Family Home

Installing a launcher does not automatically capture Home. On our TV a small, one-shot .NET helper used Samsung’s native application-operation API as **SDK user 901**, plus verified configuration writes. It did not require root or a background watcher. The actual Home key was then tested from a streaming app by the owner.

Source is in `native-home/Control.cs`. It uses the main application-control operation, checks web-app boot eligibility, and records these settings:

- Native default application for `http://tizen.org/appcontrol/operation/main`.
- `db/appfw/home_appid`.
- `db/appfw/startup_appid`.
- `db/appfw/booting_appid_backup`.
- `db/first_screen/type`.
- `db/menu/smart_hub/ontvsetting/auto_start`.

Apply changes the native Home operation, `home_appid` and auto-start; it does not indiscriminately overwrite all four saved strings. Restoration writes the exact original values. Boot behavior also involves Samsung’s own application framework, so inspect actual readback and test cold boot separately.

**Scope:** the helper requires 32-bit SDK UID 901, exact firmware `T-PTMDDEUC-0090-2130.0` and exact build `T-PTMDDEUC-0090-REL-202605141701`. The host runner also requires model `TQ65S85DAEXXC` and binds the recovery baseline to the TV’s reported unique identity and your chosen launcher ID. An S90D, QN90F or The Frame with a similar menu is not an automatic match. Do not remove the checks to get past an error; qualify the native ABI and behavior on a different model first.

The public runner was adapted from the successful private runner to accept explicit host/SDK paths and create a fresh private baseline. It stages files and uses the SDK package-name command foothold. Even `query` is therefore **not a pure network read**. The private version’s live success is not a claim that this newly adapted public runner has been installed on another TV.

For the exact supported reference build, after installing and testing your launcher, build with the .NET 6 SDK (6.0.428 was used for the original work):

```sh
dotnet build native-home/Control.csproj -c Release -o native-home/out
python3 native-home/run.py inspect --host "$TV_IP" --sdb "$SDB"
python3 native-home/run.py capture --host "$TV_IP" --sdb "$SDB"
```

Review `.local/native-home/original.json` and `BASELINE.json`, back them up privately, and preserve them unchanged. `capture` refuses to overwrite an existing baseline. A reported `BootSupported` of zero or a missing native library means stop and investigate. Confirm that the captured original Home belongs to the TV’s working original UI.

Then perform a reversible qualification cycle, one command at a time, reviewing each report before the next:

```sh
python3 native-home/run.py apply --host "$TV_IP" --sdb "$SDB"
python3 native-home/run.py query --host "$TV_IP" --sdb "$SDB"
python3 native-home/run.py restore --host "$TV_IP" --sdb "$SDB"
python3 native-home/run.py query --host "$TV_IP" --sdb "$SDB"
python3 native-home/run.py apply --host "$TV_IP" --sdb "$SDB"
```

Test the physical Home key after each assignment, including from a streaming app. Test startup after a separate full power disconnect. Keep Samsung Home and Settings installed. **Restore original Home before uninstalling Family Home.** Never substitute someone else’s `original.json`. If a later setting changed intentionally, review it before restoration; an exact-baseline restoration is not a merge of new preferences.

## 6. Get temporary root and inventory the TV

### The route that actually worked

We used [chris-ritsen/samsung-tv-root](https://github.com/chris-ritsen/samsung-tv-root) **v0.0.12**, source revision `3b97edf3762db7670585d73e29623dc56195bf98`, through its **archive-root** route. The current cached tree was compared with that upstream revision on 26 October 2026. Other repositories’ QN90B/QN90F kernel exploit commands were not the S85D recipe.

The archive route checks the SDB foothold, Samsung .NET capabilities, archive support and runtime. It stages per-run payloads and uses a private mount namespace, then authenticates a root callback. The successful sessions reported UID/EUID/GID/EGID 0 and unchanged original passwd/verification-key hashes, and removed their staging. This does not remove secure boot, all SMACK policy, read-only system mounts, DRM protections or every firmware restriction.

`archive-root probe` performs root acquisition and cleanup. Its name does **not** mean a harmless metadata-only probe. Interrupting it can leave staging behind; read its cleanup evidence before doing another session. Run one session at a time and keep the TV on until it finishes.

### Reproduce the pinned host tooling

Create a separate upstream checkout, outside this repository’s tracked source. Python 3.12+, OpenSSL, GNU Make and the .NET SDK are needed for a source build. Upstream standalone release archives avoid the source-payload build; choose the correct host architecture and verify the release provenance.

```sh
git clone https://github.com/chris-ritsen/samsung-tv-root.git ../samsung-tv-root
cd ../samsung-tv-root
git checkout --detach 3b97edf3762db7670585d73e29623dc56195bf98
python3 -m venv .venv
.venv/bin/python -m pip install -e .
make common-payload
.venv/bin/python -m samsung_tv_root --sdb "$SDB" doctor
```

For a TV proven to have .NET 3.1, upstream documents `make common31-payload` with SDK 6.0.428. Do not build or invoke the QN90B/F kernel routes merely because the archive route fails. Use runtime autodetection first; `--runtime 6.0` or `--runtime 3.1` is an explicit override only after verifying the installed runtime.

```sh
.venv/bin/python -m samsung_tv_root --sdb "$SDB" -o json archive-root probe "$TV_IP"
.venv/bin/python -m samsung_tv_root --sdb "$SDB" -o json archive-root root "$TV_IP" --command 'id; uname -m; cat /proc/self/attr/current'
```

Save the complete JSON results privately. A timing-probe failure, missing authenticated identity, missing cleanup result or wrong firmware is a stop for diagnosis, not permission to loosen the success threshold. Ordinary `sdb shell` can remain closed even after this separate root route succeeds.

### Read-only inventory commands inside an authenticated root session

The command bodies below read metadata; the surrounding temporary-root acquisition still stages files. Repeat `--command` for separate bounded commands rather than a giant output that times out. Keep report files private because process arguments and identifiers can contain personal data.

```sh
id
uname -a
cat /etc/tizen-release
cat /etc/os-release
sed -n '/^Version=/p;/^Model=/p' /etc/prd_info.ini
cat /proc/sys/kernel/random/boot_id
mount
df -h
free -m
ps -ef
systemctl list-units --all --no-pager
systemctl list-unit-files --no-pager
sqlite3 -readonly /opt/dbspace/.pkgmgr_parser.db '.schema package_app_info'
sqlite3 -readonly -header -csv /opt/dbspace/.pkgmgr_parser.db 'SELECT app_id,package,app_component,app_type,app_exec,app_disable,app_onboot,app_autorestart,app_removable,app_package_system FROM package_app_info ORDER BY app_id;'
```

Also collect selected package manifests, service definitions, reverse dependencies, executable locations, SMACK labels, typed voice preferences, relevant unit search paths and existing stop-marker/mask ownership. Inspect `systemctl cat UNIT` and `systemctl show UNIT` before deciding what disabling it will affect.

This is a system/application inventory, not a request to extract viewing history, account databases, Wi-Fi passwords, tokens or other household content. Root capability does not make all of that relevant to cleanup.

## 7. Back up before cleanup

A registry backup and inverse settings plan are **configuration recovery**, not a full firmware image. They cannot guarantee recovery from damage to signed boot/system partitions. We did not erase those partitions, delete package directories, replace system Bash, or alter persistent passwd/verification-key files.

Create a new private run directory per batch, on the computer and on writable TV storage. Save:

| Item | Why |
| --- | --- |
| Exact model, firmware/build, architecture and boot ID | Prevent replay on a different target or silently changed firmware |
| Consistent registry snapshot plus schema and integrity result | Reconstruct selected fields and detect wrong database structure |
| Every selected app’s identity, package, executable and three original flags | Generate narrow apply/undo operations |
| Original typed preferences | Restore `bool`, `int` and `string` accurately |
| Full selected unit definitions and hashes; reverse dependencies | Detect changed meanings or dependent services |
| Existing marker files and mask destinations, ownership/inodes/hashes | Remove only controls this run created |
| Process identity samples, SMACK labels and start ticks | Avoid signaling a reused PID or shared runtime |
| Original native Home baseline and installed launcher version | Retain a path back to Samsung Home |
| Hash-checked copies on the computer | A TV-only backup is insufficient if access fails |

### Consistent SQLite snapshot

The following is a **TV-side root shell recipe**, not a command to run against the Mac filesystem. Choose one run name, record it on the computer, and use it consistently. Only proceed after inspecting the live schema and exact reference build. A directory must be new; do not reuse a failed batch’s backup as if nothing happened.

```sh
set -eu
umask 077
test "$(id -u)" = 0
grep -Fx 'BUILD_ID=T-PTMDDEUC-0090-REL-202605141701' /etc/os-release
D=/opt/usr/share/tizen-cleanup-backups/your-new-run-id
mkdir "$D"
sqlite3 -readonly /opt/dbspace/.pkgmgr_parser.db ".backup '$D/registry.db'"
test "$(sqlite3 -readonly "$D/registry.db" 'PRAGMA integrity_check;')" = ok
sha256sum "$D/registry.db"
```

Create the parent backup directory once if absent, after checking it is an ordinary directory rather than a symlink. SQLite’s backup API is used because copying a live database file without its WAL state can produce an inconsistent backup. Record the snapshot hash before continuing.

Transfer the backup through the authenticated root transport. Retail `sdb pull` can be denied even for readable paths. The pinned archive route returns per-command `stdout` in JSON under `commands`; it does not provide the other model routes’ `--pull` option. One portable method is a root command that prints `base64 "$D/registry.db"`, saving that full JSON privately, decoding only that command’s `stdout` on the host, and comparing the host SHA-256 with the independently recorded TV hash. Keep the payload bounded and retry a read if truncated; never use a partial backup.

The included `tools/extract_backup.py` performs this decode/hash check from a successful archive report. It refuses reports without exactly one matching command result or successful identity/cleanup checks. From the upstream root-tool checkout, save one backup-read result (replace the run name consistently):

```sh
.venv/bin/python -m samsung_tv_root --sdb "$SDB" -o json archive-root root "$TV_IP" --command 'base64 /opt/usr/share/tizen-cleanup-backups/your-new-run-id/registry.db' > ../samsung-tizenos-cleanup/.local/backup-read.json
```

Create `.local/` first on the computer. Return to this project and use the SHA-256 independently read directly on the TV:

```sh
mkdir -p .local/batch-core
python3 tools/extract_backup.py --report .local/backup-read.json --command 'base64 /opt/usr/share/tizen-cleanup-backups/your-new-run-id/registry.db' --sha256 YOUR_64_CHARACTER_SHA256 --out .local/batch-core/registry.db
```

The extractor refuses to overwrite an existing file. Inspect the root command exit status and complete JSON before continuing.

Save preferences, unit definitions and other baseline data too. A registry snapshot alone cannot undo service masks or Home routing.

## 8. Disable selected apps without deleting their files

We changed **three fields** in `package_app_info`, for a reviewed exact list:

| Field | Applied value | Meaning |
| --- | --- | --- |
| `app_disable` | text `true` | Disable the app record |
| `app_onboot` | text `false` | Remove its app-registry boot request |
| `app_autorestart` | text `false` | Remove its app-registry auto-restart request |

These are text values in this schema. They are not universal settings for every Tizen database. A package can contain several app records, and a daemon can also be managed independently by systemd or Samsung’s app framework. Registry flags alone did not stop every existing process.

### Generate an exact, reversible plan locally

Return to the Samsung/TizenOS cleanup repository. Copy your verified snapshot to `.local/batch-core/registry.db`; do not commit it. Start with `profiles/s85d-core.json`, then compare every target’s identity and dependency role with your TV. For another firmware, make a reviewed profile for that device instead of forcing the reference one to pass. For a smaller first batch, copy the profile privately and remove the apps you do not intend to change.

```sh
python3 tools/registry_plan.py --backup .local/batch-core/registry.db --profile profiles/s85d-core.json --out .local/batch-core/plan
```

This tool is **offline only**. It checks schema, trigger absence, unique IDs and package/executable identity; creates a guarded transaction; records backup/profile hashes; and generates inverse SQL from your actual original flags. It refuses an existing output directory. It does not prove live firmware compatibility, inspect systemd dependencies or connect to a TV.

Review `apply.sql`, `restore.sql` and `PLAN.json`. Exercise apply and restore on a disposable copy of your backup, checking that every selected field returns to its original value and unrelated data is unchanged. The included automated planner tests cover drift, missing targets, trigger rejection, SQL quoting, inverse changes and preservation of unrelated records.

### Apply the prepared transaction

Stage the reviewed SQL through SDB to a fresh SDK staging location, then access it from the temporary root session. Verify its hash on both sides. Recheck current model/build, the selected identities and service definitions, and ensure the backup is complete before writing.

Inside the authenticated root session, after setting `PLAN` to the verified staged `apply.sql`:

```sh
sqlite3 -bail -cmd '.timeout 5000' /opt/dbspace/.pkgmgr_parser.db < "$PLAN"
```

The generated SQL starts `BEGIN IMMEDIATE`, checks all preconditions before any UPDATE, changes only the three selected fields and commits. A failed guard with `-bail` stops execution; closing the SQLite connection rolls back the uncommitted transaction. Do not drop the guards to get past a changed registry.

After the database transaction, apply the separately reviewed preferences/markers and stop only identified selected services/processes. Journal each completed stage. If something fails, inspect current state; do not blindly rerun the original apply. A complete “apply” spans several subsystems and is not one atomic transaction across SQLite, vconf and systemd.

The original project used a larger host orchestrator with identity checks, per-stage journals, backups, authenticated temporary-root callbacks, bounded output and recovery plans. Its household-bound runner is not published as a pretend universal installer. The public profile, planner, recipes and native helper provide the reproducible parts; service changes still require target-specific review.

## 9. Voice, ads, recognition and service controls

### Four voice preferences

Read and preserve the exact typed value first, then set the intended value. This is an example TV-side command; use the recorded original value for undo:

```sh
vconftool get db/menu/voice/voice_activated
vconftool set -f -t bool db/menu/voice/voice_activated 0
vconftool get db/menu/voice/voice_activated
```

| Key | Type | Applied value |
| --- | --- | --- |
| `db/menu/voice/voice_activated` | bool | `0` |
| `db/menu/voice/wakeupless_status` | int | `0` |
| `db/si_service/voice_recog_enable` | bool | `0` |
| `db/multi-assistant/prelaunch_mode` | bool | `0` |

This disables chosen assistant/wake-up pathways, with the loss of those voice features. It is not proof that every app with audio permission is incapable of using a microphone.

### Vendor stop-marker mechanism

On the reference build, selected units explicitly check for the **absence** of a file under `/opt/usr/share/systemd/system/`. Creating the matching empty marker prevents their condition from passing on later starts. This is a Samsung unit convention, not standard `systemctl disable` semantics.

For each unit, inspect `systemctl cat UNIT` and verify its actual `ConditionPathExists=!…` clause. Confirm reverse dependencies are understood, hash the definition, and save whether the marker already exists. Refuse symlinks and nonregular files. Create a missing marker without overwriting anything and record its inode/device and empty-file hash. Undo may remove it only if this run created it and those ownership checks still match.

Example, **only after confirming the unit names and condition on your TV**:

```sh
systemctl cat pisa-service.service
systemctl show pisa-service.service -p RequiredBy -p RequisiteOf -p BoundBy -p PartOf -p ConsistsOf
```

Two services share the `pisa-service` marker. Nine distinct markers controlled ten units in the first batch. The table below is the exact mapping used, not an instruction to create files blindly.

| Batch | Unit | Marker filename |
| --- | --- | --- |
| Core | `adagent-service.service` | `pisa-service` |
| Core | `pisa-service.service` | `pisa-service` |
| Core | `canalysis-service.service` | `canalysis-daemon` |
| Core | `com.samsung.tv.bixby-prov.service` | `com.samsung.tv.bixby-prov` |
| Core | `com.samsung.tv.farfieldvoice.service` | `com.samsung.tv.farfieldvoice` |
| Core | `com.samsung.tv.ondevice-voice.service` | `com.samsung.tv.ondevice-voice` |
| Core | `com.samsung.tv.voiceid-service.service` | `com.samsung.tv.voiceid-service` |
| Core | `com.samsung.tv.wakeupless.service` | `com.samsung.tv.wakeupless` |
| Core | `org.tizen.voice-app.service` | `org.tizen.voice-app` |
| Core | `org.tizen.voice-client.service` | `org.tizen.voice-client` |
| Extended | `com.samsung.tv.context-aware-agent.service` | `com.samsung.tv.context-aware-agent` |
| Extended | `com.samsung.tv.context-aware-service.service` | `com.samsung.tv.context-aware-service` |
| Extended | `com.samsung.tv.ghdaemon.service` | `com.samsung.tv.ghdaemon` |

After the guarded registry/preferences/markers stage, stop the reviewed units. Recheck definition hashes and dependencies immediately before stopping. Use `systemctl stop --no-block UNIT` and observe convergence rather than assuming the stop request succeeded.

### Seven runtime-only masks

The extended batch used `systemctl mask --runtime` for the following units after their dependencies and current masks were inspected. Record preexisting links and only unmask links owned by this run. These controls live under `/run` and **do not survive a full reboot**.

- `contents-ui-detector-service.service`
- `contents-recognition-service.service`
- `contents-cognition-service-manager.service`
- `content-grab-service.path`
- `content-grab-service.service`
- `media-analytics-service.service`
- `org.tizen.tv.sp-kpi.service`

Recognition manager, detector and recognition services have related dependencies; the tested extended plan considered the group together. Do not derive a universal safe order from the filenames. The reference root filesystem was read-only and its unit search path did not supply a proven writable persistent replacement. We did not install a per-boot enforcement daemon. Persisting these seven masks remains unfinished work.

### App preloading and TV Plus auto-start

The extended batch changed two representations of the app-preload setting, retaining exact originals for undo:

- `db/was/preload_by_country`: vconf **string** `false`.
- `/opt/dbspace/.webappservice.db`, table `WASConfigTable`, column `RESERVED_18`, JSON path `$.rsp.preloadByCountry`: **string** `false` in the qualified row.
- `db/menu/autorun_tv_plus`: vconf **bool** `0`.

A JSON string `"false"` and JSON boolean `false` are different. Inspect table schema, JSON validity, row identity and existing value before updating. Guard a transaction with an exact row count and original JSON field; make an inverse field update instead of copying an old whole database over live data. Take a separate consistent snapshot of this database. A later Samsung catalog refresh may rewrite the cached value, so verify again; we did not add a watcher that fights updates. TV Plus itself remained installed.

### Process handling and privacy interpretation

A unit showing `inactive` does not prove that a corresponding process cannot exist outside that unit. Conversely, `ActiveState=failed`, `MainPID=0`, `ControlPID=0` and no live control-group process can mean an old recorded failure rather than something still running.

Use two process samples separated by several seconds. Match exact executable paths or package SMACK labels such as `User::Pkg::PACKAGE`, and record each PID’s start tick from `/proc/PID/stat`. Revalidate both identity and start tick immediately before sending any signal. Never kill every `dotnet`, `wrt`, browser worker or shared Samsung app manager by process name.

On the extended batch Gaming Hub respawned despite registry changes and an inactive service. A vendor app-termination request also failed to keep it stopped. We stopped retrying and requested a real cold boot; this remains pending at the evidence cutoff. The public guide does not turn that unresolved result into a successful removal claim.

The `data-service` logger and automation/TIFA components were not broadly disabled: their dependencies and exact role remained unqualified. IACR manifest permissions included screen-related capabilities and Bixby media actions; that is not evidence of actual screen capture or uploading. Whole-TV WAN blocking was not used because the family keeps native online streaming apps. Router isolation or DNS filtering can be a separate choice, but domain lists can break logins/playback and cannot establish complete coverage of traffic to changing endpoints.

## 10. The complete reference target list

These are **app records**, not 82 independent spyware products. Multiple records belong to one package. Descriptions are concise role assessments based on registry names, manifests and the project’s review; they are not observed network-exfiltration claims. The JSON profiles include exact package, executable, component/type and original flags for comparison. Do not assume your TV has the same IDs or paths.

### Core batch: 38 records, cold-boot verified on the reference TV

| App ID | Role and expected loss when disabled |
| --- | --- |
| `adplatform.ADPlayer` | Advertising-player component; disabling can remove in-platform promotional playback. |
| `com.samsung.tizen.samsung-analytics` | Samsung analytics component; selected as optional platform measurement, without claiming a complete traffic analysis. |
| `com.samsung.tv.AccountNudgeService` | Prompts encouraging account use or sign-in; those reminders may disappear. |
| `com.samsung.tv.acr` | Automatic content recognition component; associated recognition/personalization becomes unavailable. |
| `com.samsung.tv.ad-web-framework` | Web advertising framework used by platform surfaces; promotional rendering can be affected. |
| `com.samsung.tv.adagent-service` | Advertising agent service; selected platform ad delivery/coordination is disabled. |
| `com.samsung.tv.adplayer` | Advertising player; ad playback surfaces may no longer work. |
| `com.samsung.tv.alexa-client` | Alexa client/service connection; Alexa voice features are lost. |
| `com.samsung.tv.alexa-fullscreen-app` | Alexa full-screen interface; Alexa visual responses are lost. |
| `com.samsung.tv.bixby-context-client` | Supplies context to Bixby; contextual voice actions are affected. |
| `com.samsung.tv.bixby-promotion` | Promotes Bixby features; its promotional screen is removed from use. |
| `com.samsung.tv.bixby-prov` | Bixby provisioning/service component; setup or operation of Bixby may stop. |
| `com.samsung.tv.bixbycapsuleviewer` | Bixby capsule/result viewer; assistant response cards are affected. |
| `com.samsung.tv.canalysis-service` | Content-analysis daemon; associated analysis/recognition features are disabled. |
| `com.samsung.tv.coba.adagent` | CoBA advertising interface component; associated platform ad UI is affected. |
| `com.samsung.tv.farfieldvoice` | Far-field voice service used for distant microphone interaction; hands-free voice features are affected. |
| `com.samsung.tv.mybixby` | Bixby personal/settings interface; that assistant interface is unavailable. |
| `com.samsung.tv.ondevice-voice` | On-device voice processing; offline/local voice functionality may also be lost. |
| `com.samsung.tv.pisa-service` | PISA service associated with the selected advertising/recognition stack; dependent personalization is affected. |
| `com.samsung.tv.targeted-ad-service` | Targeted advertising service; its ad personalization/delivery path is disabled. |
| `com.samsung.tv.utterance-recommender-app` | Shows suggested voice phrases; voice-command suggestions are lost. |
| `com.samsung.tv.utterance-recommender-core` | Generates or coordinates suggested utterances; assistant suggestions are lost. |
| `com.samsung.tv.vif` | Voice interaction framework; general assistant voice interaction is affected. |
| `com.samsung.tv.voice-instant-app` | Instant voice-assistant interface; associated voice UI is unavailable. |
| `com.samsung.tv.voiceassistant-music` | Music interface for a voice assistant; voice-driven music controls are affected. |
| `com.samsung.tv.voiceid-service` | Voice identity service; speaker identification/personalized voice behavior may be lost. |
| `com.samsung.tv.wakeup-engine-alexa` | Alexa wake-word engine; Alexa hands-free wake-up is disabled. |
| `com.samsung.tv.wakeup-engine-bixby` | Bixby wake-word engine; Bixby hands-free wake-up is disabled. |
| `com.samsung.tv.wakeupless` | Wake-word-free voice interaction component; continuous conversational voice features are affected. |
| `org.tizen.multi-assistant-service` | Coordinates multiple assistants; switching or prelaunching assistants is affected. |
| `org.tizen.pisa-control-service` | PISA control component in the same PISA package; selected personalization/control functions are affected. |
| `org.tizen.stt-client` | Speech-to-text client; voice transcription features are affected. |
| `org.tizen.voice-app` | Voice user interface; assistant screens may be unavailable. |
| `org.tizen.voice-app-service` | Service entry for the voice application; associated voice UI background work stops. |
| `org.tizen.voice-client` | Voice client service; assistant communication/interaction is affected. |
| `org.tizen.voice-onboarding` | Voice setup/onboarding screens; assistant setup is unavailable. |
| `yL49PNFmjW.PromotionApp` | Promotional web application; its promotion surface is disabled. |
| `yL49PNFmjW.service` | Service entry for the same promotional web package; its background promotion work is disabled. |

### Extended batch: 44 records, cold-boot verification pending

| App ID | Role and expected loss when disabled |
| --- | --- |
| `com.samsung.ep.coba.hotel` | Hospitality/hotel interface component (hotel); its hotel-mode menu, channel or alarm behavior is affected. |
| `com.samsung.ep.hotel-popup` | Hospitality/hotel interface component (hotel-popup); its hotel-mode menu, channel or alarm behavior is affected. |
| `com.samsung.ep.hotel-quicksetting-editor` | Hospitality/hotel interface component (hotel-quicksetting-editor); its hotel-mode menu, channel or alarm behavior is affected. |
| `com.samsung.tv.adventure-tpl` | Decorative Ambient/template scene (adventure); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.ambient-sound` | Ambient-mode sound service; decorative ambient audio is lost. |
| `com.samsung.tv.bathtub-tpl` | Decorative Ambient/template scene (bathtub); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.butterfly-tpl` | Decorative Ambient/template scene (butterfly); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.contents-recognition-dbmgr` | Database manager for content recognition; related recognition state management is affected. |
| `com.samsung.tv.context-aware-agent` | Context-aware agent; contextual or personalized TV suggestions/actions are affected. |
| `com.samsung.tv.context-aware-agent-toast-view` | Context-agent toast notifications; related suggestions/notifications disappear. |
| `com.samsung.tv.context-aware-grab-control` | Capture-control component for the context stack; context gathering dependent on it is affected. |
| `com.samsung.tv.context-aware-server-requester` | Network-request component for context services; related server-backed features are affected. |
| `com.samsung.tv.context-aware-service` | Context service; associated context-driven behavior is disabled. |
| `com.samsung.tv.demo-player` | Retail demonstration player; shop demonstration playback is unavailable. |
| `com.samsung.tv.floatingspheres-tpl` | Decorative Ambient/template scene (floatingspheres); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.flowers-tpl` | Decorative Ambient/template scene (flowers); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.forest-tpl` | Decorative Ambient/template scene (forest); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.gaminghub` | Gaming Hub interface; cloud-gaming browsing/hub features are unavailable. |
| `com.samsung.tv.ghdaemon` | Gaming Hub daemon; its process remained unresolved in the latest audit despite registry changes. |
| `com.samsung.tv.ghservice` | Gaming Hub service; related cloud-gaming background functions are affected. |
| `com.samsung.tv.gravity-tpl` | Decorative Ambient/template scene (gravity); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.iacr` | Bixby/media context companion with screen-related permissions; its functions are disabled without assuming actual surveillance. |
| `com.samsung.tv.infinityroom-tpl` | Decorative Ambient/template scene (infinityroom); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.islands-tpl` | Decorative Ambient/template scene (islands); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.journey-tpl` | Decorative Ambient/template scene (journey); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.lightcone-tpl` | Decorative Ambient/template scene (lightcone); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.lightgrid-tpl` | Decorative Ambient/template scene (lightgrid); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.mountain-tpl` | Decorative Ambient/template scene (mountain); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.mountainview-tpl` | Decorative Ambient/template scene (mountainview); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.onelinedrawing-tpl` | Decorative Ambient/template scene (onelinedrawing); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.rotatingtiles-tpl` | Decorative Ambient/template scene (rotatingtiles); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.sand-tpl` | Decorative Ambient/template scene (sand); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.shelteringtree-tpl` | Decorative Ambient/template scene (shelteringtree); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.skippingstone-tpl` | Decorative Ambient/template scene (skippingstone); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.skylight-tpl` | Decorative Ambient/template scene (skylight); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.spring-tpl` | Decorative Ambient/template scene (spring); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.tranquilnature-tpl` | Decorative Ambient/template scene (tranquilnature); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.water-tpl` | Decorative Ambient/template scene (water); this scene is unavailable, not established as telemetry. |
| `com.samsung.tv.window-tpl` | Decorative Ambient/template scene (window); this scene is unavailable, not established as telemetry. |
| `content-grab-service` | Content/screen-grab service in the recognition stack; dependent analysis/capture features are affected. |
| `org.tizen.ep-hotel-alarm` | Hospitality/hotel interface component (ep-hotel-alarm); its hotel-mode menu, channel or alarm behavior is affected. |
| `org.tizen.ep-hotel-channel` | Hospitality/hotel interface component (ep-hotel-channel); its hotel-mode menu, channel or alarm behavior is affected. |
| `org.tizen.ep-hotel-channellist` | Hospitality/hotel interface component (ep-hotel-channellist); its hotel-mode menu, channel or alarm behavior is affected. |
| `org.tizen.ep-hotel-popup-ui` | Hospitality/hotel interface component (ep-hotel-popup-ui); its hotel-mode menu, channel or alarm behavior is affected. |

Do not use a wildcard such as `com.samsung.*` or `*voice*` as a deletion list. The reviewed selection retained accessibility, tuner/HDMI, networking, DRM, security, audio and panel care. Those functions can share runtimes and dependencies with optional features.

## 11. Verify after a real power cycle

### Restart checkpoints: when to turn the TV off or keep it on

| Stage | TV power action | What to confirm before continuing |
| --- | --- | --- |
| Enable Developer Mode or change the developer-host IP | Perform the TV’s requested restart | Developer Mode remains on, host IP is correct, and SDB reports `device` |
| Install computer SDK/extensions or create certificates | No TV power cycle is needed for the computer installation itself; keep the TV reachable if the wizard needs its DUID | Installed extensions and completed signing profile |
| Root acquisition, inventory, backup, cleanup, app installation or native Home change | **Keep the TV on until the current operation and its cleanup finish** | Complete result and staging cleanup; do not interrupt a root session by unplugging |
| After a cleanup batch has finished and been audited | Unplug power for at least 30 seconds, reconnect, turn on, wait about one minute | A changed kernel boot ID, then a new audit and normal family functions |
| After setting native Home/startup | Test Home immediately from a streaming app; separately test a full cold start | Physical Home and startup both behave as intended; retain original Home recovery |
| TV has been “off” overnight or turned on again | Do not assume a full reboot occurred | Compare boot ID; standby can retain the same boot and running processes |
| Extended cleanup using the seven runtime masks | Record the state before a full reboot and audit afterward | Expect those masks to disappear; do not repeat the old full apply transaction |

A longer unplug is not required just because ours lasted roughly **30 minutes**. That was what the owner actually did during the successful core-batch test; the recipe requested at least 30 seconds. A factory reset, Smart Hub reset, remote Power press, computer SDB-server restart and physical TV power disconnect are different operations.

### Our actual sequence and what each step proved

Dates below are based on saved evidence and owner reports. Times shown are **UTC**, not the TV/owner’s displayed local clock. A check timestamp is not necessarily the exact moment the owner clicked a button or removed the power cable; we do not have a complete timestamped record of every physical button press.

| Date/checkpoint | What happened | What was established |
| --- | --- | --- |
| 24 October 2026: Developer Mode setup | Owner enabled the development setup and reported holding Power for about two seconds and seeing a new boot-like display | That report alone did not prove a full cold boot; subsequent connection tests established SDB access |
| 24 October: SDB recovery | Early official-SDB connection attempts failed; a later attempt returned `device` and developer capabilities | Developer transport worked even though retail shell/root flags remained disabled |
| 24 October: temporary root and inventory | Authenticated temporary archive-root access and inventories succeeded; some larger reads required follow-up batches | Root was usable for this build, with per-session cleanup and original-file checks |
| 24 October: first cleanup attempt and continuation | Backup was verified; an unsigned-script execution failure occurred, then the existing batch was continued through the reviewed shell transport | Selected configuration changed; failed/remaining-process findings still required audit, so no new blanket apply was justified |
| Overnight 24–25 October; morning audit | Owner said the TV had been off overnight; the recorded boot ID was unchanged and six selected processes remained | The overnight off period was not a verified kernel restart |
| 25 October: explicit physical disconnect | Owner reported unplugging the power cable for roughly 30 minutes, reconnecting, turning on and waiting about a minute | A later verification could test a genuine new boot rather than assumed standby behavior |
| 25 October, verification completed about 11:18 UTC | New boot ID; 38 selected app records disabled; four voice preferences off; nine markers; ten units inactive; zero selected processes in both samples | The **core** cleanup passed cold-boot verification |
| 25 October: owner’s functional check | Owner confirmed that picture, sound, remote, Live TV and their usual streaming apps worked | Daily functions were checked after the core cleanup, not inferred from process counts |
| 25 October, 11:39 UTC setup check | Owner had manually completed the Mac SDK installer; base SDK 10.0 was present, certificate extension/manager still absent | The main installer alone was not sufficient for signing |
| 25 October, 11:52 UTC extension check | TV Extensions 10.0.0, Samsung Certificate Extension 2.0.75 and Certificate Manager 1.3.11 were present | Signing software was installed; certificate creation still had to be completed |
| 25 October: certificate wizard | Owner created the Samsung TV profile, completed author/distributor issuance, clicked through completion and showed the populated profile | Our own Samsung-issued signing profile existed; no unrelated certificate provider was used |
| 25 October, signing run beginning 12:13 UTC | Owner ran the local signing command in Terminal | Signed package and matching contents/profile certificates were recorded; independent cryptographic verification was a separate subsequent check |
| 25 October: offline signature checks | Both XML signatures and referenced app contents were checked; tampered payload/signature tests were rejected | Signing validation went beyond finding two XML files in a ZIP |
| 25 October, install run beginning 12:26 UTC | SDK installed and launched Family Home 0.3.0; owner confirmed its screen on the TV | App installation worked; physical Home still used Samsung Home at that stage |
| Later 25 October | Family app/layout updates, CleanFrame-based 0.5.x UI, launcher rollback testing and native Home apply/restore/reapply were performed; owner confirmed Home from a stream opens Family Home | Physical Home routing worked, independently of a new cold-boot test |
| Later 25 October: extended cleanup | 44 additional records and related controls were changed; Gaming Hub respawn persisted and seven masks were only runtime-scoped | This batch was **not** equivalent to the already verified core batch |
| 26 October: owner turned TV on and live audit ran | Current device address was reidentified; 82 target records stayed disabled, but boot ID was still unchanged and one Gaming Hub process remained | Another reported power-on was not proof of a new kernel boot; extended cold-boot durability remained unverified |
| 26 October: requested follow-up power cycle | Owner was asked to unplug/reconnect and confirm the TV was back on | This follow-up is **pending at the guide’s evidence cutoff**, not a completed action |

This is a sanitized implementation sequence, not the private command-by-command journal. It preserves the important setup/restart decisions while omitting household identifiers, credentials and raw operational backups.

A successful command is not the same as a successful cleanup. Record these checks for the same TV and run:

1. Database integrity is `ok`. Each chosen record has the three desired flags; unrelated records are unchanged except for separately understood normal OS activity.
2. Every typed preference reads back exactly. Marker files still have the expected ownership/content and unit conditions still reference them.
3. Each selected unit has no live MainPID, ControlPID or control-group process. Record failure states rather than clearing them to make the report look clean.
4. Two process samples find no selected executables/packages; if a process remains, name it and mark the batch incomplete.
5. Temporary-root staging was cleaned and original system-file hashes are unchanged.
6. Family Home, Samsung Settings/recovery, physical Home, remote navigation, Live TV, HDMI, sound, subtitles/accessibility, casting and family streaming apps work.
7. Unplug the TV’s power cable for at least 30 seconds, reconnect, turn it on and wait about a minute. Compare `/proc/sys/kernel/random/boot_id` before/after; standby can leave the same boot ID.
8. Rediscover/check the TV address, reconnect SDB and repeat the audit. Expect runtime-only masks to be gone. Any new per-boot reapplication needs its own baseline and journal; do not replay an old full cleanup transaction.

The reference core batch passed a power disconnect and these owner functional checks. The later 44-entry batch had not passed a new cold boot at the evidence cutoff. The newer launcher’s specific RTVE/Movistar playback and cold-start behavior still deserve a fresh family acceptance check.

For performance measurements, define a repeatable starting state and record at least several trials: cold boot to usable picture, Home-button latency, launcher startup, app cold/warm launch, memory and selected background CPU. Do not compare a standby wake with a true cold boot or call a subjective improvement a measured multiplier.

## 12. Undo and recovery

Keep recoveries separate: **app preferences**, **launcher version**, **native Home assignment**, **registry/preference cleanup**, and **runtime service controls** are different layers.

- **Hide/reorder changes:** use launcher settings or restore its own saved local preference state. The app’s current key is `family-home.cleanframe.v1`; the older `family-home.settings.v1` was retained for rollback. Do not delete browser storage wholesale just to move a card.
- **Launcher update:** retain the prior source and signed widget using the same package/author identity. Reinstall/relaunch the previously working version. A different author certificate can prevent an in-place update. Uninstalling can remove app data; it is not a casual first troubleshooting step.
- **Home routing:** use `native-home/run.py restore` with your original sealed baseline and correct TV. Query the result and test the physical key. Restore this before removing the launcher. Never delete Samsung Home or Settings as “bloat.”
- **Registry:** execute your generated `restore.sql` only after comparing the live selected records, model/build and backup hash. It restores the three original fields for the selected rows, retaining unrelated changes. Do not copy an old entire registry over a live, changed database.
- **Preferences:** restore the saved typed values. Stop on unexplained drift rather than replacing an intentional later setting.
- **Markers:** remove only markers your run created, after verifying ownership/inode/hash and original absence. Leave preexisting controls alone.
- **Runtime masks:** unmask only the exact links your run created; retain any masks that existed before. A cold reboot normally clears runtime masks, but it does not necessarily restore database flags or persistent markers.
- **Processes:** after restoring configuration, restart only units that your baseline showed should be active, with dependencies reviewed; otherwise use a controlled full restart and inspect normal startup.

Our incremental private cleanup guard expects Family Home to remain assigned. In that sequence, restore the incremental cleanup before changing native Home. A friend’s orchestrator must document its own ordering constraints.

A factory reset is not a tested universal undo mechanism for these changes. It can remove accounts, apps and settings, restore preinstalled content and complicate access. Firmware flashing/downgrading and full system image restoration are outside the verified recovery methods here. A private project ZIP is a backup of host work, not a bare-metal TV recovery image.

## 13. Problems we hit and how we diagnosed them

| Symptom | What it meant in this project | Useful next action |
| --- | --- | --- |
| Port 26101 open but SDB fails | Network reachability was not sufficient; the host helper/connection state needed attention | Check correct TV address, developer-host IP and official SDB state |
| SDB helper reports server trouble | Local host SDB state, distinct from a TV root failure | Inspect devices; if appropriate restart the host SDB helper, then reconnect |
| `intershell_support: disabled` | Normal retail restriction | Use the separately qualified archive route; do not claim official shell access |
| A 2-second timing probe missed a threshold narrowly | Root foothold was not confirmed by that run | Preserve evidence and retry a clean single attempt; do not force success by relaxing checks |
| `the file is NOT signed` on an uploaded shell script | Samsung UEP refused executing the staged file directly | Our reviewed transport passed the verified script bytes to the existing shell via stdin; it did not disable UEP globally |
| `ActiveState=failed`, both PIDs zero | Earlier failure status can remain after the process exits | Inspect cgroup/process identity, not only the status string |
| Six processes remained after the first apply | Configuration had changed but old processes were still running | Cold boot and audit; the original batch then passed with zero selected processes |
| Gaming Hub returned after termination | Samsung’s framework could respawn it independently | Stop repeated killing; inspect boot behavior and exact launch source |
| “TV was off,” but boot ID unchanged | Standby was not a kernel restart | Physical unplug/reconnect and compare boot IDs |
| Old TV IP times out | DHCP address changed | Reidentify by model and known private device identity; do not target an unknown new host |
| Home opens Samsung UI | Installing a launcher does not assign the Home operation | Follow separately qualified native routing and verify the physical key |
| SDK installed but cannot sign | Samsung TV/signing extensions or profile may be absent | Check Package Manager, TV certificate profile, DUID and certificate validity |
| `Resume: command not found` | Explanatory prose was pasted into the terminal | Paste only the command inside the code block |
| Giant inventory is partial | Large outputs/session time limits | Split into bounded batches and explicitly fill gaps |

Host SDB recovery, when appropriate:

```sh
"$SDB" devices
"$SDB" kill-server
"$SDB" start-server
"$SDB" connect "$TV_IP:26101"
"$SDB" -s "$TV_IP:26101" get-state
```

This restarts the computer’s SDB helper and affects its other SDB connections. Do not run it in parallel with an active root/backup/install session. An interrupted root session must have its staging and cleanup reviewed before another attempt.

## 14. Every original GitHub repository

All six repositories originally supplied by the owner are listed here. “Tested” below names the actual test: a syntax check, local build, mocked test or author claim is not a successful TV installation. Revisions are the reviewed snapshots; consult upstream for later changes and requalify before executing new code.

| Repository | What it offers | What we actually established | Fit for a friend |
| --- | --- | --- | --- |
| [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv) | Primarily Android/Google TV ADB debloating and launcher work; Samsung/Tizen notes | Seven Samsung documentation tests passed on the older tested snapshot; Android tooling was not an applicable Tizen cleanup route | Useful comparison and documentation; Android ADB removal commands do not become Samsung SDB commands |
| [jss8649/quiet-tizen](https://github.com/jss8649/quiet-tizen) | QuietHome native launcher, root-assisted targeted cleanup and rollback for a qualified Samsung model | 19 local tests passed; stock identity guard refused the S85D; native build then lacked Tizen.NUI.dll | Strong design/reference for guarded cleanup; independently map the real TV rather than transplanting its stock package profile |
| [tdudek/samsung-remote-models-2014-and-newer](https://github.com/tdudek/samsung-remote-models-2014-and-newer) | Older Samsung PIN-pairing/encrypted remote-control protocol | 15 JavaScript syntax checks; import lacked node-fetch; S85D legacy `/ms/1.0/` returned 404; no pairing performed | Remote-control research, not root, debloat, firmware replacement or full inventory |
| [simbasjungles/free-my-tv](https://github.com/simbasjungles/free-my-tv) | Alternative launchers, with Android plus separate Tizen/webOS web builds | Tizen unsigned widget built (741,260 bytes in that snapshot); five JS syntax checks; unsigned-install guard refused installation | A real alternative launcher to assess; requires your TV signing/installation and does not automatically replace native Home or remove system telemetry |
| [chris-ritsen/samsung-tv-root](https://github.com/chris-ritsen/samsung-tv-root) | Archive-root route; model-specific kernel routes; optional controller, remote/control tools | Archive-root repeatedly worked on our S85D with authenticated root and cleanup checks | The root route actually used. Pin the reviewed code, qualify prerequisites, and keep model-specific kernel routes separate |
| [nthnclrk/CleanFrame](https://github.com/nthnclrk/CleanFrame) | MIT web launcher, Dock/List layouts, local preferences, offline materials/assets; native Home helper research | Actual source foundation for Family Home 0.5.x; local UI checks, TV installation and owner-confirmed native Home result | Best starting point for the visual experience shown here; keep its credits and create your own identity/certificates/baseline |

### Reviewed revisions and qualifications

**CleanYourTV:** test revision `cc4c7c596c089c4a16f39480fef75c3349469bf9`; later README review `204143007f0bebfb14d6ef001a32e5836b1c90b5`. Do not attach the older test result to every later commit. The Samsung notes are under `docs/devices/samsung-tizen.md`.

**Quiet Tizen:** `cf518d7a9278dca7990e27756218258e44044a29`. Its reference was `UN75U8000FFXZA`, firmware `T-KSU2EFAKUC-0090-1300.9`. Its 54 app IDs span groups and several records per package; they are not 54 proven independent trackers. Its root doctor stages an exploit path, so it should not be described as a read-only probe. We borrowed the approach and independently qualified the S85D targets. The “3× faster” social-media statement is not our measured result.

**Samsung Remote:** `4b8824a271a65b2653b7d7cd39eb38a2d195ee2d`. Its historical H/J-series assumptions did not match the S85D endpoint used in this project. A successful syntax check does not modernize that protocol.

**Free My TV:** build-tested `aa34335d25fa2224053d1bb16851e4522a6bbeb0`; later README review `57ea46051fc9dc3201da425f858ef2768f1cc1f2`. Its optional widgets/integrations can contact services such as TMDB, Open-Meteo, Binance and Watchmode. Review those if your priority is an offline launcher. Android/TCL performance numbers are not Samsung/Tizen measurements. We did not install this launcher on the reference TV.

**Samsung TV Root:** `3b97edf3762db7670585d73e29623dc56195bf98`, v0.0.12. A requested comparison on 26 October 2026 found that all 122 cached tracked files matched that upstream revision. The author describes blocking their TV from the internet and using an external Arch Linux computer. **The published repository does not supply a telemetry-disable package list comparable to Quiet Tizen’s.** Its optional UEP disabling changes execution protection, not telemetry. Its host controller reacquires access but was not installed here; permanent-root work remains stopped. Screenshot/control APIs are optional tool capabilities, not evidence Samsung uploads screenshots from this TV.

**CleanFrame:** `fa537d1892b71d2de2bf94c24cbff3812e9f70d5`. Its original reference was `QA55LS03DAWXXY`, firmware `T-PTMDUABC-0090-2130.0`, Tizen 9. Our S85D native helper has its own firmware/build guard; do not run an upstream reference-device helper unchanged on another TV. Our adaptation preserves the real upstream UI rather than recreating a rough imitation, adds Spanish family services, compact app grouping, square Apps/vertical +, sizing/reordering and HBO’s preference migration. Upstream’s own test counts remain upstream claims, distinct from our tests.

## 15. Other projects and replacement-OS limits

These were discovered during research, rather than all being original owner-supplied repos. They are useful leads, not additional verified S85D installations:

| Source | Why look at it | Boundary |
| --- | --- | --- |
| [Samsung/tizen-agent-skills](https://github.com/Samsung/tizen-agent-skills), reviewed `0ea54cbcadedf3ff59f264a147019cb65c61e92d` | Official SDK/SDB development patterns | Read as a source; not installed as a skill in this project |
| [splitcipher/couchroot](https://github.com/splitcipher/couchroot), reviewed `83906b468836869933012da03a4018fb339462b3` | S90D minimal launcher/native-Home integration notes | Related research, not the complete tool live-tested on our S85D |
| [levkropp/samsung-tv-root-untethered](https://github.com/levkropp/samsung-tv-root-untethered), reviewed `2b0629381b3eaf5a78f84332d630d6d4b10681e7` on `untethered-boot-agent` | Q60B/Tizen 6.5 boot-agent experiments | Review only; different firmware family and permanent-root direction not pursued |
| [helalaou/AeroTizen](https://github.com/helalaou/AeroTizen) | Root-free alternative launcher | Home-button/platform limitations still need checking |
| [andrearicci93/vetro](https://github.com/andrearicci93/vetro) | Privacy/debloat dashboard and model compatibility reports | Different model reports are not proof for this exact build |
| [reisxd/TizenBrew](https://github.com/reisxd/TizenBrew) and [TizenBrewInstaller](https://github.com/reisxd/TizenBrewInstaller) | Homebrew application/module ecosystem | Review app permissions and installation requirements; not a new kernel/OS |
| [Apps2Samsung/Apps2Samsung](https://github.com/Apps2Samsung/Apps2Samsung) | Samsung app installation tooling | App delivery is separate from root and Home routing |
| [leanbitlab-org/LtvLauncher](https://github.com/leanbitlab-org/LtvLauncher) | Additional launcher design reference | Android launcher, not an installable Tizen package |

A custom HTML/CSS/JavaScript launcher can substantially change the TV’s feel without changing the kernel. You can add family profiles, configurable app groups, a simpler Live TV path, favorites, local wallpapers and remote-friendly navigation. Launching an installed app is different from integrating its private catalog, playback or account data; use supported APIs and account for content-provider restrictions.

Replacing all of Tizen with Android/Linux would require a compatible boot chain, display/audio/tuner/network drivers, remote/power management and usually DRM support. None of the reviewed projects supplied a verified drop-in OS replacement for this S85D. Temporary root is not evidence that arbitrary firmware can boot. An external HDMI computer/streaming box with the TV’s network disconnected is a separate architectural option, with its own UI, privacy and remote-control tradeoffs; it is not what our native-app household chose.

## 16. Keep a local project memory

The original project maintained a local corpus, typed findings, sources, search records, graph links, lexical/semantic retrieval and a generated chronological `log.md`. This made it possible to reuse research and distinguish earlier failed attempts from later successful checks. The private corpus is not published, because it contains household/device evidence.

A new installation can reproduce the workflow without copying those records:

```text
.local/
  inventory/                 private TV metadata and exports
  runs/RUN_ID/               report, backup hashes, plan, undo and results
  certificates/              private or separate encrypted storage; never Git
  memory/
    sources.jsonl            URL, revision, retrieved_at, local snapshot/hash
    searches.jsonl           query/URL, tool, UTC, result URLs, learned, limits
    facts.jsonl              claim, status, observed_at, evidence, supersedes
    events.jsonl             command/file/action facts and exact times
    graph.json               nodes and evidence/supersedes relationships
    index.sqlite             searchable text index, optionally embedding index
    log.md                   concise generated factual journal
```

Keep raw facts append-only. Use statuses such as `observed`, `owner_constraint`, `source_claim`, `hypothesis` and `review_result`. Record a command’s start/end/exit code and nonsecret arguments. Record the files it changed and their hashes. Store long request details in a separate JSON file and reference it. Never log passwords, private keys or authentication tokens; a secret being local does not make a public commit private.

When asking someone to run a command, record `instruction_issued` with `execution_confirmed: false`. Later append the actual result. “Please unplug the TV” does not become “TV cold-booted” until evidence confirms it. An old inventory is not current live state. Link a superseding finding instead of silently rewriting the old one.

Search memory before repeating web research. For every external read, including failures, record exact query/URL, retrieval time, tool, result URL, snapshot when available, what was learned and what remains uncertain. A saved GitHub source does not prove upstream is unchanged; pin the commit and refresh deliberately.

For retrieval, begin with full-text search and explicit graph edges; add local embeddings or an LSA/semantic index only if useful. Search matches are pointers to evidence, not proof. Record which index/model generated a similarity result and rebuild when sources change. The original journal is project-scoped, not OS-wide tracing, and cannot reconstruct every command that happened outside it.

See `memory/README.md` for starter record shapes. This public project ships a template, not the original private semantic-search database.

## 17. What a future maintainer should do next

1. Record the new TV’s exact hardware/firmware, family needs and current features.
2. Install/qualify the launcher independently before system cleanup. Preserve its app identity and author certificate for updates.
3. Qualify native Home only on an understood build; retain and test the original assignment.
4. Compare the core profile with live records; back up, generate guarded inverse changes, and test a small batch.
5. Validate after a true cold boot, not a standby wake. Treat respawn and missing masks as unresolved work.
6. Review the extra context/recognition/Gaming Hub group separately. Seven runtime masks need a deliberately designed persistent/per-boot mechanism if desired; that was not completed here.
7. Do not promise “zero spyware,” guaranteed speedups, permanent root or universal compatibility. State the measured result and remaining limits.
8. Update this guide, compatibility matrix and source pins only from new evidence. Keep public code separate from private operational reports and backups.

The result worth reproducing is a usable, recoverable family TV: a calm launcher, chosen optional platform components disabled, working native apps and a documented route back. The fastest reliable path is to reuse the reviewed approach while rebuilding the identity, backup and evidence for the new television.
