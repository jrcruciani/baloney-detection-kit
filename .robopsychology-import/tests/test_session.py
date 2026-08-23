"""Tests for session persistence."""

import json
import os

import pytest

from robopsych.session import SessionState


class TestSessionState:
    def test_create(self):
        sess = SessionState.create(
            provider_name="anthropic",
            model="claude-sonnet-4-6",
            sequence=["2.1", "2.4", "2.5"],
            scenario_name="test",
            task="Review this code",
        )
        assert sess.provider_name == "anthropic"
        assert sess.model == "claude-sonnet-4-6"
        assert sess.sequence == ["2.1", "2.4", "2.5"]
        assert sess.scenario_name == "test"
        assert sess.task == "Review this code"
        assert sess.started_at != ""
        assert sess.completed_steps == []

    def test_remaining_steps_all(self):
        sess = SessionState.create(
            provider_name="openai", model="gpt-4o",
            sequence=["2.1", "2.4", "2.5"],
        )
        assert sess.remaining_steps == ["2.1", "2.4", "2.5"]

    def test_remaining_steps_partial(self):
        sess = SessionState.create(
            provider_name="openai", model="gpt-4o",
            sequence=["2.1", "2.4", "2.5"],
        )
        sess.completed_steps = [
            {"prompt_id": "2.1", "prompt_name": "Layer Map",
             "prompt_text": "test", "response": "resp"},
        ]
        assert sess.remaining_steps == ["2.4", "2.5"]

    def test_remaining_steps_all_done(self):
        sess = SessionState.create(
            provider_name="openai", model="gpt-4o",
            sequence=["2.1", "2.4"],
        )
        sess.completed_steps = [
            {"prompt_id": "2.1", "prompt_name": "a", "prompt_text": "", "response": ""},
            {"prompt_id": "2.4", "prompt_name": "b", "prompt_text": "", "response": ""},
        ]
        assert sess.remaining_steps == []

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "session.json"
        sess = SessionState.create(
            provider_name="anthropic",
            model="claude-sonnet-4-6",
            sequence=["2.1", "2.4"],
            scenario_name="sql-injection",
            task="Review code",
        )
        sess.completed_steps = [
            {"prompt_id": "2.1", "prompt_name": "Layer Map",
             "prompt_text": "diagnose", "response": "analysis result"},
        ]
        sess.messages = [
            {"role": "system", "content": "You are..."},
            {"role": "user", "content": "diagnose"},
            {"role": "assistant", "content": "analysis result"},
        ]
        sess.save(path)

        assert path.exists()
        data = json.loads(path.read_text())
        assert data["provider_name"] == "anthropic"
        assert data["model"] == "claude-sonnet-4-6"
        assert len(data["completed_steps"]) == 1
        assert data["updated_at"] != ""

        loaded = SessionState.load(path)
        assert loaded.provider_name == "anthropic"
        assert loaded.model == "claude-sonnet-4-6"
        assert loaded.remaining_steps == ["2.4"]
        assert len(loaded.messages) == 3
        if os.name == "posix":
            assert path.stat().st_mode & 0o777 == 0o600

    def test_save_updates_timestamp(self, tmp_path):
        path = tmp_path / "session.json"
        sess = SessionState.create(
            provider_name="openai", model="gpt-4o", sequence=["2.1"],
        )
        sess.save(path)
        first_update = sess.updated_at
        sess.save(path)
        assert sess.updated_at >= first_update

    def test_load_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            SessionState.load(tmp_path / "does_not_exist.json")
