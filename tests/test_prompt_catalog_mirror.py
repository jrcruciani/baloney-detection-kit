from pathlib import Path


def test_prompt_catalog_mirror_matches_packaged_catalog():
    root = Path(__file__).resolve().parents[1]
    framework_catalog = root / "prompts" / "diagnosis" / "catalog.yaml"
    packaged_catalog = root / "src" / "bdk" / "data" / "prompts.yaml"

    assert framework_catalog.read_text(encoding="utf-8") == packaged_catalog.read_text(
        encoding="utf-8"
    )
