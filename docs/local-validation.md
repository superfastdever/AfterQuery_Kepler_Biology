# Running the gates locally

Kepler runs the same gates on the real harness, so a local failure is a
guaranteed pipeline failure. Validate before every submission.

## Setup

```bash
uv tool install harbor      # https://harborframework.com/docs
docker info                 # the daemon must be running
```

## The three commands

```bash
tools/structure-check.py tasks/<date>/<slug>   # submit-time gates, seconds
tools/validate.sh tasks/<date>/<slug>          # oracle must be 1, nop must be 0
tools/validate.sh tasks/<date>/<slug> --check  # adds harbor's LLM rubric review
```

`validate.sh` runs the structure check first, then the oracle and nop runs. Run
it **several times**: the verifier has to be deterministic, and a grader that
passes once is not yet proven.

If the oracle scores 0, read the verifier log before touching the solution.
Most first failures are an artifact path the verifier cannot find, or a tool
that was never installed in the verifier image.

If the nop scores 1, the verifier is passing on nothing and must change.

## Sandbox quirks

Cloud dev containers (including Claude Code on the web) route egress through a
policy-enforcing proxy that re-terminates TLS. Two consequences show up as
Docker build failures that look like bundle defects but are not.

### `pip install` fails with `CERTIFICATE_VERIFY_FAILED`

```
Could not fetch URL https://pypi.org/simple/pytest/: ... self-signed
certificate in certificate chain
```

The build container does not trust the proxy's CA. The fix must **not** go into
the bundle — Kepler's infrastructure has no such proxy, and a Dockerfile
carrying a local CA would be wrong everywhere else and reads as environment
contamination to a reviewer.

`validate.sh` handles this automatically. When it finds a CA bundle at
`/root/.ccr/ca-bundle.crt` (override with `CCR_CA_BUNDLE`), it copies the task
to `build/.local-validation/<slug>/` and patches only the copy, adding the CA
and the standard `PIP_CERT` / `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` variables
after each `FROM`. Harbor runs against the copy; the committed bundle is
untouched. See `tools/_local_ca_patch.py`.

The patch only changes whether TLS can be verified, never which packages get
installed — but it is still a divergence from what Kepler builds. Re-validate
on a machine without an intercepting proxy before treating a run as final.

### apt fails with `403 Forbidden`

```
Err:1 http://deb.debian.org/debian bookworm InRelease
  403  Forbidden
```

This is an **egress policy denial**, not a TLS problem, and it must not be
routed around. In the container these notes were written in,
`deb.debian.org` was blocked while `archive.ubuntu.com` was reachable — so
Debian-based images (`python:*-slim-bookworm` among them) could not `apt-get`,
while `ubuntu:24.04` could.

Practical consequences:

- The verifier image installs its Python dependencies with `pip` and does not
  `apt-get` at all. Keep it that way unless a task genuinely needs a system
  package — the verifier should be minimal regardless.
- If a task's environment needs Debian packages, either base it on Ubuntu or
  validate on a machine with unrestricted egress. Do not weaken the bundle to
  fit a local policy.

Blocked hosts are worth reporting to whoever owns the sandbox policy rather
than working around.

## Where output lands

| Path | What |
| --- | --- |
| `build/harbor-jobs/` | Harbor job directories, one per run |
| `build/harbor-jobs/*.log` | Console output for each run |
| `build/.local-validation/` | CA-patched copies, local use only |
| `build/<slug>.zip` | The submission artifact |

All of `build/` is gitignored.

Inside a job directory, the useful files are `exception.txt` (why a trial
errored), `trial.log` (the full build and run log), and
`artifacts/` (what harbor copied out of the agent's container — check here
first when the verifier says a file is missing).
