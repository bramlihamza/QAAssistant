"""Tests unitaires — memory/short_term.py"""

import pytest
from memory.short_term import store, recall, clear, size, MAX_MEMORY


@pytest.fixture(autouse=True)
def reset_memory():
    """Remet la mémoire à zéro avant chaque test."""
    clear()
    yield
    clear()


# ── store / recall ────────────────────────────────────────────────────────────

def test_store_and_recall_single():
    store({"role": "user", "content": "Bonjour"})
    msgs = recall(limit=1)
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Bonjour"
    assert msgs[0]["role"] == "user"


def test_recall_returns_most_recent():
    store({"role": "user", "content": "msg1"})
    store({"role": "assistant", "content": "msg2"})
    store({"role": "user", "content": "msg3"})
    msgs = recall(limit=2)
    assert len(msgs) == 2
    assert msgs[-1]["content"] == "msg3"
    assert msgs[0]["content"] == "msg2"


def test_recall_limit_zero():
    store({"role": "user", "content": "test"})
    assert recall(limit=0) == []


def test_recall_limit_exceeds_size():
    store({"role": "user", "content": "seul"})
    msgs = recall(limit=100)
    assert len(msgs) == 1


# ── MAX_MEMORY ────────────────────────────────────────────────────────────────

def test_memory_capped_at_max():
    for i in range(MAX_MEMORY + 5):
        store({"role": "user", "content": f"msg {i}"})
    assert size() == MAX_MEMORY


def test_memory_keeps_most_recent_after_overflow():
    for i in range(MAX_MEMORY + 3):
        store({"role": "user", "content": f"msg {i}"})
    msgs = recall(limit=MAX_MEMORY)
    contents = [m["content"] for m in msgs]
    # Les premiers messages doivent avoir été supprimés
    assert "msg 0" not in contents
    assert f"msg {MAX_MEMORY + 2}" in contents


# ── clear / size ──────────────────────────────────────────────────────────────

def test_clear_empties_memory():
    store({"role": "user", "content": "temp"})
    clear()
    assert size() == 0
    assert recall() == []


def test_size_increments():
    assert size() == 0
    store({"role": "user", "content": "a"})
    assert size() == 1
    store({"role": "assistant", "content": "b"})
    assert size() == 2


# ── Validation de format ──────────────────────────────────────────────────────

def test_store_ignores_invalid_message(caplog):
    import logging
    with caplog.at_level(logging.WARNING, logger="memory.short_term"):
        store("pas un dict")
        store({"role": "user"})          # manque 'content'
        store({"content": "sans role"})  # manque 'role'
    assert size() == 0
