#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # Example: Keep lists short on one line if they fit
        if isinstance(obj, list) and len(obj) < 4:
            return json.JSONEncoder.default(self, obj)
        return super().default(obj)

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def load_jsonc(path: Path) -> dict:
    """
    Very simple JSONC loader:
    - strips // line comments
    - strips /* */ block comments
    """
    text = path.read_text(encoding="utf-8")
    lines = []
    in_block = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("/*"):
            in_block = True
            continue
        if stripped.endswith("*/"):
            in_block = False
            continue
        if in_block:
            continue
        if stripped.startswith("//"):
            continue

        lines.append(line)

    return json.loads("\n".join(lines))


def run(cmd: list[str], cwd: Path | None = None, capture_output:bool = False):
    result = subprocess.run(
        cmd, 
        cwd=cwd, 
        check=True, 
        capture_output=capture_output,
        stdin=sys.stdin, # inherit stdin to enable git to be interactive
    )
    return result.stdout if capture_output else None


def sync_lib(libinfo_path: Path):
    original_libinfo_path = libinfo_path
    libinfo_path = libinfo_path.resolve()
    base_dir = libinfo_path.parent

    meta = load_jsonc(libinfo_path)

    repo = meta["repo"]
    tag = meta.get("tag")
    files = meta.get("files", [])

    new_meta = meta.copy()

    if not tag:
        raise RuntimeError("libinfo.jsonc must specify a tag")

    if not files:
        raise RuntimeError("libinfo.jsonc contains no files")

    with tempfile.TemporaryDirectory(prefix="pkms-lib-") as tmp:
        tmp = Path(tmp)

        # print(f"[INFO] Cloning {repo} to {repr(str(tmp))}")
        # run(["git", "clone", "--quiet", repo, str(tmp)])

        # print(f"[INFO] Checking out tag {tag}")
        # run(["git", "checkout", "--quiet", tag], cwd=tmp)

        print(f"[INFO] Cloning {repo} to {repr(tmp.as_posix())}")
        print(f"[INFO] Checking out tag {tag}")
        run(["git", "-c", "advice.detachedHead=false", "clone", "--branch", tag, "--single-branch", repo, tmp])

        print(f"[INFO] Getting commit rev on tag {tag}")
        # output: bytearray = run(["git", "rev-parse", tag], cwd=tmp, capture_output=True)
        output: bytearray = run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True)
        commit = output.decode().strip()
        print(f"[INFO] Getting commit rev={commit} on tag {tag}")

        new_files = []
        for entry in files:
            src = tmp / entry["from"]
            dst = base_dir / entry["to"]

            if not src.exists():
                raise FileNotFoundError(f"Source file not found: {entry['from']}")

            print(f"[SYNC] {entry['from']} -> {entry['to']}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

            # integrity check
            size = dst.stat().st_size
            sha256 = sha256_of_file(dst)

            new_entry = {
                'from': entry['from'],
                'to': entry['to'],
                'size': size,
                'sha256': sha256.lower(),
            }
            new_files.append(new_entry)

        new_meta.pop('commit')
        new_meta['commit'] = commit
        new_meta.pop('files')
        new_meta['files'] = new_files
    new_libinfo_path = libinfo_path.with_suffix('.new.jsonc')
    new_libinfo_path.write_text(json.dumps(new_meta, indent=4), newline='\n')
    path = original_libinfo_path.with_suffix('.new.jsonc').as_posix()
    print(f"[INFO] New libinfo is at {repr(path)}, please verify and merge the config.")
    


def main():
    parser = argparse.ArgumentParser(
        description="Sync embedded library files from libinfo.jsonc"
    )
    default = "./pkg/pkms/lib/odt_to_html/libinfo.jsonc"
    parser.add_argument("libinfo", type=Path, help="Path to libinfo.jsonc", default=default, nargs='?')

    args = parser.parse_args()

    try:
        sync_lib(args.libinfo)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()