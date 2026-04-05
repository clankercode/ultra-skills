#!/usr/bin/env python3
"""Install/update symlinks for ultra-* skills into Claude Code's skills dir."""
import os
import sys
from pathlib import Path

TARGET_DIR = Path.home() / ".claude" / "skills"
HARNESS_NAME = "Claude Code"


def main() -> int:
    source_root = Path(__file__).resolve().parent
    try:
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: could not create {TARGET_DIR}: {exc}", file=sys.stderr)
        return 1

    linked = updated = already = skipped = errors = 0
    skills = sorted(p for p in source_root.glob("ultra-*") if p.is_dir())

    for src in skills:
        target = TARGET_DIR / src.name
        try:
            if target.is_symlink():
                current = os.readlink(target)
                # Resolve to absolute for comparison
                current_abs = (target.parent / current).resolve() if not os.path.isabs(current) else Path(current).resolve()
                if current_abs == src.resolve():
                    print(f"  ok    {src.name} (already linked)")
                    already += 1
                else:
                    target.unlink()
                    target.symlink_to(src)
                    print(f"  upd   {src.name} (was -> {current})")
                    updated += 1
            elif target.exists():
                # Real directory or file - do not touch
                print(
                    f"  WARN  {src.name}: {target} exists as a real path. "
                    f"Skipping. Suggested fix: mv {target} {target}.backup && rm -rf {target}"
                )
                skipped += 1
            else:
                target.symlink_to(src)
                print(f"  link  {src.name}")
                linked += 1
        except OSError as exc:
            print(f"  ERR   {src.name}: {exc}", file=sys.stderr)
            errors += 1

    print(
        f"\n{HARNESS_NAME} ({TARGET_DIR}): "
        f"{linked} linked, {updated} updated, {already} already-correct, "
        f"{skipped} skipped (real dir), {errors} errors"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
