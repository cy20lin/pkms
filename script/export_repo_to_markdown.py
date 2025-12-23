import subprocess
import argparse
import fnmatch
from pathlib import Path
import os

def safe_backtick_wrapper(content: str, language: str = "") -> str:
    """
    Wrap file content in a Markdown code block, avoiding backtick conflicts.
    """
    max_backticks = 3
    for line in content.splitlines():
        if "```" in line:
            max_backticks = max(max_backticks, line.count("`") + 1)
    wrapper = "`" * max_backticks
    return f"{wrapper}{language}\n{content}\n{wrapper}"

def is_binary_file(path: Path) -> bool:
    """
    Detect binary files by scanning first 1024 bytes for null bytes.
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
    except Exception:
        return True
    return False

def get_git_files(repo_dir: Path):
    """
    List tracked + untracked (non-ignored) files using git.
    """
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        check=True
    )
    lines = result.stdout.splitlines()
    files = [path for path in lines if os.path.isfile(path)]
    files.sort()
    return files

def should_skip_file(file: str, patterns: list[str]) -> bool:
    """
    Check if file path matches any user-specified skip pattern.
    """
    if not patterns:
        return False
    return any(fnmatch.fnmatch(file, pat) for pat in patterns)

# Language mapping for syntax highlighting
lang_map = {
    # Programming languages
    ".py": "python", ".pyw": "python",
    ".js": "javascript", ".ts": "typescript",
    ".java": "java",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "bash", ".bash": "bash",
    ".bat": "bat",
    ".pl": "perl",
    ".lua": "lua",
    ".r": "r",
    ".jl": "julia",

    # Web / markup / data formats
    ".html": "html", ".htm": "html",
    ".css": "css", ".scss": "scss", ".less": "less",
    ".xml": "xml", ".xsl": "xml",
    ".json": "json",
    ".jsonc": "jsonc",
    ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".md": "markdown",
    ".txt": "text",

    # Config / scripting
    ".gradle": "groovy",
    ".properties": "ini",

    # SQL / data
    ".sql": "sql",
    ".csv": "csv",

    # Other
    ".tex": "latex",
    ".asm": "asm",
}

# Special filenames without extensions
special_filenames = {
    "Dockerfile": "dockerfile",
    "Makefile": "makefile",
    "Vagrantfile": "ruby",
    "CMakeLists.txt": "cmake",
    "Gemfile": "ruby",
    "Rakefile": "ruby",
    "package.json": "json",
    "tsconfig.json": "json",
    "requirements.txt": "text",
    "Pipfile": "toml",
    "pyproject.toml": "toml",
}

def detect_language(file_path: Path) -> str:
    """
    Detect language based on extension or special filename.
    """
    ext = file_path.suffix
    filename = file_path.name
    language = lang_map.get(ext, "")
    if not language:
        language = special_filenames.get(filename, "")
    return language

def export_git_project_to_markdown(repo_dir: Path, output_file: Path,
                                   extensions=None, include_index=True,
                                   binary_skip=False, preserve_newline=False,
                                   skip_filepath_patterns=None):
    files = get_git_files(repo_dir)

    with output_file.open("w", encoding="utf-8", newline="\n") as out:
        out.write("# Project Export (Git tracked + untracked files)\n\n")

        # Index section
        if include_index:
            out.write("## Index\n")
            for file in files:
                if extensions and not any(file.endswith(ext) for ext in extensions):
                    continue
                if should_skip_file(file, skip_filepath_patterns):
                    continue
                out.write(f"- {file}\n")
            out.write("\n---\n\n")

        # Export each file
        for file in files:
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue
            if should_skip_file(file, skip_filepath_patterns):
                print(f"Skipped by pattern: {file}")
                continue

            display_path = file  # keep Unix style for Markdown
            file_path = repo_dir / Path(file)

            if binary_skip and is_binary_file(file_path):
                print(f"Skipped binary file: {file_path}")
                continue

            try:
                size = file_path.stat().st_size
                newline_mode = None if preserve_newline else ""
                with file_path.open("r", encoding="utf-8", errors="replace", newline=newline_mode) as f:
                    lines = f.readlines()
                content = "".join(lines)
                line_count = len(lines)

                # Metadata
                out.write(f"## FILE: {display_path}\n")
                out.write(f"- Size: {size} bytes\n")
                out.write(f"- Lines: {line_count}\n\n")

                # Language detection
                language = detect_language(file_path)

                # Code block
                out.write(safe_backtick_wrapper(content, language))
                out.write("\n\n")
            except Exception as e:
                print(f"Skipped {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Export git-tracked + untracked project files into a single Markdown file."
    )
    parser.add_argument("--repo", "-r", required=True, help="Path to the git repository root")
    parser.add_argument("--output", "-o", required=True, help="Output Markdown file path")
    parser.add_argument("--ext", "-e", nargs="*", default=None,
                        help="Filter by file extensions (e.g. .py .md .txt)")
    parser.add_argument("--no-index", action="store_true", help="Disable index section in output")
    parser.add_argument("--binary-skip", action="store_true", help="Skip binary files when exporting")
    # NOTE
    parser.add_argument("--preserve-original-newline", action="store_true",
                        help="Preserve original CRLF or LF newlines from source files")
    parser.add_argument("--skip", nargs="*", default=None,
                        help="Glob patterns of file paths to skip entirely (e.g. '**/*.html' '**/*.cpp')")

    args = parser.parse_args()
    repo_dir = Path(args.repo).resolve()
    output_file = Path(args.output).resolve()

    export_git_project_to_markdown(
        repo_dir,
        output_file,
        args.ext,
        include_index=not args.no_index,
        binary_skip=args.binary_skip,
        preserve_newline=args.preserve_original_newline,
        skip_filepath_patterns=args.skip
    )

if __name__ == "__main__":
    main()
