import json
import hashlib
from pathlib import Path

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


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_libinfo(libinfo_path: Path) -> None:
    base_dir = libinfo_path.parent
    info = load_jsonc(libinfo_path)

    errors = 0

    for entry in info.get("files", []):
        rel = entry["to"]
        expected_size = entry.get("size")
        expected_sha256 = entry.get("sha256")

        file_path = base_dir / rel

        print(f"Checking: {file_path}")

        if not file_path.exists():
            print(f"  ❌ MISSING file")
            errors += 1
            continue

        actual_size = file_path.stat().st_size
        if expected_size is None: 
            print("  ❌ MISSING size")
            errors += 1
        elif actual_size != expected_size:
            print(f"  ❌ SIZE mismatch: expected {expected_size}, got {actual_size}")
            errors += 1
        else:
            print(f"  ✅ size OK")

        if expected_sha256 is None: 
            print("  ❌ MISSING sha256")
            errors += 1
        else:
            actual_sha256 = sha256_of_file(file_path)
            if actual_sha256.lower() != expected_sha256.lower():
                print(f"  ❌ SHA256 mismatch")
                print(f"     expected: {expected_sha256}")
                print(f"     actual:   {actual_sha256}")
                errors += 1
            else:
                print(f"  ✅ sha256 OK")

    if errors:
        raise SystemExit(f"\nIntegrity check failed: {errors} error(s)\n")
    else:
        print("\nAll files passed integrity check ✔\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python verify_libinfo.py path/to/libinfo.jsonc")
        raise SystemExit(1)

    verify_libinfo(Path(sys.argv[1]))
