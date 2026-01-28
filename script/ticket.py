#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
from datetime import datetime, timezone
import pathlib
import time

DEFAULT_REMOTE = "origin"
DEFAULT_BRANCH = "beads-sync"
DEFAULT_WORKTREE = "./.git/beads-worktrees/beads-sync"
SYNC_FILES = [
    ".beads/issues.jsonl",
    ".beads/deletions.jsonl",
    ".beads/interactions.jsonl",
    ".beads/metadata.json",
]

def find_sync_files(worktree):
    files = []
    for rel in SYNC_FILES:
        abs_path = os.path.join(worktree, rel)
        if os.path.isfile(abs_path):
            files.append(rel)
    return files

# ---------- helpers ----------

def run(cmd, cwd=None, allow_fail=False, capture=False):
    cmd_strs = [ repr(c) if ' ' in c else c for c in cmd]
    print(f"$ {' '.join(cmd_strs)}")
    if capture:
        result = subprocess.run(cmd, cwd=cwd, text=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    else:
        result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0 and not allow_fail:
        raise RuntimeError(f"command failed: {' '.join(cmd)}")
    return result


def abort(msg):
    print(f"✗ {msg}")
    sys.exit(1)


def ok(msg):
    print(f"✓ {msg}")


# ---------- safety checks ----------

def check_worktree(path):
    if not os.path.isdir(path):
        abort(f"worktree does not exist: {path}")
    ok(f"worktree exists: {path}")


def get_branch(path):
    res = run(
        ["git", "branch", "--show-current"],
        cwd=path,
        capture=True
    )
    if res.returncode != 0:
        abort("failed to detect current branch")
    return res.stdout.strip()


def check_branch(path, expected):
    current = get_branch(path)
    if current != expected:
        abort(f"worktree on branch '{current}', expected '{expected}'")
    ok(f"on branch {expected}")


# ---------- status ----------

def stat_issues_jsonl(worktree, rel):
    path = os.path.join(worktree, rel)
    if os.name == 'nt':
        path = path.replace('\\','/')

    if not os.path.isfile(path):
        print(f"- {rel}: MISSING")
        # print(f"    path : {path!r}")
        return

    st = os.stat(path)

    def fmt(ts):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

    print(f"- {rel}: EXISTS")
    # print(f"    path : {path!r}")
    print(f"    size : {st.st_size} bytes")
    print(f"    ctime: {fmt(st.st_ctime)}")
    print(f"    mtime: {fmt(st.st_mtime)}")
    print(f"    atime: {fmt(st.st_atime)}")

def do_status(remote, branch, worktree):
    print("=== status ===")

    if not os.path.isdir(worktree):
        print(f"- worktree: MISSING ({worktree})")
        return

    print(f"- worktree: OK ({worktree})")

    print('')

    current = get_branch(worktree)
    if current == branch:
        print(f"- branch:   OK ({branch})")
    else:
        print(f"- branch:   MISMATCH (on {current}, expect {branch})")

    print('')

    # git staged / unstaged JSONL
    res = run(
        ["git", "status", "--porcelain", ".beads"],
        cwd=worktree,
        capture=True
    )
    if res.stdout.strip():
        print("- jsonl:    MODIFIED (pending commit)")
    else:
        print("- jsonl:    CLEAN")

    print('')

    # beads hint (best-effort, no side effects)
    try:
        run(["bd", "sync", "--status"], allow_fail=True)
        print("- beads:    status checked")
    except Exception:
        print("- beads:    status unavailable")

    print('')

    pathlib.Path(worktree)/ '.beads' / 'issue'
    if not os.path.isdir(worktree):
        print(f"- worktree: MISSING ({worktree})")
        return

    print(f"- worktree: OK ({worktree})")

    print('')

    for file in SYNC_FILES:
        stat_issues_jsonl(worktree, file)
        print('')

    print("=== end status ===")

# ---------- operations ----------

def do_pull(remote, branch, worktree):
    print("=== pull: remote → db ===")
    run(["git", "pull", "--rebase", remote, branch], cwd=worktree)
    run(["bd", "sync", "--import-only"])
    ok("pull completed")


def do_push(remote, branch, worktree):
    print("== push: db → remote ==")
    run(["bd", "sync", "--flush-only"])

    sync_files = find_sync_files(worktree=worktree)

    run(["git", "add", "--"] + sync_files, cwd=worktree)

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--"] + sync_files,
        cwd=worktree
    )

    if diff.returncode == 0:
        ok("no changes to commit, push skipped")
        return

    msg = f"ticket(sync): {datetime.now(timezone.utc).astimezone().isoformat()}"
    run(["git", "commit", "-m", msg], cwd=worktree)
    run(["git", "push", remote, branch], cwd=worktree)
    ok("push completed")

def ensure_clean_history(remote, branch, worktree):
    print("# Ensure clean worktree history")
    r = run(
        ["git", "log", f"{remote}/{branch}..HEAD", "--oneline", "--no-decorate", "--no-abbrev-commit"],
        cwd=worktree,
        capture=True,
        allow_fail=True,
    )
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    if r.returncode != 0:
        raise RuntimeError(
            f"Exit with non-zero code={r.returncode}\n"
        )
    if len(lines) == 1 and lines[0].split(' ', 1)[1].startswith("ticket(sync):"):
        rev = lines[0].split(' ', 1)[0]
        print("# Found unpushed ticket(sync) commit, dropping it.")
        run(["git", "reset", "--mixed", f"{rev}~1"], cwd=worktree)
        ok("Dropped unpushed ticket(sync) commit successfully")
    elif lines:
        raise RuntimeError(
            "Found unpushed non-ticket commits. Refusing to clean.\n"
            + "\n".join(lines)
        )
    else:
        ok("No unpushed ticket(sync) commit found. Worktree clean.")

def do_clean(remote, branch, worktree):
    """
    Drop unpushed ticket(sync) commit if exists.
    """
    return ensure_clean_history(remote, branch, worktree)

# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Predictable beads sync wrapper (human + agent safe)"
    )

    choices = ["status", "pull", "push", "sync", "clean", "help"]
    parser.add_argument(
        "command",
        metavar="command",
        choices=["status", "pull", "push", "sync", "clean", "help"],
        help=f"operation to perform: one of {{{', '.join(choices)}}}"
    )
    parser.add_argument(
        "remote", 
        nargs="?", 
        default=DEFAULT_REMOTE,
        help=f"git remote repo to sync to, default is {DEFAULT_REMOTE!r}"
    )
    parser.add_argument(
        "branch", 
        nargs="?", 
        default=DEFAULT_BRANCH,
        help=f"git branch to perform sync , default is {DEFAULT_BRANCH!r}"
    )
    parser.add_argument(
        "worktree", 
        nargs="?", 
        default=DEFAULT_WORKTREE,
        help=f"git worktree path to work in, default is {DEFAULT_WORKTREE!r}"
    )

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        return

    if args.command == "status":
        do_status(args.remote, args.branch, args.worktree)
        return

    # safety gates for mutating commands
    check_worktree(args.worktree)
    check_branch(args.worktree, args.branch)

    try:
        if args.command == "pull":
            ensure_clean_history(args.remote, args.branch, args.worktree)
            do_pull(args.remote, args.branch, args.worktree)

        elif args.command == "push":
            ensure_clean_history(args.remote, args.branch, args.worktree)
            do_push(args.remote, args.branch, args.worktree)

        elif args.command == "sync":
            ensure_clean_history(args.remote, args.branch, args.worktree)
            do_pull(args.remote, args.branch, args.worktree)
            do_push(args.remote, args.branch, args.worktree)

        elif args.command == "clean":
            do_clean(args.remote, args.branch, args.worktree)

        ok("operation finished successfully")

    except RuntimeError as e:
        abort(str(e))


if __name__ == "__main__":
    main()
