# Development

For working *on* snowline. If you only want to *use* it, the README is enough.

## Tests

```bash
python tests/run_tests.py          # ~24 seconds
snowline test-clone                # same tests, from a clean git clone
```

Tests run the scripts end to end through `subprocess` rather than importing
their functions. Two real defects had survived precisely because they only
appeared on the `--apply` path of a real run.

### Every test must be shown to fail first

A test that passes against already-correct code proves nothing. Before adding a
test, break the fix and confirm the test catches it:

```bash
# 1. remove the fix
python tests/run_tests.py     # must FAIL, and the message must name what broke
# 2. restore it
python tests/run_tests.py     # must pass
git diff --stat               # must be empty — no mutation left behind
```

This is not theoretical. The first test written for `smart_replace --apply`
passed while the defect was still present. Three of the six rejection tests
originally passed for reasons unrelated to the gate they claimed to test.

### Rejection tests need both directions

A test that only proves "it refused" cannot tell a working gate from a broken
tool that refuses everything. Prove both: it refuses when it should, and it
accepts when the condition is met.

### Pengujian Mutasi

Mutasi atau skrip uji harus dijalankan dengan `PYTHONPATH=src` atau lewat `snowline test-clone`. Tanpa itu, kode yang diuji adalah paket yang terpasang di site-packages, bukan kode dari pohon kerja.

## Rule #12 — templates and installed copies must match

`src/snowline/templates/` is the source. Three targets mirror it:

```
.agents/                    this repo's own installation
test_hook_arah6/.agents/    hook test fixture
../cbt_master/.agents/      the real project that uses snowline
```

`verify_rule12.ps1` runs on every commit via the pre-commit hook and compares
file hashes. A fix that lives only in `templates/` never reaches anyone.

Sync before committing:

```bash
python -c "
import shutil, os
src = 'src/snowline/templates'
for t in ['../cbt_master/.agents', '.agents', 'test_hook_arah6/.agents']:
    if not os.path.isdir(t): continue
    for it in ['skills', 'hooks', 'hooks.json']:
        s, d = os.path.join(src, it), os.path.join(t, it)
        shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d)
"
```

Note: the checker compares raw bytes, so a CRLF/LF difference reads as a
content difference. `git checkout` can reintroduce one.

## CI

`.github/workflows/ci.yml` runs the suite on every push and pull request to
`main`, on `ubuntu-latest`. One round takes about 14 seconds.

It has been proven to go red: commit `39a166a` broke a test on purpose and the
run failed; `8742682` restored it and the run passed.

## Repository layout

```
src/snowline/               the package
  templates/                what gets installed into a project's .agents/
  chamber_templates/        what `init_chamber` installs
tests/                      the suite
docs/                       this file
.github/workflows/          CI

.here_we_are/               research notes, state, and the chamber connector
agents_chamber/             chamber rules and archive
archive/  deferred/  plan_archive/  plan_tracker/     historical, not shipped
```

`deferred/` holds four tools that were written but intentionally not shipped —
see its README for why.

## Chamber

This repo is developed through the chamber protocol: a human PM relays between
a TL session and a QA session, and every claim of completion must carry the
command and its raw output.

Rules: `agents_chamber/CHAMBER_RULES.md` (Indonesian).
Current state: `.here_we_are/STATE.md`.
Working channel: `.here_we_are/connector.md`.

Two rules there are worth knowing even if you never use the protocol:

- **An entry is not done until `git log` shows it.** Passing on your own disk
  is not passing; a clean clone decides.
- **State files are overwritten, logs are appended.** `STATE.md` is rewritten
  in place; `connector.md` only grows and gets rotated when it passes ~100 KB.

## Releasing

```bash
# bump version in three places, they must agree
pyproject.toml        version = "x.y.z"
src/snowline/__init__.py    __version__
src/snowline/cli.py         the line printed by `snowline`

git tag -a vx.y.z -m "..."
git push origin main && git push origin vx.y.z
```

Users update with:

```bash
pip uninstall snowline-agent-tools -y
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git --force-reinstall --no-cache-dir
```

`--no-cache-dir` matters. Without it pip can reuse a cached clone and install
an old commit while reporting success.
