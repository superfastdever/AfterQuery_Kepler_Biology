#!/usr/bin/env python3
"""Make a LOCAL-ONLY copy of a task that trusts a TLS-intercepting proxy.

Some sandboxes (Claude Code cloud containers among them) route egress through
a proxy that re-terminates TLS. Docker build containers do not trust that
proxy's CA, so `pip install` inside a build dies with:

    CERTIFICATE_VERIFY_FAILED: self-signed certificate in certificate chain

Kepler's infrastructure has no such proxy, so the fix must NOT go into the
bundle -- a Dockerfile carrying a local CA would be wrong everywhere else and
would look like environment contamination to a reviewer.

This script therefore copies the task elsewhere and patches only the copy:
the CA bundle is placed in each Docker build context and every Dockerfile is
given, after each FROM, the standard CA environment variables the proxy's
README prescribes. The bundle that gets committed and submitted is untouched.

Used by tools/validate.sh; not normally run by hand.

    tools/_local_ca_patch.py <src-task-dir> <dest-dir> [--ca <path>]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_CA = Path("/root/.ccr/ca-bundle.crt")
CA_NAME = "ccr-local-proxy-ca.crt"

# Inserted after each FROM. Kept to a COPY and ENVs so the patch cannot change
# which packages get installed -- only whether TLS to them can be verified.
PATCH = f"""
# >>> LOCAL VALIDATION ONLY -- injected by tools/_local_ca_patch.py.
# Not part of the submitted bundle. Lets this build trust the sandbox's
# TLS-intercepting egress proxy so pip can reach PyPI.
COPY {CA_NAME} /usr/local/share/ca-certificates/{CA_NAME}
ENV PIP_CERT=/usr/local/share/ca-certificates/{CA_NAME} \\
    SSL_CERT_FILE=/usr/local/share/ca-certificates/{CA_NAME} \\
    REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/{CA_NAME} \\
    CURL_CA_BUNDLE=/usr/local/share/ca-certificates/{CA_NAME} \\
    NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/{CA_NAME}
# <<< LOCAL VALIDATION ONLY
"""


def patch_dockerfile(path: Path) -> int:
    """Insert the CA block after every FROM line. Returns how many were added."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    added = 0
    for line in lines:
        out.append(line)
        if line.lstrip().upper().startswith("FROM "):
            if not line.endswith("\n"):
                out.append("\n")
            out.append(PATCH)
            added += 1
    if added:
        path.write_text("".join(out), encoding="utf-8")
    return added


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("dest", type=Path)
    ap.add_argument("--ca", type=Path, default=DEFAULT_CA)
    args = ap.parse_args()

    if not args.src.is_dir():
        print(f"error: {args.src} is not a directory", file=sys.stderr)
        return 2
    if not args.ca.is_file():
        print(f"error: CA bundle not found at {args.ca}", file=sys.stderr)
        return 2

    if args.dest.exists():
        shutil.rmtree(args.dest)
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(args.src, args.dest)

    total = 0
    for dockerfile in sorted(args.dest.rglob("Dockerfile")):
        n = patch_dockerfile(dockerfile)
        if n:
            # The CA must sit in that Dockerfile's build context.
            shutil.copyfile(args.ca, dockerfile.parent / CA_NAME)
            total += n
            print(f"  patched {dockerfile.relative_to(args.dest)} ({n} stage(s))")

    if not total:
        print("  no Dockerfiles patched", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
