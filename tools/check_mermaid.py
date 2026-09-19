#!/usr/bin/env python3
"""Extract every ```mermaid block from the repo's Markdown and render it.

GitHub renders Mermaid server-side and simply prints a parse error in place of
a broken diagram, so a syntax mistake ships silently. This renders each block
with mermaid-cli and fails on the first one that does not compile.

    npm install -g @mermaid-js/mermaid-cli
    python3 tools/check_mermaid.py

Set MMDC_PUPPETEER_CONFIG to a puppeteer JSON config if Chromium is not on the
default path (common in containers).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOCK_RE = re.compile(r"^```mermaid[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)


def blocks() -> list[tuple[Path, int, str]]:
    found = []
    for md in sorted(REPO.rglob("*.md")):
        if any(p in md.parts for p in (".git", "node_modules")):
            continue
        text = md.read_text(encoding="utf-8")
        for m in BLOCK_RE.finditer(text):
            line = text[: m.start()].count("\n") + 1
            found.append((md.relative_to(REPO), line, m.group(1)))
    return found


def main() -> int:
    mmdc = shutil.which("mmdc")
    found = blocks()
    print(f"{len(found)} mermaid block(s) across the repo")
    if not mmdc:
        print("mmdc not found -- install @mermaid-js/mermaid-cli to validate rendering.")
        print("Listing blocks only.")
        for path, line, _ in found:
            print(f"  {path}:{line}")
        return 0

    cfg = os.environ.get("MMDC_PUPPETEER_CONFIG")
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for path, line, source in found:
            src = Path(tmp) / "d.mmd"
            src.write_text(source, encoding="utf-8")
            cmd = [mmdc, "-i", str(src), "-o", str(Path(tmp) / "d.svg")]
            if cfg:
                cmd += ["-p", cfg]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = (proc.stdout or "") + (proc.stderr or "")
            ok = proc.returncode == 0 and "Error" not in out and "error" not in out.lower()
            print(f"  {'OK  ' if ok else 'FAIL'} {path}:{line}")
            if not ok:
                failures += 1
                print("    " + "\n    ".join(out.strip().splitlines()[-8:]))
    if failures:
        print(f"\n{failures} block(s) failed to render")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
