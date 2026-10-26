# Contributing

Preserve the existing CleanFrame-based visual system, remote focus, cached rendering, public assets and local-only network policy. Keep runtime JavaScript compatible with the qualified TV engine. Do not add telemetry or CDN calls without making the behavioral change explicit.

Run `npm ci`, `npm run check`, `npm test`, `python3 -m unittest discover -s tests -p 'test_*.py'` and `npm run build`. For interaction changes, also inspect a 1920×1080 browser preview and test D-pad focus; mocked DOM tests do not replace visual or physical-TV checks.

Keep your own stable app identity and author certificate. Create an independent identity once for a separate installation. Never change a released identity silently. Do not publish signed widgets, private keys, certificate profiles, device baselines or raw household evidence.

System changes must be based on a fresh exact-device baseline, a reviewed scope, guarded writes, inverse operations and post-restart verification. Do not weaken a model/build guard merely to make an unsupported TV pass. Label source claims, hypotheses, local tests and live-device observations separately.

Third-party assets retain their original terms. Retain CleanFrame’s MIT attribution and all bundled notices. Do not include proprietary fonts. Keep private files in ignored `.local/` or separate encrypted storage; audit the staged Git tree before publishing.
