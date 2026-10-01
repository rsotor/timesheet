# Contributing

Thanks for helping. This is a small tool: keep changes small and focused.

## Setup

```bash
uv sync --extra dev
uv run pytest -v
```

## Rules

- **Never commit real data**: no real IDs, company names, tokens or emails in code, tests, screenshots
  or docs. Use `xxxx`, `acme`, `1234`.
- Tests must not call the real APIs: mock `requests` like the existing tests do.
- If you add a dependency, commit the updated `uv.lock` (CI runs `uv sync --locked`).
- English for code, messages and docs.

## Pull request titles

PRs are squash-merged, so the PR title becomes the commit message and the CHANGELOG line.
It must follow this format (checked by CI):

```
type(optional scope): description
```

| Type | Use for | In CHANGELOG |
|---|---|---|
| `feat` | New behaviour | Features |
| `fix` | Bug fix | Bug fixes |
| `perf` | Performance | Performance |
| `docs` | Documentation | Documentation |
| `build` | Dependencies, packaging | Dependencies and maintenance |
| `revert` | Undo a previous change | Reverts |
| `ci`, `test`, `refactor`, `chore` | Everything else | Hidden |

Add `!` after the type for a breaking change, e.g. `feat!: rename BAMBOO_SUBDOMAIN`.

## Releasing a version (maintainers)

1. release-please keeps a PR titled `chore: release X.Y.Z` open, with the CHANGELOG already written.
2. Its checks wait for approval: click **Approve workflows and run** on that PR.
3. When it is green, merge it. The tag `vX.Y.Z` and the GitHub Release are created automatically.
