"""
conftest.py — Fixtures partagées entre tous les tests.

Garantit un état propre (mémoire vidée, métriques réinitialisées)
avant chaque test qui en a besoin.
"""

import pytest
import memory.short_term as _mem


@pytest.fixture(autouse=False)
def clean_memory():
    """Vide la mémoire courte avant ET après chaque test qui l'utilise."""
    _mem.clear()
    yield
    _mem.clear()
