---
title: 'Support all config parameters through environment variables'
type: 'feature'
created: '2026-05-15T00:00:00Z'
status: 'done'
baseline_commit: '0708026a20bc471c76c907a19d9cd53d08b9be4e'
context: ['{project-root}/_bmad-output/project-context.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Container deployments are currently less ergonomic because not all runtime settings are exposed in a predictable environment-variable contract. This forces operators to rely on config files even when environment-only configuration is preferred in orchestrated environments.

**Approach:** Extend the settings model so every supported configuration parameter can be read from environment variables, while preserving deterministic precedence: environment variables override config file values, and config file values override defaults. Keep validation strict so unsupported keys still fail fast.

## Boundaries & Constraints

**Always:**
- Preserve precedence exactly as: environment variables > config file values > in-code defaults.
- Keep existing setting names and value types stable to avoid breaking current callers.
- Continue rejecting unknown config-file keys with a clear error.
- Ensure settings loading remains import-safe for application startup.

**Ask First:**
- Renaming existing config keys or introducing aliases that could change backward compatibility.
- Expanding scope beyond application settings loading (for example runtime behavior changes in unrelated modules).

**Never:**
- Introduce direct SQLite or mtv_dl integration changes for this issue.
- Add new required settings without defaults unless explicitly requested.
- Relax validation to silently ignore malformed or unknown config keys.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| ENV_PRECEDENCE | YAML provides `port: 7000`; env has `PORT=9001` | Loaded settings use `port=9001` and keep non-overridden YAML values | N/A |
| FILE_FALLBACK | Env var for `host` is missing; YAML provides `host: 127.0.0.1` | Loaded settings use file value for `host` | N/A |
| DEFAULT_FALLBACK | Neither env nor YAML defines `enable_mkv_merge` | Loaded settings use default `False` | N/A |
| UNKNOWN_FILE_KEY | YAML contains unsupported key | Settings loading fails with explicit unknown-key error | Raise `ValueError` with key names |
| INVALID_TYPE_FROM_ENV | Env var cannot coerce to target type (e.g., non-int for `PORT`) | Settings validation fails and startup does not proceed silently | Surface validation error at load time |

</frozen-after-approval>

## Code Map

- `src/mtv_dl_web/config/settings.py` -- Defines settings schema and config/env merge logic.
- `tests/test_service_configuration.py` -- Verifies precedence, validation, and fallback behavior for settings loading.
- `src/mtv_dl_web/main.py` -- Consumes resolved settings values during startup; indirect integration surface to keep compatible.

## Tasks & Acceptance

**Execution:**
- [x] `src/mtv_dl_web/config/settings.py` -- Ensure every declared setting field is env-bindable and loaded with strict precedence (env > file > defaults), including config-file-assisted initialization -- implements issue behavior and prevents container configuration gaps.
- [x] `src/mtv_dl_web/config/settings.py` -- Keep unknown config key validation and explicit load failure behavior unchanged or stricter -- preserves safe, predictable startup.
- [x] `tests/test_service_configuration.py` -- Expand tests to cover all settings parameters across precedence paths (env override, file fallback, default fallback) and representative type coercion errors -- proves behavior is complete and stable.

**Acceptance Criteria:**
- Given a config file defines valid values and matching environment variables are set for one or more settings, when settings are loaded, then environment values take precedence and non-overridden file values are retained.
- Given a setting is absent from environment variables but present in the config file, when settings are loaded, then the config file value is used.
- Given a setting is absent from both environment variables and config file, when settings are loaded, then the model default is used.
- Given the config file contains unknown keys, when settings are loaded, then loading fails with an explicit unknown-key error.
- Given an environment variable value cannot be parsed into the target setting type, when settings are loaded, then validation fails instead of silently coercing to an invalid runtime state.

## Spec Change Log

## Design Notes

The implementation should continue using a single source-of-truth settings schema so adding a new field automatically participates in precedence handling without duplicating merge code. Favor deriving the list of configurable keys from the settings model metadata rather than maintaining separate hardcoded allowlists.

## Verification

**Commands:**
- `pytest tests/test_service_configuration.py` -- expected: all settings precedence and validation tests pass.
- `pytest` -- expected: regression suite remains green.

## Suggested Review Order

**Precedence merge logic**

- Start here to see env/file/default precedence encoded in one flow.
  [`settings.py:39`](../../src/mtv_dl_web/config/settings.py#L39)

- This merge point preserves environment-derived values and applies only safe YAML keys.
  [`settings.py:58`](../../src/mtv_dl_web/config/settings.py#L58)

- Final model reconstruction re-validates merged values before runtime use.
  [`settings.py:65`](../../src/mtv_dl_web/config/settings.py#L65)

**Coverage of contract**

- Validates all settings load from YAML when no environment overrides exist.
  [`test_service_configuration.py:48`](../../tests/test_service_configuration.py#L48)

- Proves all exposed environment variables override file-provided values.
  [`test_service_configuration.py:82`](../../tests/test_service_configuration.py#L82)

- Guards startup against invalid typed environment values.
  [`test_service_configuration.py:126`](../../tests/test_service_configuration.py#L126)

- Confirms defaults apply when both env and YAML omit a setting.
  [`test_service_configuration.py:137`](../../tests/test_service_configuration.py#L137)
