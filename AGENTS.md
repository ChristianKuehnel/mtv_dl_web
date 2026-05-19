# Agent Notes

## Project Commands
- Setup: `scripts/setup.sh`
- Lint: `scripts/lint.sh`
- Run locally: `scripts/run.sh`
- Python syntax check: `.venv/bin/python -m compileall src/mtv_dl_web`

## Editing Preferences
- Keep the frontend in `src/mtv_dl_web/static/index.html`.
- Use `apply_patch` for manual file edits.
- Prefer small, focused changes that match the existing style.
- Do not run `scripts/setup.sh` unless dependency installation is needed.

## Configuration
- Runtime config is loaded from `mtv_dl_web.yaml`.
- `download_basedir` is the user-facing download base directory.
- `mtv_dl_targetdir` is the mtv_dl target template.
- `config.base_dir` is the normalized absolute base directory.
- `config.download_path` is derived from `base_dir` and `mtv_dl_targetdir`.

## Linting
- Shell scripts are checked with ShellCheck.
- Python is checked with Black and mypy.
- `src/mtv_dl_web/static/index.html` is checked with Prettier and HTMLHint.
- run `scripts/lint.sh` as to execute all linters
