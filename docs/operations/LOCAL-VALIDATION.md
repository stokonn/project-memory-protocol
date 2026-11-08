# Local validation checklist

This checklist is for maintainers validating a PMP change before opening or updating a pull request. Run it from the repository root in a disposable development checkout.

## 1. Record the exact source

Before running checks, record:

- `git rev-parse HEAD` — the source commit being tested
- `git status --short` — whether the checkout contains uncommitted changes
- Python version and operating system
- the exact command and exit status for every check

Do not describe results from a dirty checkout as validation of a commit unless the diff is also recorded.

## 2. Prepare an isolated environment

Use a project-local virtual environment. Do not install PMP globally just to satisfy a test.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If the repository does not define a `dev` extra, follow the dependency instructions in `pyproject.toml` instead; do not silently invent a dependency group.

## 3. Run the test suite and packaging checks

```sh
python -m pytest
python -m build
```

Run any repository-defined lint, type-check, synthetic demo, and benchmark commands documented in the current project configuration. Record commands exactly; do not infer a pass from a command merely starting.

## 4. Exercise the relevant behavior

For adapter, checkpoint, or recovery changes, add or run focused tests covering:

- project paths containing spaces
- invocation from outside the project working directory
- a conflicting inherited `PMP_STATE_HOME`
- read-only inspection leaving private state unchanged
- interrupted or damaged journal handling
- source changes invalidating stale verification evidence
- preservation of existing user configuration and hook artifacts

Only claim a case was tested if a test or operator run actually exercised it.

## 5. Report results precisely

A useful validation note includes:

| Field | Record |
| --- | --- |
| Source SHA | Full commit SHA |
| Worktree | Clean or exact uncommitted diff |
| Environment | OS and Python version |
| Tests | Exact command, passed/failed/skipped counts |
| Build | Exact command and result |
| CI | Workflow run URL and exact tested SHA |
| Limitations | Untested platforms, live integrations, or manual steps |

A green CI matrix demonstrates only the code paths exercised by those jobs. It does not prove authenticated vendor-hook delivery, model behavior, token savings, or safety of an unrelated user project.

## Safety boundary

Use disposable synthetic projects for integration probes. Do not point experiments at a real project such as Gould, copy credentials or transcripts into test fixtures, bypass agent approval prompts, or reset private PMP state to make a test pass.
