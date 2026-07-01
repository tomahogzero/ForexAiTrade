# ForexAiTrade Codex Working Rules

Last updated: 2026-07-01

## Standard Workflow

Before starting a checkpoint:

```powershell
git checkout main
git pull origin main
git status
```

If `main` is dirty and pull would overwrite local user files, do not clean, revert, delete, or stash without explicit approval. Create an isolated worktree from latest `origin/main` instead.

Create a checkpoint branch:

```powershell
git checkout -b research/checkpoint-<letter>-<short-topic>
```

Do not commit directly to `main`.
Do not merge to `main`.
Open a Draft PR after finishing when the checkpoint workflow calls for publication.
Do not mark a PR ready for review unless explicitly asked.

## Permanent Guardrails

- Do not enable live trading by default.
- Do not optimize parameters unless explicitly allowed.
- Do not increase lot or risk.
- Do not claim profitability.
- Do not add martingale.
- Do not add uncontrolled grid recovery.
- Do not add recovery lot multiplication.
- Do not bypass RiskManager.
- Do not force broker minimum lot if it violates risk budget.
- Do not run MT5 unless the checkpoint explicitly requires it.
- Do not kill unrelated `terminal64.exe` processes.
- If running MT5, only stop the process started by the runner.
- Keep execution status separate from strategy performance.
- Losing valid reports are still `execution_status=PASS`.

## Documentation-Only Work

For documentation-only checkpoints:

- Do not change EA/source code.
- Do not change presets.
- Do not run backtests.
- Do not run MT5 Strategy Tester.
- Update docs only.
- Compile is not required unless MQL5 source changes.

## Artifact Audit

Before commit, confirm no forbidden artifacts are staged:

- `.ex5`
- `.pyc`
- `__pycache__/`
- `.zip`
- `.agents/`
- `.git/`
- temp/cache/log files
- machine-specific config files

Use explicit staging, for example:

```powershell
git add docs/ai
```

Avoid `git add -A` in a mixed worktree.

## PR Review Expectations

Every PR should state:

- scope
- changed files
- whether compile was required
- compile result if applicable
- whether MT5 was run
- artifact audit result
- guardrail confirmation
- no profitability claim

## New Chat Recovery Procedure

In a fresh Codex chat:

1. Read `docs/ai/context.md`.
2. Read `docs/ai/current-status.md`.
3. Read `docs/ai/working-rules.md`.
4. Read the latest checkpoint docs relevant to the request.
5. Check `git status`, current branch, and remote.
6. If local root is dirty, isolate work in a clean worktree from `origin/main`.
7. Keep changes scoped and auditable.
