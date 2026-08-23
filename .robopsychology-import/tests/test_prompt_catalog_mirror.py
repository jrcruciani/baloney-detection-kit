from pathlib import Path


def test_prompt_catalog_mirror_matches_packaged_catalog():
    root = Path(__file__).resolve().parents[1]
    framework_catalog = root / "prompts" / "prompts.yaml"
    packaged_catalog = root / "src" / "robopsych" / "data" / "prompts.yaml"

    assert framework_catalog.read_text(encoding="utf-8") == packaged_catalog.read_text(
        encoding="utf-8"
    )
