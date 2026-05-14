from pathlib import Path


def test_publish_workflow_exists_and_targets_main() -> None:
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "publish-container.yml"
    assert workflow_path.exists()

    content = workflow_path.read_text()
    assert "on:" in content
    assert "push:" in content
    assert "branches:" in content
    assert "- main" in content


def test_publish_workflow_uses_ghcr_and_packages_write() -> None:
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "publish-container.yml"
    content = workflow_path.read_text()

    assert "packages: write" in content
    assert "ghcr.io" in content
    assert "docker/build-push-action" in content
    assert "push: true" in content


def test_publish_workflow_includes_cosign_signing() -> None:
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "publish-container.yml"
    content = workflow_path.read_text()

    assert "id-token: write" in content
    assert "sigstore/cosign-installer" in content
    assert "cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.build-and-push.outputs.digest }}" in content


def test_readme_documents_published_image_and_mounts() -> None:
    readme = (Path(__file__).parent.parent / "README.md").read_text()

    assert "ghcr.io" in readme
    assert "/data" in readme
    assert "/downloads" in readme
    assert "/config" in readme
    assert "/home/appuser/.mtv_dl_web" not in readme
    assert "docker run" in readme
    assert "podman run" in readme


def test_readme_documents_readiness_and_persistence_check() -> None:
    readme = (Path(__file__).parent.parent / "README.md").read_text()

    assert "GET /health" in readme or "curl http://localhost:8000/health" in readme
    assert "restart" in readme
    assert "persists" in readme or "persistence" in readme
