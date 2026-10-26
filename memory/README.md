# Private project memory starter

Create `.local/memory/` for your installation; it is ignored by Git. The original household corpus is not part of this repository. These are record shapes, not fabricated historical events.

Store one JSON object per line. Use actual UTC timestamps at observation time and stable IDs for evidence links.

```json
{"id":"event:unique","occurred_at":"ACTUAL_UTC_TIME","kind":"command_finished","executable":"python3","args":["tools/project.py","check"],"exit_code":0,"evidence":["relative/private/report.json"]}
```

```json
{"id":"source:unique","url":"SOURCE_URL","upstream_revision":"COMMIT_OR_DATE","retrieved_at":"ACTUAL_UTC_TIME","snapshot":"relative/private/source.md","sha256":"ACTUAL_DIGEST"}
```

```json
{"id":"search:unique","query":"EXACT_QUERY_OR_URL","tool":"TOOL_USED","occurred_at":"ACTUAL_UTC_TIME","results":["RESULT_URL"],"learned":"Supported finding","limitations":"What this read cannot establish"}
```

```json
{"id":"fact:unique","status":"observed","observed_at":"ACTUAL_UTC_TIME","text":"Specific finding","evidence":["event:unique"],"supersedes":[]}
```

Use separate statuses for `source_claim`, `hypothesis`, `owner_constraint` and `review_result`. A proposed command is an `instruction_issued` event with `execution_confirmed: false`, not a success event.

Generate `log.md` from events: timestamp, action/command, exit status and evidence path only. Keep interpretation in findings. Do not rewrite old entries; add corrections or superseding evidence. A local full-text index can search records; graph edges link sources, findings, events and superseding claims. Optional local semantic indexing should retain model/index metadata and point back to the original evidence.

Logging is project-scoped. A wrapper cannot reconstruct older commands it did not observe. Never capture passwords, keys, tokens or unredacted account payloads just for completeness.
