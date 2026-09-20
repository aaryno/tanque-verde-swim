# Golden-path spike — what was filed, what was not, and why

**Date:** 2026-09-20
**Worker:** `lane@tv-swim` pool worker, order `f052f27b-3abf-4ba4-8207-778a6ac2b6ca`, attempt `47451d44-7704-433c-85a1-851ddca16d85`, epoch 1
**Conversation:** `78a112ae-5dde-4768-945e-eaa41cc0a325`
**Source material:** `/Users/aaryn/workspaces/tv-swim/docs/startup-friction-2026-09-20.md` (215 lines; commits `8a7b07e` + `b693fe3` on that repo's `main`)

---

## What was filed

**ONE issue:** [swimlane4/hearth#3817](https://github.com/swimlane4/hearth/issues/3817) —
*"SPIKE: the golden path from 'Aaryn names a project and a repo' to a working coordinator — what the one provisioning step should be, measured against a real fresh birth (~35 tool calls, ~70k context)"*
Label: `hearth` (verified present via `gh label list --repo swimlane4/hearth` before filing).

**ONE cross-reference comment:** [swimlane4/agent-commander#1498 (comment)](https://github.com/swimlane4/agent-commander/issues/1498#issuecomment-5751965770)

No code was modified, no PR opened, no BOARD claim posted, no second issue filed.

### Why swimlane4/hearth and not agent-commander

The code, #3807 and #3808 live on `swimlane4/hearth`; that is where the work would happen. A Hearth spike filed only on agent-commander would be invisible to `lane@hearth-dev`. One filed only on hearth would be invisible to this workspace's planning thread, whose CLAUDE.md requires tv-swim work to be findable from #1498. The cross-reference comment is what keeps both true without duplicating the issue.

### What the spike answers

- **The central question** — the one provisioning step. Headline finding: this is a **composition problem, not a construction problem**. Six of eight pieces already ship (`createWorkspace()`, `resolveCoordinatorLane`, `coordinatorBirth.ts`, `coordinatorContext.ts`, the enrollment route, and lane binding as a `coord:note` side effect). Two are genuinely missing: *ask-for-and-clone-the-code-repo* and *record-a-canonical-objective*. Nothing calls the existing six in sequence.
- **Q1** one-line fixes (bind `live_sessions.lane` at spawn; call the existing uuid validator at the HTTP boundary; name `session.jsonl` in §0; default `pool:lane --show` to the caller's lane) vs. design gaps (a new Conversation cannot write durable state at all; the repo is never asked for).
- **Q2** yes, workspace creation should require a code repo — with the full causal chain from `lib/workspaceCreate.ts` having no repo input through to a lane pointed at a directory with no code, and a stated distinction from #2480 so the two do not collapse into one field.
- **Q3** `conversation_state_entries` is the right home; enrollment-at-creation is the preferred fix; do not build a coordinator-local to-do store.
- **Q4** three new rows for COORDINATOR.md §0's routing table plus a partial-pack branch, with the measurement `grep -c 'session.jsonl' docs/hearth/COORDINATOR.md` → 0.
- **Q5** ~35 calls / ~70k, set against §0's own 2026-08-30 incident (~12 calls / 69k), with an acceptance test: ≤3 tool calls, ≤10k context, zero hand repairs, zero minted credentials.

### Evidence discipline

Every code claim was re-verified against the **serving build** — `/Users/aaryn/workspaces/swimlane4/hearth` @ `84b15da0e` (2026-09-20T13:24:32Z) — not against the friction log and not against `~/workspaces/hearth`. This is the log's own §C item about the serving build applied to itself.

One claim was **sharpened** rather than repeated. The log said the `portfolio.track` 500 happens because "the route and the ledger both declare it `string`". Verified: `lib/coordinator/portfolioOpArgs.ts:89` already types `objective_entry_id: "uuid"` and lines 208-209 already refuse a non-uuid by name. The HTTP route at `app/api/master-portfolio/ops/route.ts:126,135` simply does not call that validator. That is a stronger and more actionable statement, and it is the single best piece of evidence for the "one-line fix vs. design gap" question. (The defect itself is owned elsewhere — cited as evidence, not re-filed.)

---

## What was deliberately NOT filed, because it is already owned

`lane@hearth-dev` accepted the handoff of the friction log's defects and is folding them into #3808 and #3807, and amending `lane@master`'s existing "portfolio ops 500 empty" record rather than opening a second one. Re-filing any of these would be the exact duplication this workspace's RULE 2 exists to prevent.

| Item | What it is | Owner |
|---|---|---|
| A1 | `live_sessions.lane` NULL — every `HEARTH-OP` refused `caller_unresolved` before claim | `lane@hearth-dev` → #3808 / #3807 |
| A2 | Context pack partial — `.hearth/context/` held only `system/session.jsonl` | `lane@hearth-dev` → #3808 / #3807 |
| A3 | Lane `source_repo` pointed at the docs workspace, not the code | `lane@hearth-dev` → #3808 / #3807 |
| B2 | `POST /api/master-portfolio/ops {op:"track"}` → HTTP 500, zero-length body | `lane@master`'s existing record, being amended |
| B4 | `GET /api/conversations/:id/soul` returns the HTML app shell, not JSON | `lane@hearth-dev` → #3808 / #3807 |

#3817 **links** to these and uses the same incidents as evidence for design questions. It asks no one to fix a bug twice, and it says so explicitly in a table near the top so a reader cannot mistake it for a re-file.

### Duplicate check performed before filing

```
gh issue list --repo swimlane4/hearth --search "coordinator bootstrap enrollment conversation startup" --state all --limit 40   → empty
gh issue list --repo swimlane4/hearth --search "golden path" --state all --limit 20                                            → #3394, #3383, #3417 (none is this spike)
gh issue list --repo swimlane4/hearth --search "spike provisioning workspace repo clone lane" --state all --limit 20            → empty
gh issue list --repo swimlane4/hearth --search "workspace creation repo clone" --state all --limit 15                           → #2480 (adjacent, linked, not a duplicate)
gh issue list --repo swimlane4/agent-commander --search "golden path startup friction spike" --state all --limit 20             → empty
gh issue list --repo swimlane4/agent-commander --label tv-swim --state all --limit 20                                           → #1498 only
```

An empty `gh issue list` exits 0 whether the search genuinely matched nothing or the query was wrong, so the silence was corroborated rather than trusted: `gh auth status` confirmed the account, and a known-good `gh issue list --state open --limit 3` returned #3816/#3815/#3814 from the same repo. The `hearth` label was confirmed to exist with `gh label list` before `gh issue create`, because `create` errors on a missing label while `list` prints nothing and exits 0.

---

## Friction items judged too weak to carry as spike findings

### B5 — "my `HEARTH-OP` probe produced *nothing*"

**Excluded as a finding; carried only as a correction.** The log's own Corrections §C1 retracts the strong version, and that retraction is the honest record. A well-formed unfenced column-0 `HEARTH-OP portfolio.read` was emitted and `pool:op-census` reported "0 HEARTH-OP declarations emitted" over a window it said reached the window start across 327 transcript events. But the declaration **is** present in the durable transcript at `.event.summary` — and `summary` may be a derived or truncated field, so the raw output row `lib/pool/coordinatorOpWindow.ts` scans may legitimately not exist for a Hearth-launched coordinator.

Whether that is a scanner gap or an emission that never produced a scannable row is **not established**, and the log's author says plainly they should not have implied the first. A spike question of the form "is this a hole in #2575's guarantee?" cannot be answered from one unreplicated observation with two live readings, and asking it as though it could would invite exactly the dismissal the spike is trying to avoid. It appears in #3817 under "Corrections carried", explicitly marked as not claimed.

### "The portfolio holds 22 objectives, none about swimming"

**Excluded as stated; the surviving friction was reframed.** The original sentence was a machine-wide read reported as though scoped to this Conversation — it is *Master's* portfolio (`f8452d2c-…`, lane `master`, epoch 15), read via `ops:portfolio-coverage`, which reads the store. Master flagged it independently, because 22 objectives inside a minutes-old Conversation is what a context bleed looks like. It was not one: `GET /api/conversations/78a112ae` returns `durable_state.items: []`, `state_entries: 0`.

What survives is not the count but the **tool shape**: a coordinator's only convenient portfolio read has no "mine" scoping, which makes reporting someone else's state as your own the *default* mistake rather than a careless one. That is carried in #3817's secondary-frictions section, with the incident as its evidence.

### Auto-renewed executive leases as evidence of liveness

**Struck entirely, per Corrections §C4.** Lease renewal is automatic and says nothing about whether a Conversation is doing useful work or is correctly configured. It is not friction and it is not evidence; it is a misreading, and repeating it would weaken everything around it.

### `runtime UNDECLARED`

**Kept, but demoted to a secondary friction.** It did not block launching. `pool:master-conversation --show` reports it as a defect-shaped fact with no guidance on whether a coordinator should act on it — the friction is the missing guidance, not the undeclared runtime, and that is too small to carry as a spike question.

---

## Constraints observed

- ONE GitHub issue created. ONE cross-reference comment posted.
- No repository code modified. No PR opened, no merge, no publish, no BOARD claim.
- The friction log's Corrections section was read in full and its corrections — not its original claims — are what the spike carries.
