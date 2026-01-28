#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
from datetime import datetime, timezone
import pathlib
import time

DEFAULT_ORIGIN = "origin"
DEFAULT_BRANCH = "beads-sync"
DEFAULT_WORKTREE = "./.git/beads-worktrees/beads-sync"


# ---------- helpers ----------

def run(cmd, cwd=None, allow_fail=False, capture=False):
    print(f"$ {' '.join(cmd)}")
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

def stat_issues_jsonl(worktree):
    path = os.path.join(worktree, ".beads", "issues.jsonl")
    if os.name == 'nt':
        path = path.replace('\\','/')

    if not os.path.isfile(path):
        print(f"- issues.jsonl: MISSING")
        print(f"    path : {path!r}")
        return

    st = os.stat(path)

    def fmt(ts):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

    print(f"- issues.jsonl: EXISTS")
    print(f"    path : {path!r}")
    print(f"    size : {st.st_size} bytes")
    print(f"    ctime: {fmt(st.st_ctime)}")
    print(f"    mtime: {fmt(st.st_mtime)}")
    print(f"    atime: {fmt(st.st_atime)}")

def do_status(origin, branch, worktree):
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

    stat_issues_jsonl(worktree)

    print("=== end status ===")




# ---------- operations ----------

def do_pull(origin, branch, worktree):
    print("=== pull: remote → db ===")
    run(["git", "pull", "--rebase", origin, branch], cwd=worktree)
    run(["bd", "sync", "--import-only"])
    ok("pull completed")


def do_push(origin, branch, worktree):
    print("== push: db → remote ==")
    run(["bd", "sync", "--flush-only"])

    run(["git", "add", ".beads"], cwd=worktree)

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=worktree
    )

    if diff.returncode == 0:
        ok("no changes to commit, push skipped")
        return

    msg = f"ticket(sync): {datetime.now(timezone.utc).astimezone().isoformat()}"
    run(["git", "commit", "-m", msg], cwd=worktree)
    run(["git", "push", origin, branch], cwd=worktree)
    ok("push completed")


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Predictable beads sync wrapper (human + agent safe)"
    )

    parser.add_argument(
        "command",
        choices=["status", "pull", "push", "sync", "help"],
        help="operation to perform"
    )
    parser.add_argument("origin", nargs="?", default=DEFAULT_ORIGIN)
    parser.add_argument("branch", nargs="?", default=DEFAULT_BRANCH)
    parser.add_argument("worktree", nargs="?", default=DEFAULT_WORKTREE)

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        return

    if args.command == "status":
        do_status(args.origin, args.branch, args.worktree)
        return

    # safety gates for mutating commands
    check_worktree(args.worktree)
    check_branch(args.worktree, args.branch)

    try:
        if args.command == "pull":
            do_pull(args.origin, args.branch, args.worktree)

        elif args.command == "push":
            do_push(args.origin, args.branch, args.worktree)

        elif args.command == "sync":
            do_pull(args.origin, args.branch, args.worktree)
            do_push(args.origin, args.branch, args.worktree)

        ok("operation finished successfully")

    except RuntimeError as e:
        abort(str(e))


if __name__ == "__main__":
    main()
