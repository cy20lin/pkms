# ticket.py – explicit beads sync helper

`ticket.py` is a **thin, explicit, and user-controlled wrapper** around beads sync workflows.

It exists because the built-in `bd sync` workflow hides too many steps, states, and assumptions.
This tool makes *every step visible, auditable, and predictable*.

---

## Design goals

* Reduce cognitive load, not increase it
* No hidden state transitions
* Git operations are explicit and inspectable
* Failure is loud and early
* Easy to migrate away from beads (JSONL-first)

---

## Command overview

```bash
ticket.py {pull|push|sync|status|help} [origin] [branch] [worktree-dir]
```

### Defaults

| Parameter    | Default                           |
| ------------ | --------------------------------- |
| origin       | origin                            |
| branch       | beads-sync                        |
| worktree-dir | ./.git/beads-worktrees/beads-sync |

---

## Commands

### `ticket pull`

**Remote → DB**

Steps:

1. Ensure worktree exists
2. Ensure worktree is on the specified branch
3. `git pull --rebase <origin> <branch>`
4. `bd sync --import-only`

Success criteria:

* No errors
* No import conflicts

---

### `ticket push`

**DB → Remote**

Steps:

1. Ensure worktree exists
2. `bd sync --flush-only`
3. Detect changes in `.beads/issues.jsonl`
4. If changed:

   * `git add .beads/issues.jsonl`
   * `git commit -m "ticket(sync): <local-iso-timestamp>"`
   * `git push <origin> <branch>`
5. If no changes: considered **successful noop sync**

---

### `ticket sync`

**pull + push (explicit sequence)**

Steps:

1. `ticket pull`
2. `ticket push`

Each step must succeed before continuing.

---

### `ticket status`

Prints:

* Worktree existence
* Current branch
* Git clean/dirty state
* beads JSONL file info (if exists):

  * path: `<worktree>/.beads/issues.jsonl`
  * size
  * ctime / mtime / atime

This command is **read-only** and safe.

---

## Commit message convention

All commits created by this tool use:

```text
ticket(sync): YYYY-MM-DDTHH:MM:SS.xxxxxx+TZ
```

Rationale:

* `ticket` is human-readable and tool-agnostic
* Avoids collision with `tk-<id>` issue prefixes
* Distinguishes personal workflow tooling from beads internals
* Follows conventional-commit style (`tool(scope)`)

---

## Safety checks

Before any mutating operation, `ticket.py` verifies:

* Worktree directory exists
* Worktree is on the expected branch
* Previous command succeeded

Failure aborts immediately with a clear error.

---

## Non-goals

* Replacing beads
* Hiding git
* Being "smart"

This tool prefers **explicitness over magic**.
