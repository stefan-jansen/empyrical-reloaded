import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from empyrical import utils


@pytest.mark.parametrize("period_index", [True, False])
def test_fama_french_daily_provider_dates_remain_utc(period_index, monkeypatch):
    record = json.loads(
        (
            Path(__file__).parent / "test_data/famafrench-provider-response.json"
        ).read_text()
    )

    def read_factors(dataset, data_source, start, end):
        assert data_source == "famafrench"
        assert str(start) == "2024-01-02"
        assert str(end) == "2024-01-05"
        frame = record["records"][dataset]
        index = pd.PeriodIndex(frame["index"], freq="D", name="Date")
        if not period_index:
            index = index.to_timestamp()
        return {0: pd.DataFrame(frame["data"], index=index, columns=frame["columns"])}

    monkeypatch.setattr(utils, "web", SimpleNamespace(DataReader=read_factors))
    result = utils.get_fama_french(start="2024-01-02", end="2024-01-05")
    expected = pd.DataFrame(
        [
            [-0.007, -0.0055, 0.0079, 0.0002, -0.0211],
            [-0.0101, -0.0194, -0.001, 0.0002, 0.0059],
            [-0.0033, 0.0021, 0.0009, 0.0002, -0.003],
            [0.0015, -0.0081, 0.0063, 0.0002, -0.0025],
        ],
        columns=["Mkt-RF", "SMB", "HML", "RF", "Mom"],
        index=pd.date_range("2024-01-02", periods=4, tz="UTC", name="Date"),
    )
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize("end_kwargs", [{}, {"end": None}, {"end": "2024-01-03"}])
def test_fama_french_default_end_remains_usable_by_provider(end_kwargs, monkeypatch):
    record = json.loads(
        (
            Path(__file__).parent / "test_data/famafrench-provider-response.json"
        ).read_text()
    )

    def read_factors(dataset, data_source, start, end):
        frame = record["records"][dataset]
        index = pd.PeriodIndex(frame["index"], freq="D", name="Date")
        data = pd.DataFrame(frame["data"], index=index, columns=frame["columns"])
        provider_end = pd.Timestamp("2024-01-05") if end is None else pd.Timestamp(end)
        return {0: data.truncate(pd.Timestamp(start), provider_end)}

    monkeypatch.setattr(utils, "web", SimpleNamespace(DataReader=read_factors))
    result = utils.get_fama_french(start="2024-01-02", **end_kwargs)
    expected_dates = ["2024-01-02", "2024-01-03"]
    if end_kwargs.get("end") is None:
        expected_dates += ["2024-01-04", "2024-01-05"]
    assert result.index.tolist() == [
        pd.Timestamp(date, tz="UTC") for date in expected_dates
    ]
    assert result.columns.tolist() == ["Mkt-RF", "SMB", "HML", "RF", "Mom"]
    assert result.notna().all().all()
