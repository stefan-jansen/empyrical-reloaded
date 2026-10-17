from types import SimpleNamespace

import pytest

from empyrical import utils


def test_yahoo_returns_missing_optional_dependency_has_install_guidance(monkeypatch):
    monkeypatch.setattr(utils, "yf", None)
    with pytest.raises(ImportError, match="empyrical-reloaded\\[yfinance\\]"):
        utils.get_symbol_returns_from_yahoo("SPY")


def test_yahoo_returns_preserves_original_provider_exception(monkeypatch):
    original = ConnectionError("provider unavailable")

    def download(*args, **kwargs):
        raise original

    monkeypatch.setattr(utils, "yf", SimpleNamespace(download=download))
    with pytest.warns(UserWarning, match="Yahoo Finance read failed"):
        with pytest.raises(ConnectionError, match="provider unavailable") as observed:
            utils.get_symbol_returns_from_yahoo("SPY")
    assert observed.value is original
