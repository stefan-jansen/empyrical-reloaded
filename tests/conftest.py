import pytest
import pandas as pd
import numpy as np
from packaging.version import Version

PANDAS22 = Version(pd.__version__) >= Version("2.2.0")
monthly = "ME" if PANDAS22 else "M"
annual = "YE" if PANDAS22 else "A"


@pytest.fixture(scope="function")
def set_helpers(request):
    rand = np.random.RandomState(1337)
    request.cls.ser_length = 120
    request.cls.window = 12

    request.cls.returns = pd.Series(
        rand.randn(1, 120)[0] / 100.0,
        index=pd.date_range("2000-1-30", periods=120, freq=monthly),
    )

    request.cls.factor_returns = pd.Series(
        rand.randn(1, 120)[0] / 100.0,
        index=pd.date_range("2000-1-30", periods=120, freq=monthly),
    )


@pytest.fixture(scope="session")
def input_data():
    simple_benchmark = pd.Series(
        np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]) / 100,
        index=pd.date_range("2000-1-30", periods=9, freq="D"),
    )

    rand = np.random.RandomState(1337)

    noise = pd.Series(
        rand.normal(0, 0.001, 1000),
        index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
    )

    inv_noise = noise.multiply(-1)

    noise_uniform = pd.Series(
        rand.uniform(-0.01, 0.01, 1000),
        index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
    )

    random_100k = pd.Series(rand.randn(100_000))
    mixed_returns = pd.Series(
        np.array([np.nan, 1.0, 10.0, -4.0, 2.0, 3.0, 2.0, 1.0, -10.0]) / 100,
        index=pd.date_range("2000-1-30", periods=9, freq="D"),
    )

    one = [
        -0.00171614,
        0.01322056,
        0.03063862,
        -0.01422057,
        -0.00489779,
        0.01268925,
        -0.03357711,
        0.01797036,
    ]

    two = [
        0.01846232,
        0.00793951,
        -0.01448395,
        0.00422537,
        -0.00339611,
        0.03756813,
        0.0151531,
        0.03549769,
    ]

    # Sparse noise, same as noise but with np.nan sprinkled in
    replace_nan = rand.choice(noise.index.tolist(), rand.randint(1, 10))
    sparse_noise = noise.replace(replace_nan, np.nan)

    # Flat line tz
    flat_line_1_tz = pd.Series(
        np.linspace(0.01, 0.01, num=1000),
        index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
    )

    # Sparse flat line at 0.01
    # replace_nan = rand.choice(noise.index.tolist(), rand.randint(1, 10))
    sparse_flat_line_1_tz = flat_line_1_tz.replace(replace_nan, np.nan)

    df_index_simple = pd.date_range("2000-1-30", periods=8, freq="D")
    df_index_week = pd.date_range("2000-1-30", periods=8, freq="W")
    df_index_month = pd.date_range("2000-1-30", periods=8, freq=monthly)

    df_week = pd.DataFrame(
        {
            "one": pd.Series(one, index=df_index_week),
            "two": pd.Series(two, index=df_index_week),
        }
    )

    df_month = pd.DataFrame(
        {
            "one": pd.Series(one, index=df_index_month),
            "two": pd.Series(two, index=df_index_month),
        }
    )

    df_simple = pd.DataFrame(
        {
            "one": pd.Series(one, index=df_index_simple),
            "two": pd.Series(two, index=df_index_simple),
        }
    )

    df_week = pd.DataFrame(
        {
            "one": pd.Series(one, index=df_index_week),
            "two": pd.Series(two, index=df_index_week),
        }
    )

    df_month = pd.DataFrame(
        {
            "one": pd.Series(one, index=df_index_month),
            "two": pd.Series(two, index=df_index_month),
        }
    )

    input_one = [
        np.nan,
        0.01322056,
        0.03063862,
        -0.01422057,
        -0.00489779,
        0.01268925,
        -0.03357711,
        0.01797036,
    ]
    input_two = [
        0.01846232,
        0.00793951,
        -0.01448395,
        0.00422537,
        -0.00339611,
        0.03756813,
        0.0151531,
        np.nan,
    ]

    df_index = pd.date_range("2000-1-30", periods=8, freq="D")

    return {
        # Simple benchmark, no drawdown
        "simple_benchmark": simple_benchmark,
        "simple_benchmark_w_noise": simple_benchmark
        + rand.normal(0, 0.001, len(simple_benchmark)),
        "simple_benchmark_df": simple_benchmark.rename("returns").to_frame(),
        # All positive returns, small variance
        "positive_returns": pd.Series(
            np.array([1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]) / 100,
            index=pd.date_range("2000-1-30", periods=9, freq="D"),
        ),
        # All negative returns
        "negative_returns": pd.Series(
            np.array([0.0, -6.0, -7.0, -1.0, -9.0, -2.0, -6.0, -8.0, -5.0]) / 100,
            index=pd.date_range("2000-1-30", periods=9, freq="D"),
        ),
        # All negative returns
        "all_negative_returns": pd.Series(
            np.array([-2.0, -6.0, -7.0, -1.0, -9.0, -2.0, -6.0, -8.0, -5.0]) / 100,
            index=pd.date_range("2000-1-30", periods=9, freq="D"),
        ),
        # Positive and negative returns with max drawdown
        "mixed_returns": mixed_returns,
        # Weekly returns
        "weekly_returns": pd.Series(
            np.array([0.0, 1.0, 10.0, -4.0, 2.0, 3.0, 2.0, 1.0, -10.0]) / 100,
            index=pd.date_range("2000-1-30", periods=9, freq="W"),
        ),
        # Monthly returns
        "monthly_returns": pd.Series(
            np.array([0.0, 1.0, 10.0, -4.0, 2.0, 3.0, 2.0, 1.0, -10.0]) / 100,
            index=pd.date_range("2000-1-30", periods=9, freq=monthly),
        ),
        # Series of length 1
        "one_return": pd.Series(
            np.array([1.0]) / 100,
            index=pd.date_range("2000-1-30", periods=1, freq="D"),
        ),
        "udu_returns": pd.Series(
            np.array([10, -10, 10]) / 100,
            index=pd.date_range("2000-1-30", periods=3, freq="D"),
        ),
        # Empty series
        "empty_returns": pd.Series(
            np.array([]) / 100,
            index=pd.date_range("2000-1-30", periods=0, freq="D"),
        ),
        # Random noise
        "noise": noise,
        "noise_uniform": noise_uniform,
        "random_100k": random_100k,
        # Random noise inv
        "inv_noise": inv_noise,
        # Flat line
        "flat_line_0": pd.Series(
            np.linspace(0, 0, num=1000),
            index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
        ),
        "flat_line_1": pd.Series(
            np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]) / 100,
            index=pd.date_range("2000-1-30", periods=9, freq="D"),
        ),
        # Flat line with tz
        "flat_line_1_tz": pd.Series(
            np.linspace(0.01, 0.01, num=1000),
            index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
        ),
        "flat_line_yearly": pd.Series(
            np.array([3.0, 3.0, 3.0]) / 100,
            index=pd.date_range("2000-1-30", periods=3, freq=annual),
        ),
        # Positive line
        "pos_line": pd.Series(
            np.linspace(0, 1, num=1000),
            index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
        ),
        # Negative line
        "neg_line": pd.Series(
            np.linspace(0, -1, num=1000),
            index=pd.date_range("2000-1-30", periods=1000, freq="D", tz="UTC"),
        ),
        # Sparse noise, same as noise but with np.nan sprinkled in
        "sparse_noise": sparse_noise,
        # Sparse flat line at 0.01
        "sparse_flat_line_1_tz": sparse_flat_line_1_tz,
        "one": one,
        "two": two,
        "df_index_simple": df_index_simple,
        "df_index_week": df_index_week,
        "df_index_month": df_index_month,
        "df_simple": df_simple,
        "df_week": df_week,
        "df_month": df_month,
        "df_empty": pd.DataFrame(),
        "df_input": pd.DataFrame(
            {
                "one": pd.Series(input_one, index=df_index),
                "two": pd.Series(input_two, index=df_index),
            }
        ),
    }


@pytest.fixture
def returns(input_data, request):
    name = request.param
    if name not in input_data.keys():
        return eval(name, input_data)
    return input_data[name]


required_return = returns
benchmark = returns
risk_free = returns
factor_returns = returns
add_noise = returns
prices = returns


@pytest.fixture(scope="session")
def expected_data():
    expected_0_one = [
        0.000000,
        0.013221,
        0.044264,
        0.029414,
        0.024372,
        0.037371,
        0.002539,
        0.020555,
    ]
    expected_0_two = [
        0.018462,
        0.026548,
        0.011680,
        0.015955,
        0.012504,
        0.050542,
        0.066461,
        0.066461,
    ]

    expected_100_one = [
        100.000000,
        101.322056,
        104.426424,
        102.941421,
        102.437235,
        103.737087,
        100.253895,
        102.055494,
    ]
    expected_100_two = [
        101.846232,
        102.654841,
        101.167994,
        101.595466,
        101.250436,
        105.054226,
        106.646123,
        106.646123,
    ]

    mixed_returns_gpd_risk = [
        0.1,
        0.10001255835838491,
        1.5657360018514067e-06,
        0.4912526273742347,
        0.59126595492541179,
    ]

    negative_returns_gpd_risk = [
        0.05,
        0.068353586736348199,
        9.4304947982121171e-07,
        0.34511639904932639,
        0.41347032855617882,
    ]

    df_index = pd.date_range("2000-1-30", periods=8, freq="D")

    df_0_expected = pd.DataFrame(
        {
            "one": pd.Series(expected_0_one, index=df_index),
            "two": pd.Series(expected_0_two, index=df_index),
        }
    )

    df_100_expected = pd.DataFrame(
        {
            "one": pd.Series(expected_100_one, index=df_index),
            "two": pd.Series(expected_100_two, index=df_index),
        }
    )
    return {
        "df_empty": pd.DataFrame(),
        "df_0_expected": df_0_expected,
        "df_100_expected": df_100_expected,
        "mixed_returns_expected_gpd_risk_result": mixed_returns_gpd_risk,
        "negative_returns_expected_gpd_risk_result": negative_returns_gpd_risk,
    }


@pytest.fixture
def expected(expected_data, request):
    name = request.param
    if name not in expected_data.keys():
        return eval(name)
    return expected_data[name]
