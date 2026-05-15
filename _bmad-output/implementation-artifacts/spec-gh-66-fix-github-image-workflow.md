---
title: 'Issue 66: Fix container publish workflow build failure'
type: 'bugfix'
created: '2026-05-15T00:00:00Z'
status: 'in-review'
baseline_commit: '778f10169b8b3c270c72998b0811c2b55ccfc208'
context:
  - '{project-root}/_bmad-output/project-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** GitHub issue #66 reports that the `Publish Container Image` workflow fails during the Docker build step on `main`, so no new image is pushed to GHCR. The failing log shows `/bin/sh: 1: curl: not found` at the `RUN curl -LsSf https://astral.sh/uv/install.sh ...` layer in the project `Dockerfile`, revealing a brittle uv installation method in the container build.

**Approach:** Replace shell-installer based uv bootstrapping with the official binary-copy pattern (`COPY --from=ghcr.io/astral-sh/uv ...`) in the Dockerfile, preserving existing runtime behavior and image publishing flow while removing the `curl` dependency. Then verify the fix by rebuilding locally and ensuring CI-oriented checks around the Dockerfile still pass.

## Boundaries & Constraints

**Always:** Keep scope limited to restoring successful image build/publish for issue #66; keep `Dockerfile` based on `python:3.11-slim`; install uv using the official container-binary copy pattern from `ghcr.io/astral-sh/uv`; preserve current workflow trigger/metadata/signing behavior unless a direct bug fix requires adjustment; keep Docker layering clean and deterministic.

**Ask First:** Any change that alters image tagging strategy, signing policy, workflow permissions, registry target, base image family/version, or dependency installation mechanism beyond fixing the missing build prerequisite.

**Never:** Do not redesign the release workflow, add unrelated tooling, or refactor application runtime startup; do not use shell-installer based uv bootstrap (`curl`/install script) or ad-hoc Python/pip fallbacks; do not broaden this issue into general container hardening or multi-platform optimization work.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Build on clean runner | `publish-container.yml` runs on GitHub-hosted Ubuntu with `Dockerfile` based on `python:3.11-slim` and uv copied from official image | Build progresses past uv availability step and continues dependency sync/push steps without curl dependency | If build still fails, log points to the next concrete layer failure rather than `curl: not found` |
| Local Docker build | Developer runs `docker build -t mtv_dl_web:test .` from repo root | Image builds successfully with uv installed and app layers created | If apt repo/network fails, Docker build exits with apt error and no partial success is reported |
| Future base image refresh | Upstream `python:3.11-slim` updates package metadata | Dockerfile still obtains uv from the explicit uv image source and remains independent of base-image package availability | If uv source tag/digest changes incompatibly, build fails at copy step with explicit source reference |

</frozen-after-approval>

## Code Map

- `Dockerfile` -- Container build definition updated to source uv binaries from the official uv image.
- `.github/workflows/publish-container.yml` -- GitHub Actions workflow that executes the failing build-and-push path for issue #66.

## Tasks & Acceptance

**Execution:**
- [x] `Dockerfile` -- Replace shell-based uv installation with `COPY --from=ghcr.io/astral-sh/uv ...` so uv binaries are provided directly in the image -- removes the missing-`curl` failure mode and aligns with the recommended installation path for containers.
- [x] `Dockerfile` -- Remove obsolete uv install-script and `PATH` mutation lines tied to `/root/.cargo/bin` -- keeps the image definition minimal and avoids dead configuration.
- [x] `.github/workflows/publish-container.yml` -- Verify no workflow YAML change is required for this defect; only adjust if needed to support the corrected Docker build path -- prevents incidental workflow churn.
- [x] `Dockerfile` -- Ensure ordering remains cache-friendly (uv binary availability before `uv sync`, dependency layer before full source copy) -- preserves efficient rebuild characteristics.

**Acceptance Criteria:**
- Given the repository state that reproduced issue #66, when GitHub Actions runs `Publish Container Image`, then the build no longer fails at uv bootstrap due to missing `curl` and proceeds through dependency installation.
- Given the updated `Dockerfile`, when `docker build -t mtv_dl_web:test .` is executed locally, then the image build completes successfully through dependency installation layers.
- Given unchanged workflow tags/signing configuration, when the publish workflow succeeds, then image tags and signing behavior remain consistent with existing `latest` and `main-<sha>` output conventions.

## Spec Change Log

## Design Notes

The failure is deterministic and isolated: the Dockerfile executes `curl` in a slim base image that does not include it by default. The lowest-risk correction is to remove the shell-installer dependency entirely and copy uv binaries from the official uv container image.

A minimal pattern that fits this repository's current container style is:

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

This keeps the change focused on the failing dependency path, keeps layer contents predictable, and avoids introducing a broader workflow/toolchain shift in the same bugfix.

## Verification

**Commands:**
- `docker build -t mtv_dl_web:test .` -- expected: build succeeds and no `curl: not found` appears.
- `python3 -m pytest` -- expected: existing tests still pass (sanity check that container fix did not affect app code paths).
