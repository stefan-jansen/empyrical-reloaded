"""Compare five columnwise metric adapters without claiming full API compatibility."""

import json
import platform
from importlib.metadata import version

import numpy as np
import pandas as pd

import empyrical as ep
from ml4t.diagnostic.evaluation import portfolio_analysis as destination
from ml4t.diagnostic.metrics import periodic_sharpe_ratio, periodic_sortino_ratio


def main() -> None:
    prices = pd.DataFrame(
        {
            "strategy_a": [100.0, 101.0, 99.0, 103.0, 102.0],
            "strategy_b": [50.0, 49.0, 51.0, 50.0, 52.0],
        },
        index=pd.date_range("2024-01-02", periods=5, freq="B", tz="UTC", name="date"),
    )
    returns = ep.simple_returns(prices)
    periods_per_year = 52
    periodic_rate = 0.0001
    calculations = {
        "annual_return": (
            lambda frame: ep.annual_return(frame, annualization=periods_per_year),
            lambda frame: frame.apply(
                lambda column: destination.annual_return(
                    column, periods_per_year=periods_per_year
                )
            ),
        ),
        "annual_volatility": (
            lambda frame: ep.annual_volatility(frame, annualization=periods_per_year),
            lambda frame: frame.apply(
                lambda column: destination.annual_volatility(
                    column, periods_per_year=periods_per_year
                )
            ).to_numpy(),
        ),
        "max_drawdown": (
            ep.max_drawdown,
            lambda frame: frame.apply(destination.max_drawdown),
        ),
        "sharpe_ratio": (
            lambda frame: ep.sharpe_ratio(
                frame, risk_free=periodic_rate, annualization=periods_per_year
            ),
            lambda frame: frame.apply(
                lambda column: periodic_sharpe_ratio(
                    column,
                    periodic_risk_free_rate=periodic_rate,
                    annualization_factor=periods_per_year,
                )
            ).to_numpy(),
        ),
        "sortino_ratio": (
            lambda frame: ep.sortino_ratio(
                frame, required_return=periodic_rate, annualization=periods_per_year
            ),
            lambda frame: frame.apply(
                lambda column: periodic_sortino_ratio(
                    column,
                    periodic_risk_free_rate=periodic_rate,
                    annualization_factor=periods_per_year,
                )
            ),
        ),
    }
    results = []
    for case in ("finite", "missing_observation"):
        frame = returns.copy()
        if case == "missing_observation":
            frame.iloc[1, 0] = np.nan
        for name, (legacy, adapted) in calculations.items():
            expected = legacy(frame)
            actual = adapted(frame)
            if type(actual) is not type(expected):
                raise AssertionError((name, type(actual), type(expected)))
            if isinstance(expected, pd.Series):
                pd.testing.assert_series_equal(actual, expected, rtol=1e-10, atol=1e-12)
            else:
                np.testing.assert_allclose(
                    actual, expected, rtol=1e-10, atol=1e-12, equal_nan=True
                )
            results.append({"case": case, "metric": name, "status": "matching"})
    flattened = destination.annual_return(returns, periods_per_year=periods_per_year)
    if (
        np.asarray(flattened).shape
        == np.asarray(ep.annual_return(returns, annualization=periods_per_year)).shape
    ):
        raise AssertionError(
            "The unadapted DataFrame control no longer detects flattening"
        )
    print(
        json.dumps(
            {
                "scope": "Ten examples, five scalar metrics, two columns; not full API parity",
                "python": platform.python_version(),
                "versions": {
                    name: version(name)
                    for name in (
                        "empyrical-reloaded",
                        "ml4t-diagnostic",
                        "numpy",
                        "pandas",
                    )
                },
                "periods_per_year": periods_per_year,
                "periodic_rf_or_mar": periodic_rate,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
