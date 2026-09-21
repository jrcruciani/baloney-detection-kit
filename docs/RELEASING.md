# Releasing BDK

Maintainer-only checklist: a human authorizes publication; preparation is not a release or efficacy claim.

1. Select an exact reviewed commit and version under [VERSIONING.md](../VERSIONING.md).
   For historical `v3.0.0`, review the `1a8f843` baseline; do not tag the current tip's Unreleased additions as historical 3.0.0.
   Alternatively prepare the next version after maintainer behavior/version sign-off (including Spanish review); this guide chooses neither.
2. Align `pyproject.toml`, `src/bdk/__init__.py`, `CITATION.cff`, `.claude-plugin/plugin.json`, `.zenodo.json`, and `CHANGELOG.md`.
   For a new version, bump all five metadata versions, move only approved Unreleased entries, and agree the citation/changelog release date.
   Historical 3.0.0 has software date `2026-08-23`, not a first GitHub/Zenodo publication timestamp; never fabricate dates or a DOI.
3. Verify PyPI's trusted publisher matches this owner/repository, `.github/workflows/publish.yml`, and environment `pypi`.
   Review the selected commit's workflow: pinned `pypa/gh-action-pypi-publish`, `id-token: write`, no long-lived token (already configured in source).
   Verify the repository's Zenodo integration is enabled before publication; `.zenodo.json` alone does not enable it.
4. Run every [required offline check](../CONTRIBUTING.md#required-checks), then `python -m build` for wheel AND sdist.
   Inspect both archives for unintended/private files; install the wheel alone into a fresh temporary venv with base dependencies only.
   Check `bdk`/`robopsych`, diagnostic data, and exact `bdk apply` retrieval (English six, Spanish compact/full for the current candidate).
   Use the selected release's promised inventory for older baselines; no optional SDKs/dev artifacts in the base install. Worksheets remain repository-only.
5. Only after review/approval, a maintainer may run this historical-version example (replace the SHA; use the approved version instead for new releases):

   ```bash
   git tag -a v3.0.0 <reviewed-3.0.0-sha> -m "BDK 3.0.0"
   git push origin refs/tags/v3.0.0
   gh release create v3.0.0 --verify-tag --title "BDK 3.0.0" --notes-file <reviewed-release-notes>
   ```

6. Verify the published tag's commit and GitHub release, then the publish workflow result AND actual PyPI version/artifacts; test a fresh registry install.
   A green build or successful upload step alone is not proof of the expected package; do not add unverified success badges.
7. Verify Zenodo actually minted a DOI for that release; only then paste the real DOI into `README.md` and `CITATION.cff` (no guessed placeholders).
8. Optionally tag `prompt-v2.0` at that same commit only after explicit behavior/version approval; an unchanged marker does not imply unchanged behavior.
