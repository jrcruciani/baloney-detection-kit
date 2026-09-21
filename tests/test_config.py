"""Strict, isolated tests of the CLI model-alias configuration."""

from pathlib import Path

import pytest

from bdk.config import ModelConfigError, load_model_aliases, resolve_model

pytestmark = pytest.mark.usefixtures("isolated_model_config")


def test_missing_files_preserve_raw_ids():
    assert load_model_aliases() == {}
    for model in ("claude-raw", "gpt-raw", "gemini-raw", "azure/deployment", "org/custom"):
        assert resolve_model(model) == model


def test_default_requires_explicit_configuration():
    with pytest.raises(ModelConfigError, match='Model alias "default" is not configured') as exc:
        resolve_model("default")
    assert "./bdk.toml" in str(exc.value)
    assert "~/.config/bdk/config.toml" in str(exc.value)
    assert "raw model ID" in str(exc.value)


def test_local_overrides_user_per_alias(isolated_model_config):
    user, local = isolated_model_config
    user.write_text('[models]\ndefault = "gpt-user"\nanthropic = "claude-user"\n')
    local.write_text('[models]\ndefault = "gemini-local"\nazure = "azure/deployment"\n')
    assert load_model_aliases() == {
        "default": "gemini-local",
        "anthropic": "claude-user",
        "azure": "azure/deployment",
    }
    assert resolve_model("default") == "gemini-local"
    assert resolve_model("anthropic") == "claude-user"
    assert resolve_model("azure") == "azure/deployment"
    assert resolve_model("Default") == "Default"


def test_aliases_are_single_lookup_not_chains(isolated_model_config):
    _, local = isolated_model_config
    local.write_text('[models]\nfirst = "second"\nsecond = "first"\n')
    assert resolve_model("first") == "second"
    assert resolve_model("second") == "first"


@pytest.mark.parametrize("location", [0, 1], ids=["user", "local"])
@pytest.mark.parametrize(
    "content",
    [
        b"[models",
        b"[models]\ndefault = 'one'\ndefault = 'two'",
        b"[models]\ndefault = '\xff'",
        b"",
        b"models = 'gpt-raw'",
        b"[provider]\napi_key = 'not-a-credential'",
        b"[models]\ndefault = 'gpt-raw'\n[credentials]\nkey = 'not-a-credential'",
        b"[models]\ndefault = 1",
        b"[models]\ndefault = true",
        b"[models]\ndefault = ['gpt-raw']",
        b"[models]\ndefault = {model = 'gpt-raw'}",
        b"[models]\ndefault = ''",
        b"[models]\ndefault = '  '",
        b"[models]\ndefault = ' gpt-raw'",
        b'[models]\ndefault = "gpt-raw\\n"',
        b"[models]\ndefault = 'default'",
        b"[models]\ndefault = 'https://example.com'",
        b"[models]\n'' = 'gpt-raw'",
        b"[models]\n'bad name' = 'gpt-raw'",
    ],
)
def test_invalid_config_fails_even_for_raw_models(isolated_model_config, location, content):
    paths = isolated_model_config
    for path in paths:
        path.write_text('[models]\ndefault = "gpt-valid"\n')
    paths[location].write_bytes(content)
    with pytest.raises(ModelConfigError) as exc:
        resolve_model("raw-id")
    assert str(paths[location]) in str(exc.value)


@pytest.mark.parametrize("location", [0, 1], ids=["user", "local"])
@pytest.mark.parametrize("failure", ["directory", "dangling-symlink", "permission", "stat"])
def test_filesystem_errors_are_not_silently_skipped(
    isolated_model_config, monkeypatch, location, failure
):
    path = isolated_model_config[location]
    if failure == "directory":
        path.mkdir()
    elif failure == "dangling-symlink":
        path.symlink_to(path.with_name("missing.toml"))
    else:
        path.write_text('[models]\ndefault = "gpt-raw"\n')
        method = "open" if failure == "permission" else "lstat"
        original = getattr(Path, method)

        def fail(selected, *args, **kwargs):
            if selected == path:
                raise PermissionError("test access denied")
            return original(selected, *args, **kwargs)

        monkeypatch.setattr(Path, method, fail)
    with pytest.raises(ModelConfigError, match="Cannot (read|access) model config") as exc:
        load_model_aliases()
    assert str(path) in str(exc.value)


@pytest.mark.parametrize("method", ["home", "cwd"])
def test_config_location_errors_are_explicit(monkeypatch, method):
    def fail():
        raise RuntimeError("test location unavailable")

    monkeypatch.setattr(Path, method, fail)
    with pytest.raises(ModelConfigError, match="Cannot locate model configuration"):
        load_model_aliases()


def test_no_parent_search_or_environment_expansion(isolated_model_config, monkeypatch):
    user, local = isolated_model_config
    local.parent.parent.joinpath("bdk.toml").write_text('[models]\ndefault = "gpt-parent"\n')
    assert load_model_aliases() == {}
    user.write_text('[models]\ndefault = "$MODEL_ID"\n')
    monkeypatch.setenv("MODEL_ID", "gpt-expanded")
    assert resolve_model("default") == "$MODEL_ID"
