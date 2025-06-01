from copy import copy
from operator import attrgetter

import numpy as np
import pandas as pd
from pandas.core.generic import NDFrame
from scipy import stats
from functools import wraps
import pytest
import empyrical
import empyrical.utils as emutils
from empyrical.stats import (
    aggregate_returns,
    alpha_beta,
    up_alpha_beta,
    down_alpha_beta,
)

DECIMAL_PLACES = 8

rand = np.random.RandomState(1337)


class BaseTestClass:
    def assert_indexes_match(self, result, expected):
        """
        Assert that two pandas objects have the same indices.

        This is a method instead of a free function so that we can override it
        to be a no-op in suites like TestStatsArrays that unwrap pandas objects
        into ndarrays.
        """
        pd.testing.assert_index_equal(result.index, expected.index)

        if isinstance(result, pd.DataFrame) and isinstance(expected, pd.DataFrame):
            pd.testing.assert_index_equal(result.columns, expected.columns)


class TestStats(BaseTestClass):
    @pytest.mark.parametrize(
        "prices, expected",
        [
            # Constant price implies zero returns,
            # and linearly increasing prices imples returns like 1/n
            ("flat_line_1", [0.0] * (9 - 1)),
            ("pos_line", [np.inf] + [1 / n for n in range(1, 999)]),
        ],
        indirect=["prices"],
    )
    def test_simple_returns(self, prices, expected):
        simple_returns = self.empyrical.simple_returns(prices)
        np.testing.assert_almost_equal(np.array(simple_returns), expected, 4)
        self.assert_indexes_match(simple_returns, prices.iloc[1:])

    @pytest.mark.parametrize(
        "returns, starting_value, expected",
        [
            ("empty_returns", 0, []),
            (
                "mixed_returns",
                0,
                [
                    0.0,
                    0.01,
                    0.111,
                    0.066559,
                    0.08789,
                    0.12052,
                    0.14293,
                    0.15436,
                    0.03893,
                ],
            ),
            (
                "mixed_returns",
                100,
                [
                    100.0,
                    101.0,
                    111.1,
                    106.65599,
                    108.78912,
                    112.05279,
                    114.29384,
                    115.43678,
                    103.89310,
                ],
            ),
            (
                "negative_returns",
                0,
                [
                    0.0,
                    -0.06,
                    -0.1258,
                    -0.13454,
                    -0.21243,
                    -0.22818,
                    -0.27449,
                    -0.33253,
                    -0.36590,
                ],
            ),
        ],
        indirect=["returns"],
    )
    def test_cum_returns(self, returns, starting_value, expected):
        cum_returns = self.empyrical.cum_returns(
            returns,
            starting_value=starting_value,
        )
        for i in range(returns.size):
            if isinstance(expected, pd.Series):
                expected_val = expected.iloc[i]
            else:
                expected_val = expected[i]
            if isinstance(cum_returns, pd.Series):
                ret_val = cum_returns.iloc[i]
            else:
                ret_val = cum_returns[i]

            np.testing.assert_almost_equal(ret_val, expected_val, 4)

        self.assert_indexes_match(cum_returns, returns)

    @pytest.mark.parametrize(
        "returns, starting_value, expected",
        [
            ("empty_returns", 0, np.nan),
            ("one_return", 0, 0.01),
            ("mixed_returns", 0, 0.03893),
            ("mixed_returns", 100, 103.89310),
            ("negative_returns", 0, -0.36590),
        ],
        indirect=["returns"],
    )
    def test_cum_returns_final(self, returns, starting_value, expected):
        cum_returns_final = self.empyrical.cum_returns_final(
            returns,
            starting_value=starting_value,
        )
        np.testing.assert_almost_equal(cum_returns_final, expected, 4)

    @pytest.mark.parametrize(
        "returns, convert_to, expected",
        [
            (
                "simple_benchmark",
                empyrical.WEEKLY,
                [0.0, 0.040604010000000024, 0.0],
            ),
            (
                "simple_benchmark",
                empyrical.MONTHLY,
                [0.01, 0.03030099999999991],
            ),
            ("simple_benchmark", empyrical.QUARTERLY, [0.04060401]),
            ("simple_benchmark", empyrical.YEARLY, [0.040604010000000024]),
            (
                "weekly_returns",
                empyrical.MONTHLY,
                [0.0, 0.087891200000000058, -0.04500459999999995],
            ),
            ("weekly_returns", empyrical.YEARLY, [0.038931091700480147]),
            ("monthly_returns", empyrical.YEARLY, [0.038931091700480147]),
            (
                "monthly_returns",
                empyrical.QUARTERLY,
                [
                    0.11100000000000021,
                    0.008575999999999917,
                    -0.072819999999999996,
                ],
            ),
        ],
        indirect=["returns"],
    )
    def test_aggregate_returns(self, returns, convert_to, expected):
        returns = aggregate_returns(returns, convert_to).values.tolist()
        for i, v in enumerate(returns):
            np.testing.assert_almost_equal(v, expected[i], DECIMAL_PLACES)

    @pytest.mark.parametrize(
        "returns, expected",
        [
            ("empty_returns", np.nan),
            ("one_return", 0.0),
            ("simple_benchmark", 0.0),
            ("mixed_returns", -0.1),
            ("positive_returns", -0.0),
            # negative returns means the drawdown is just the returns
            ("negative_returns", -0.36590730),
            (
                "all_negative_returns",
                -0.378589157,
            ),
            (
                "udu_returns",
                -0.10,
            ),
        ],
        indirect=["returns"],
    )
    def test_max_drawdown(self, returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.max_drawdown(returns),
            expected,
            DECIMAL_PLACES,
        )

    # Maximum drawdown is always less than or equal to zero. Translating
    # returns by a positive constant should increase the maximum
    # drawdown to a maximum of zero. Translating by a negative constant
    # decreases the maximum drawdown.
    @pytest.mark.parametrize(
        "returns, constant",
        [
            ("noise", 0.0001),
            ("noise", 0.001),
            ("noise_uniform", 0.01),
            ("noise_uniform", 0.1),
        ],
        indirect=["returns"],
    )
    def test_max_drawdown_translation(self, returns, constant):
        depressed_returns = returns - constant
        raised_returns = returns + constant
        max_dd = self.empyrical.max_drawdown(returns)
        depressed_dd = self.empyrical.max_drawdown(depressed_returns)
        raised_dd = self.empyrical.max_drawdown(raised_returns)
        assert max_dd <= raised_dd
        assert depressed_dd <= max_dd

    @pytest.mark.parametrize(
        "returns, period, expected",
        [
            ("mixed_returns", empyrical.DAILY, 1.9135925373194231),
            ("weekly_returns", empyrical.WEEKLY, 0.24690830513998208),
            ("monthly_returns", empyrical.MONTHLY, 0.052242061386048144),
        ],
        indirect=["returns"],
    )
    def test_annual_ret(self, returns, period, expected):
        np.testing.assert_almost_equal(
            self.empyrical.annual_return(returns, period=period),
            expected,
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, period, expected",
        [
            ("flat_line_1_tz", empyrical.DAILY, 0.0),
            ("mixed_returns", empyrical.DAILY, 0.9136465399704637),
            ("weekly_returns", empyrical.WEEKLY, 0.38851569394870583),
            ("monthly_returns", empyrical.MONTHLY, 0.18663690238892558),
        ],
        indirect=["returns"],
    )
    def test_annual_volatility(self, returns, period, expected):
        np.testing.assert_almost_equal(
            self.empyrical.annual_volatility(returns, period=period),
            expected,
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, period, expected",
        [
            ("empty_returns", empyrical.DAILY, np.nan),
            ("one_return", empyrical.DAILY, np.nan),
            ("mixed_returns", empyrical.DAILY, 19.135925373194233),
            ("weekly_returns", empyrical.WEEKLY, 2.4690830513998208),
            ("monthly_returns", empyrical.MONTHLY, 0.52242061386048144),
        ],
        indirect=["returns"],
    )
    def test_calmar(self, returns, period, expected):
        np.testing.assert_almost_equal(
            self.empyrical.calmar_ratio(returns, period=period),
            expected,
            DECIMAL_PLACES,
        )

    # Regression tests for omega ratio
    @pytest.mark.parametrize(
        "returns, risk_free, required_return, expected",
        [
            ("empty_returns", "0.0", 0.0, np.nan),
            ("one_return", "0.0", 0.0, np.nan),
            ("mixed_returns", "0.0", 10.0, 0.83354263497557934),
            ("mixed_returns", "0.0", -10.0, np.nan),
            ("mixed_returns", "flat_line_1", 0.0, 0.8125),
            ("positive_returns", "0.01", 0.0, np.nan),
            ("positive_returns", "0.011", 0.0, 1.125),
            ("positive_returns", "0.02", 0.0, 0.0),
            ("negative_returns", "0.01", 0.0, 0.0),
        ],
        indirect=["returns", "risk_free"],
    )
    def test_omega(self, returns, risk_free, required_return, expected):
        np.testing.assert_almost_equal(
            self.empyrical.omega_ratio(
                returns, risk_free=risk_free, required_return=required_return
            ),
            expected,
            DECIMAL_PLACES,
        )

    # As the required return increases (but is still less than the maximum
    # return), omega decreases
    @pytest.mark.parametrize(
        "returns, required_return_less, required_return_more",
        [
            ("noise_uniform", 0.0, 0.001),
            ("noise", 0.001, 0.002),
        ],
        indirect=["returns"],
    )
    def test_omega_returns(self, returns, required_return_less, required_return_more):
        assert self.empyrical.omega_ratio(
            returns, required_return_less
        ) > self.empyrical.omega_ratio(returns, required_return_more)

    # Regressive sharpe ratio tests
    @pytest.mark.parametrize(
        "returns, risk_free, expected",
        [
            ("empty_returns", "0.0", np.nan),
            ("one_return", "0.0", np.nan),
            ("mixed_returns", "mixed_returns", np.nan),
            ("mixed_returns", "0.0", 1.7238613961706866),
            ("mixed_returns", "simple_benchmark", 0.34111411441060574),
            ("positive_returns", "0.0", 52.915026221291804),
            ("negative_returns", "0.0", -24.406808633910085),
            ("flat_line_1", "0.0", np.inf),
        ],
        indirect=["returns", "risk_free"],
    )
    def test_sharpe_ratio(self, returns, risk_free, expected):
        np.testing.assert_almost_equal(
            self.empyrical.sharpe_ratio(returns, risk_free=risk_free),
            expected,
            DECIMAL_PLACES,
        )

    # Translating the returns and required returns by the same amount
    # does not change the sharpe ratio.
    @pytest.mark.parametrize(
        "returns, required_return, translation",
        [
            ("noise_uniform", 0, 0.005),
            ("noise_uniform", 0.005, 0.005),
        ],
        indirect=["returns"],
    )
    def test_sharpe_translation_same(self, returns, required_return, translation):
        sr = self.empyrical.sharpe_ratio(returns, required_return)
        sr_depressed = self.empyrical.sharpe_ratio(
            returns - translation, required_return - translation
        )
        sr_raised = self.empyrical.sharpe_ratio(
            returns + translation, required_return + translation
        )
        np.testing.assert_almost_equal(sr, sr_depressed, DECIMAL_PLACES)
        np.testing.assert_almost_equal(sr, sr_raised, DECIMAL_PLACES)

    # Translating the returns and required returns by the different amount
    # yields different sharpe ratios
    @pytest.mark.parametrize(
        "returns, required_return, translation_returns, translation_required",
        [
            ("noise_uniform", 0, 0.0002, 0.0001),
            ("noise_uniform", 0.005, 0.0001, 0.0002),
        ],
        indirect=["returns"],
    )
    def test_sharpe_translation_diff(
        self,
        returns,
        required_return,
        translation_returns,
        translation_required,
    ):
        sr = self.empyrical.sharpe_ratio(returns, required_return)
        sr_depressed = self.empyrical.sharpe_ratio(
            returns - translation_returns,
            required_return - translation_required,
        )
        sr_raised = self.empyrical.sharpe_ratio(
            returns + translation_returns,
            required_return + translation_required,
        )
        assert sr != sr_depressed
        assert sr != sr_raised

    # Translating the required return inversely affects the sharpe ratio.
    @pytest.mark.parametrize(
        "returns, required_return, translation",
        [("noise_uniform", 0, 0.005), ("noise", 0, 0.005)],
        indirect=["returns"],
    )
    def test_sharpe_translation_1(self, returns, required_return, translation):
        sr = self.empyrical.sharpe_ratio(returns, required_return)
        sr_depressed = self.empyrical.sharpe_ratio(
            returns, required_return - translation
        )
        sr_raised = self.empyrical.sharpe_ratio(returns, required_return + translation)
        assert sr_depressed > sr
        assert sr > sr_raised

    # Returns of a wider range or larger standard deviation decreases the
    # sharpe ratio
    @pytest.mark.parametrize("small, large", [(0.001, 0.002), (0.01, 0.02)])
    def test_sharpe_noise(self, small, large):
        index = pd.date_range("2000-1-30", periods=1000, freq="D")
        smaller_normal = pd.Series(
            rand.normal(0.01, small, 1000),
            index=index,
        )
        larger_normal = pd.Series(
            rand.normal(0.01, large, 1000),
            index=index,
        )
        assert self.empyrical.sharpe_ratio(
            smaller_normal, 0.001
        ) > self.empyrical.sharpe_ratio(larger_normal, 0.001)

    # Regressive downside risk tests
    @pytest.mark.parametrize(
        "returns, required_return, period, expected",
        [
            ("empty_returns", "0.0", empyrical.DAILY, np.nan),
            ("one_return", "0.0", empyrical.DAILY, 0.0),
            ("mixed_returns", "mixed_returns", empyrical.DAILY, 0.0),
            ("mixed_returns", "0.0", empyrical.DAILY, 0.60448325038829653),
            ("mixed_returns", "0.1", empyrical.DAILY, 1.7161730681956295),
            ("weekly_returns", "0.0", empyrical.WEEKLY, 0.25888650451930134),
            ("weekly_returns", "0.1", empyrical.WEEKLY, 0.7733045971672482),
            ("monthly_returns", "0.0", empyrical.MONTHLY, 0.1243650540411842),
            ("monthly_returns", "0.1", empyrical.MONTHLY, 0.37148351242013422),
            (
                "df_simple",
                "0.0",
                empyrical.DAILY,
                pd.Series(
                    [0.20671788246185202, 0.083495680595704475],
                    index=["one", "two"],
                ),
            ),
            (
                "df_week",
                "0.0",
                empyrical.WEEKLY,
                pd.Series(
                    [0.093902996054410062, 0.037928477556776516],
                    index=["one", "two"],
                ),
            ),
            (
                "df_month",
                "0.0",
                empyrical.MONTHLY,
                pd.Series(
                    [0.045109540184877193, 0.018220251263412916],
                    index=["one", "two"],
                ),
            ),
        ],
        indirect=["returns", "required_return"],
    )
    def test_downside_risk(self, returns, required_return, period, expected):
        downside_risk = self.empyrical.downside_risk(
            returns, required_return=required_return, period=period
        )
        if isinstance(downside_risk, float):
            np.testing.assert_almost_equal(downside_risk, expected, DECIMAL_PLACES)
        else:
            for i in range(downside_risk.size):
                if isinstance(expected, pd.Series):
                    expected_val = expected.iloc[i]
                else:
                    expected_val = expected[i]
                if isinstance(downside_risk, pd.Series):
                    down_val = downside_risk.iloc[i]
                else:
                    down_val = downside_risk[i]
                np.testing.assert_almost_equal(down_val, expected_val, DECIMAL_PLACES)

    # As a higher percentage of returns are below the required return,
    # downside risk increases.
    @pytest.mark.parametrize(
        "add_noise, returns",
        [("noise", "flat_line_0"), ("noise_uniform", "flat_line_0")],
        indirect=True,
    )
    def test_downside_risk_noisy(self, add_noise, returns):
        noisy_returns_1 = add_noise[0:250].add(returns[250:], fill_value=0)
        noisy_returns_2 = add_noise[0:500].add(returns[500:], fill_value=0)
        noisy_returns_3 = add_noise[0:750].add(returns[750:], fill_value=0)
        dr_1 = self.empyrical.downside_risk(noisy_returns_1, returns)
        dr_2 = self.empyrical.downside_risk(noisy_returns_2, returns)
        dr_3 = self.empyrical.downside_risk(noisy_returns_3, returns)
        assert dr_1 <= dr_2
        assert dr_2 <= dr_3

    # Downside risk increases as the required_return increases
    @pytest.mark.parametrize(
        "returns, required_return",
        [("noise", 0.005), ("noise_uniform", 0.005)],
        indirect=["returns"],
    )
    def test_downside_risk_trans(self, returns, required_return):
        dr_0 = self.empyrical.downside_risk(returns, -required_return)
        dr_1 = self.empyrical.downside_risk(returns, 0)
        dr_2 = self.empyrical.downside_risk(returns, required_return)
        assert dr_0 <= dr_1
        assert dr_1 <= dr_2

    # Downside risk for a random series with a required return of 0 is higher
    # for datasets with larger standard deviation
    @pytest.mark.parametrize(
        "smaller_std, larger_std", [(0.001, 0.002), (0.001, 0.01), (0, 0.001)]
    )
    def test_downside_risk_std(self, smaller_std, larger_std):
        less_noise = pd.Series(
            (
                rand.normal(0, smaller_std, 1000)
                if smaller_std != 0
                else np.full(1000, 0)
            ),
            index=pd.date_range("2000-1-30", periods=1000, freq="D"),
        )
        more_noise = pd.Series(
            (rand.normal(0, larger_std, 1000) if larger_std != 0 else np.full(1000, 0)),
            index=pd.date_range("2000-1-30", periods=1000, freq="D"),
        )
        assert self.empyrical.downside_risk(less_noise) < self.empyrical.downside_risk(
            more_noise
        )

    # Regressive sortino ratio tests
    @pytest.mark.parametrize(
        "returns, required_return, period, expected",
        [
            ("empty_returns", "0.0", empyrical.DAILY, np.nan),
            ("one_return", "0.0", empyrical.DAILY, np.nan),
            ("mixed_returns", "mixed_returns", empyrical.DAILY, np.nan),
            ("mixed_returns", "0.0", empyrical.DAILY, 2.605531251673693),
            (
                "mixed_returns",
                "flat_line_1",
                empyrical.DAILY,
                -1.3934779588919977,
            ),
            ("positive_returns", "0.0", empyrical.DAILY, np.inf),
            ("negative_returns", "0.0", empyrical.DAILY, -13.532743075043401),
            ("simple_benchmark", "0.0", empyrical.DAILY, np.inf),
            ("weekly_returns", "0.0", empyrical.WEEKLY, 1.1158901056866439),
            ("monthly_returns", "0.0", empyrical.MONTHLY, 0.53605626741889756),
            (
                "df_simple",
                "0.0",
                empyrical.DAILY,
                pd.Series(
                    [3.0639640966566306, 38.090963117002495],
                    index=["one", "two"],
                ),
            ),
            (
                "df_week",
                "0.0",
                empyrical.WEEKLY,
                pd.Series(
                    [1.3918264112070571, 17.303077589064618],
                    index=["one", "two"],
                ),
            ),
            (
                "df_month",
                "0.0",
                empyrical.MONTHLY,
                pd.Series(
                    [0.6686117809312383, 8.3121296084492844],
                    index=["one", "two"],
                ),
            ),
        ],
        indirect=["returns", "required_return"],
    )
    def test_sortino(self, returns, required_return, period, expected):
        sortino_ratio = self.empyrical.sortino_ratio(
            returns, required_return=required_return, period=period
        )
        if isinstance(sortino_ratio, float):
            np.testing.assert_almost_equal(sortino_ratio, expected, DECIMAL_PLACES)
        else:
            for i in range(sortino_ratio.size):
                if isinstance(expected, pd.Series):
                    expected_val = expected.iloc[i]
                else:
                    expected_val = expected[i]
                if isinstance(sortino_ratio, pd.Series):
                    sortino_val = sortino_ratio.iloc[i]
                else:
                    sortino_val = sortino_ratio[i]

                np.testing.assert_almost_equal(
                    sortino_val, expected_val, DECIMAL_PLACES
                )

    # A large Sortino ratio indicates there is a low probability of a large
    # loss, therefore randomly changing values larger than required return to a
    # loss of 25 percent decreases the ratio.
    @pytest.mark.parametrize(
        "returns, required_return",
        [
            ("noise_uniform", "0"),
            ("noise", "0"),
        ],
        indirect=True,
    )
    def test_sortino_add_noise(self, returns, required_return):
        # Don't mutate global test state
        returns = returns.copy()
        sr_1 = self.empyrical.sortino_ratio(returns, required_return)
        upside_values = returns[returns > required_return].index.tolist()
        # Add large losses at random upside locations
        loss_loc = rand.choice(upside_values, 2)
        returns[loss_loc[0]] = -0.01
        sr_2 = self.empyrical.sortino_ratio(returns, required_return)
        returns[loss_loc[1]] = -0.01
        sr_3 = self.empyrical.sortino_ratio(returns, required_return)
        assert sr_1 > sr_2
        assert sr_2 > sr_3

    # Similarly, randomly increasing some values below the required return to
    # the required return increases the ratio.
    @pytest.mark.parametrize(
        "returns, required_return",
        [("noise_uniform", "0"), ("noise", "0")],
        indirect=True,
    )
    def test_sortino_sub_noise(self, returns, required_return):
        # Don't mutate global test state
        returns = returns.copy()
        sr_1 = self.empyrical.sortino_ratio(returns, required_return)
        downside_values = returns[returns < required_return].index.tolist()
        # Replace some values below the required return to the required return
        loss_loc = rand.choice(downside_values, 2)
        returns[loss_loc[0]] = required_return
        sr_2 = self.empyrical.sortino_ratio(returns, required_return)
        returns[loss_loc[1]] = required_return
        sr_3 = self.empyrical.sortino_ratio(returns, required_return)
        assert sr_1 <= sr_2
        assert sr_2 <= sr_3

    # Translating the returns and required returns by the same amount
    # should not change the sortino ratio.
    @pytest.mark.parametrize(
        "returns, required_return, translation",
        [("noise_uniform", 0, 0.005), ("noise_uniform", 0.005, 0.005)],
        indirect=["returns"],
    )
    def test_sortino_translation_same(self, returns, required_return, translation):
        sr = self.empyrical.sortino_ratio(returns, required_return)
        sr_depressed = self.empyrical.sortino_ratio(
            returns - translation, required_return - translation
        )
        sr_raised = self.empyrical.sortino_ratio(
            returns + translation, required_return + translation
        )
        np.testing.assert_almost_equal(sr, sr_depressed, DECIMAL_PLACES)
        np.testing.assert_almost_equal(sr, sr_raised, DECIMAL_PLACES)

    # Translating the returns and required returns by the same amount
    # should not change the sortino ratio.
    @pytest.mark.parametrize(
        "returns, required_return, translation_returns, translation_required",
        [("noise_uniform", 0, 0, 0.001), ("noise_uniform", 0.005, 0.001, 0)],
        indirect=["returns"],
    )
    def test_sortino_translation_diff(
        self,
        returns,
        required_return,
        translation_returns,
        translation_required,
    ):
        sr = self.empyrical.sortino_ratio(returns, required_return)
        sr_depressed = self.empyrical.sortino_ratio(
            returns - translation_returns,
            required_return - translation_required,
        )
        sr_raised = self.empyrical.sortino_ratio(
            returns + translation_returns,
            required_return + translation_required,
        )
        assert sr != sr_depressed
        assert sr != sr_raised

    # Regressive tests for information ratio
    @pytest.mark.parametrize(
        "returns, factor_returns, expected",
        [
            ("empty_returns", "0.0", np.nan),
            ("one_return", "0.0", np.nan),
            ("pos_line", "pos_line", np.nan),
            ("mixed_returns", "0.0", 0.10859306069076737),
            ("mixed_returns", "flat_line_1", -0.06515583641446039),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_excess_sharpe(self, returns, factor_returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.excess_sharpe(returns, factor_returns),
            expected,
            DECIMAL_PLACES,
        )

    # The magnitude of the information ratio increases as a higher
    # proportion of returns are uncorrelated with the benchmark.
    @pytest.mark.parametrize(
        "returns, benchmark",
        [
            ("flat_line_0", "pos_line"),
            ("flat_line_1_tz", "pos_line"),
            ("noise", "pos_line"),
        ],
        indirect=True,
    )
    def test_excess_sharpe_noisy(self, returns, benchmark):
        noisy_returns_1 = returns[0:250].add(benchmark[250:], fill_value=0)
        noisy_returns_2 = returns[0:500].add(benchmark[500:], fill_value=0)
        noisy_returns_3 = returns[0:750].add(benchmark[750:], fill_value=0)
        ir_1 = self.empyrical.excess_sharpe(noisy_returns_1, benchmark)
        ir_2 = self.empyrical.excess_sharpe(noisy_returns_2, benchmark)
        ir_3 = self.empyrical.excess_sharpe(noisy_returns_3, benchmark)
        assert abs(ir_1) < abs(ir_2)
        assert abs(ir_2) < abs(ir_3)

    # Vertical translations change the information ratio in the
    # direction of the translation.
    @pytest.mark.parametrize(
        "returns, add_noise, benchmark",
        [
            ("pos_line", "noise", "flat_line_1_tz"),
            ("pos_line", "inv_noise", "flat_line_1_tz"),
            ("neg_line", "noise", "flat_line_1_tz"),
            ("neg_line", "inv_noise", "flat_line_1_tz"),
        ],
        indirect=True,
    )
    def test_excess_sharpe_trans(self, returns, add_noise, benchmark):
        ir = self.empyrical.excess_sharpe(returns + add_noise, returns)
        raised_ir = self.empyrical.excess_sharpe(
            returns + add_noise + benchmark, returns
        )
        depressed_ir = self.empyrical.excess_sharpe(
            returns + add_noise - benchmark, returns
        )
        assert ir < raised_ir
        assert depressed_ir < ir

    @pytest.mark.parametrize(
        "returns, benchmark, expected",
        [
            ("empty_returns", "simple_benchmark", (np.nan, np.nan)),
            ("one_return", "one_return", (np.nan, np.nan)),
            (
                "mixed_returns",
                "negative_returns[1:]",
                (-0.9997853834885004, -0.71296296296296313),
            ),
            ("mixed_returns", "mixed_returns", (0.0, 1.0)),
            ("mixed_returns", "-mixed_returns", (0.0, -1.0)),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_alpha_beta(self, returns, benchmark, expected):
        alpha, beta = alpha_beta(returns, benchmark)

        np.testing.assert_almost_equal(alpha, expected[0], DECIMAL_PLACES)
        np.testing.assert_almost_equal(beta, expected[1], DECIMAL_PLACES)

    # Regression tests for alpha
    @pytest.mark.parametrize(
        "returns, benchmark, expected",
        [
            ("empty_returns", "simple_benchmark", np.nan),
            ("one_return", "one_return", np.nan),
            # ("mixed_returns", "flat_line_1", np.nan),
            ("mixed_returns", "mixed_returns", 0.0),
            ("mixed_returns", "-mixed_returns", 0.0),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_alpha(self, returns, benchmark, expected):
        observed = self.empyrical.alpha(returns, benchmark)
        np.testing.assert_almost_equal(observed, expected, DECIMAL_PLACES)

        if len(returns) == len(benchmark):
            # Compare to scipy linregress
            returns_arr = returns.values
            benchmark_arr = benchmark.values
            mask = ~np.isnan(returns_arr) & ~np.isnan(benchmark_arr)

            masked_benchmark_data = benchmark_arr[mask]
            masked_returns_data = returns_arr[mask]

            if len(masked_benchmark_data) < 2:
                with pytest.warns(
                    RuntimeWarning,
                    match="invalid value encountered in (?:scalar divide|sqrt)",
                ):
                    slope, intercept, _, _, _ = stats.linregress(
                        masked_benchmark_data, masked_returns_data
                    )
                    np.testing.assert_almost_equal(
                        observed, intercept * 252, DECIMAL_PLACES
                    )
            else:
                slope, intercept, _, _, _ = stats.linregress(
                    masked_benchmark_data, masked_returns_data
                )
                np.testing.assert_almost_equal(
                    observed, intercept * 252, DECIMAL_PLACES
                )

    # Alpha/beta translation tests.
    @pytest.mark.parametrize(
        "mean_returns, translation",
        [
            (0, 0.001),
            (0.01, 0.001),
        ],
    )
    def test_alpha_beta_translation(self, mean_returns, translation):
        # Generate correlated returns and benchmark.
        std_returns = 0.01
        correlation = 0.8
        std_bench = 0.001
        means = [mean_returns, 0.001]
        covs = [
            [std_returns**2, std_returns * std_bench * correlation],
            [std_returns * std_bench * correlation, std_bench**2],
        ]
        (ret, bench) = rand.multivariate_normal(means, covs, 1000).T
        returns = pd.Series(
            ret, index=pd.date_range("2000-1-30", periods=1000, freq="D")
        )
        benchmark = pd.Series(
            bench, index=pd.date_range("2000-1-30", periods=1000, freq="D")
        )

        # Translate returns and generate alphas and betas.
        returns_depressed = returns - translation
        returns_raised = returns + translation
        alpha_beta = self.empyrical(return_types=np.ndarray).alpha_beta
        (alpha_depressed, beta_depressed) = alpha_beta(returns_depressed, benchmark)
        (alpha_standard, beta_standard) = alpha_beta(returns, benchmark)
        (alpha_raised, beta_raised) = alpha_beta(returns_raised, benchmark)
        # Alpha should change proportionally to how much returns were
        # translated.
        np.testing.assert_almost_equal(
            ((alpha_standard + 1) ** (1 / 252)) - ((alpha_depressed + 1) ** (1 / 252)),
            translation,
            DECIMAL_PLACES,
        )
        np.testing.assert_almost_equal(
            ((alpha_raised + 1) ** (1 / 252)) - ((alpha_standard + 1) ** (1 / 252)),
            translation,
            DECIMAL_PLACES,
        )
        # Beta remains constant.
        np.testing.assert_almost_equal(beta_standard, beta_depressed, DECIMAL_PLACES)
        np.testing.assert_almost_equal(beta_standard, beta_raised, DECIMAL_PLACES)

    # Test alpha/beta with a smaller and larger correlation values.
    @pytest.mark.parametrize("corr_less, corr_more", [(0.1, 0.9)])
    def test_alpha_beta_correlation(self, corr_less, corr_more):
        mean_returns = 0.01
        mean_bench = 0.001
        std_returns = 0.01
        std_bench = 0.001
        index = pd.date_range("2000-1-30", periods=1000, freq="D")
        # Generate less correlated returns
        means_less = [mean_returns, mean_bench]
        covs_less = [
            [std_returns**2, std_returns * std_bench * corr_less],
            [std_returns * std_bench * corr_less, std_bench**2],
        ]
        (ret_less, bench_less) = rand.multivariate_normal(means_less, covs_less, 1000).T
        returns_less = pd.Series(ret_less, index=index)
        benchmark_less = pd.Series(bench_less, index=index)
        # Genereate more highly correlated returns
        means_more = [mean_returns, mean_bench]
        covs_more = [
            [std_returns**2, std_returns * std_bench * corr_more],
            [std_returns * std_bench * corr_more, std_bench**2],
        ]
        (ret_more, bench_more) = rand.multivariate_normal(means_more, covs_more, 1000).T
        returns_more = pd.Series(ret_more, index=index)
        benchmark_more = pd.Series(bench_more, index=index)
        # Calculate alpha/beta values
        alpha_beta = self.empyrical(return_types=np.ndarray).alpha_beta
        alpha_less, beta_less = alpha_beta(returns_less, benchmark_less)
        alpha_more, beta_more = alpha_beta(returns_more, benchmark_more)
        # Alpha determines by how much returns vary from the benchmark return.
        # A lower correlation leads to higher alpha.
        assert alpha_less > alpha_more
        # Beta measures the volatility of returns against benchmark returns.
        # Beta increases proportionally to correlation.
        assert beta_less < beta_more

    # When faced with data containing np.nan, do not return np.nan. Calculate
    # alpha and beta using dates containing both.
    @pytest.mark.parametrize(
        "returns, benchmark",
        [
            ("sparse_noise", "sparse_noise"),
        ],
        indirect=True,
    )
    def test_alpha_beta_with_nan_inputs(self, returns, benchmark):
        alpha, beta = self.empyrical(return_types=np.ndarray).alpha_beta(
            returns,
            benchmark,
        )
        assert not np.isnan(alpha)
        assert not np.isnan(beta)

    @pytest.mark.parametrize(
        "returns, benchmark, expected, decimal_places",
        [
            ("empty_returns", "simple_benchmark", np.nan, DECIMAL_PLACES),
            ("one_return", "one_return", np.nan, DECIMAL_PLACES),
            # ("mixed_returns", "flat_line_1", np.nan, DECIMAL_PLACES),
            ("noise", "noise", 1.0, DECIMAL_PLACES),
            ("2 * noise", "noise", 2.0, DECIMAL_PLACES),
            ("noise", "inv_noise", -1.0, DECIMAL_PLACES),
            ("2 * noise", "inv_noise", -2.0, DECIMAL_PLACES),
            # (
            #     "sparse_noise * flat_line_1_tz",
            #     "sparse_flat_line_1_tz",
            #     np.nan,
            #     DECIMAL_PLACES,
            # ),
            (
                "simple_benchmark_w_noise",
                "simple_benchmark_df",
                1.0,
                2,
            ),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_beta(
        self,
        returns,
        benchmark,
        expected,
        decimal_places,
    ):
        observed = self.empyrical.beta(returns, benchmark)
        np.testing.assert_almost_equal(
            observed,
            expected,
            decimal_places,
        )

        if len(returns) == len(benchmark):
            # Compare to scipy linregress
            effective_benchmark = benchmark
            if isinstance(benchmark, pd.DataFrame):
                effective_benchmark = benchmark["returns"]

            returns_arr = returns.values
            # Ensure benchmark_arr is derived from the potentially modified effective_benchmark
            benchmark_arr = effective_benchmark.values
            mask = ~np.isnan(returns_arr) & ~np.isnan(benchmark_arr)

            masked_benchmark_data = benchmark_arr[mask]
            masked_returns_data = returns_arr[mask]

            if len(masked_benchmark_data) < 2:
                with pytest.warns(
                    RuntimeWarning,
                    match="invalid value encountered in (?:scalar divide|sqrt)",
                ):
                    slope, intercept, _, _, _ = stats.linregress(
                        masked_benchmark_data, masked_returns_data
                    )
                    np.testing.assert_almost_equal(
                        observed, slope, decimal_places
                    )  # Use decimal_places from params
            else:
                slope, intercept, _, _, _ = stats.linregress(
                    masked_benchmark_data, masked_returns_data
                )
                np.testing.assert_almost_equal(
                    observed, slope, decimal_places
                )  # Use decimal_places from params

    @pytest.mark.parametrize(
        "returns, benchmark",
        [
            ("empty_returns", "simple_benchmark"),
            ("one_return", "one_return"),
            # TODO: these are failing, disabling for now
            # (mixed_returns, simple_benchmark[1:]),
            # (mixed_returns, negative_returns[1:]),
            ("mixed_returns", "mixed_returns"),
            ("mixed_returns", "-mixed_returns"),
        ],
        indirect=True,
    )
    def test_alpha_beta_equality(self, returns, benchmark):
        alpha, beta = alpha_beta(returns, benchmark)
        np.testing.assert_almost_equal(
            alpha, self.empyrical.alpha(returns, benchmark), DECIMAL_PLACES
        )
        np.testing.assert_almost_equal(
            beta, self.empyrical.beta(returns, benchmark), DECIMAL_PLACES
        )

        if len(returns) == len(benchmark):
            # Compare to scipy linregress
            returns_arr = returns.values
            benchmark_arr = benchmark.values
            mask = ~np.isnan(returns_arr) & ~np.isnan(benchmark_arr)

            # For this specific linregress call in the test: x = returns, y = benchmark
            masked_returns_data_for_x = returns_arr[mask]
            masked_benchmark_data_for_y = benchmark_arr[mask]

            if len(masked_returns_data_for_x) < 2:
                with pytest.warns(
                    RuntimeWarning,
                    match="invalid value encountered in (?:scalar divide|sqrt)",
                ):
                    slope, intercept, _, _, _ = stats.linregress(
                        masked_returns_data_for_x, masked_benchmark_data_for_y
                    )
                    np.testing.assert_almost_equal(alpha, intercept, DECIMAL_PLACES)
                    np.testing.assert_almost_equal(beta, slope, DECIMAL_PLACES)
            else:
                slope, intercept, _, _, _ = stats.linregress(
                    masked_returns_data_for_x, masked_benchmark_data_for_y
                )
                np.testing.assert_almost_equal(alpha, intercept, DECIMAL_PLACES)
                np.testing.assert_almost_equal(beta, slope, DECIMAL_PLACES)

    @pytest.mark.parametrize(
        "returns, expected",
        [
            ("empty_returns", np.nan),
            ("one_return", np.nan),
            ("mixed_returns", 0.1529973665111273),
            ("flat_line_1_tz", 1.0),
        ],
        indirect=["returns"],
    )
    def test_stability_of_timeseries(self, returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.stability_of_timeseries(returns),
            expected,
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, expected",
        [
            ("empty_returns", np.nan),
            ("one_return", 1.0),
            ("mixed_returns", 0.9473684210526313),
            ("random_100k", 1.0),
        ],
        indirect=["returns"],
    )
    def test_tail_ratio(self, returns, expected):
        np.testing.assert_almost_equal(self.empyrical.tail_ratio(returns), expected, 1)

    # Regression tests for CAGR.
    @pytest.mark.parametrize(
        "returns, period, expected",
        [
            ("empty_returns", empyrical.DAILY, np.nan),
            ("one_return", empyrical.DAILY, 11.274002099240244),
            ("mixed_returns", empyrical.DAILY, 1.9135925373194231),
            ("flat_line_1_tz", empyrical.DAILY, 11.274002099240256),
            ("flat_line_yearly", empyrical.YEARLY, 0.03),
        ],
        indirect=["returns"],
    )
    def test_cagr(self, returns, period, expected):
        np.testing.assert_almost_equal(
            self.empyrical.cagr(returns, period=period),
            expected,
            DECIMAL_PLACES,
        )

    # CAGR is calculated by the starting and ending value of returns,
    # translating returns by a constant will change cagr in the same
    # direction of translation.
    @pytest.mark.parametrize(
        "returns, constant",
        [("noise", 0.01), ("noise_uniform", 0.01)],
        indirect=["returns"],
    )
    def test_cagr_translation(self, returns, constant):
        cagr_depressed = self.empyrical.cagr(returns - constant)
        cagr_unchanged = self.empyrical.cagr(returns)
        cagr_raised = self.empyrical.cagr(returns + constant)
        assert cagr_depressed < cagr_unchanged
        assert cagr_unchanged < cagr_raised

    # Function does not return np.nan when inputs contain np.nan.
    @pytest.mark.parametrize("returns", ["sparse_noise"], indirect=True)
    def test_cagr_with_nan_inputs(self, returns):
        assert not np.isnan(self.empyrical.cagr(returns))

    # Adding noise to returns should not significantly alter the cagr values.
    # Confirm that adding noise does not change cagr values to one
    # significant digit
    @pytest.mark.parametrize(
        "returns, add_noise",
        [
            ("pos_line", "noise"),
            ("pos_line", "noise_uniform"),
            ("flat_line_1_tz", "noise"),
        ],
        indirect=True,
    )
    def test_cagr_noisy(self, returns, add_noise):
        cagr = self.empyrical.cagr(returns)
        noisy_cagr_1 = self.empyrical.cagr(returns + add_noise)
        noisy_cagr_2 = self.empyrical.cagr(returns - add_noise)
        np.testing.assert_approx_equal(cagr, noisy_cagr_1, 1)
        np.testing.assert_approx_equal(cagr, noisy_cagr_2, 1)

    # regression tests for beta_fragility_heuristic
    @pytest.mark.parametrize(
        "returns, factor_returns, expected",
        [
            ("one_return", "one_return", np.nan),
            ("positive_returns", "simple_benchmark", 0.0),
            ("mixed_returns", "simple_benchmark", 0.09),
            ("negative_returns", "simple_benchmark", -0.029999999999999999),
        ],
        indirect=["returns", "factor_returns"],
    )
    def est_beta_fragility_heuristic(self, returns, factor_returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.beta_fragility_heuristic(returns, factor_returns),
            expected,
            DECIMAL_PLACES,
        )

    # regression tests for gpd_risk_estimates
    @pytest.mark.parametrize(
        "returns, expected",
        [
            ("one_return", "[0, 0, 0, 0, 0]"),
            ("empty_returns", "[0, 0, 0, 0, 0]"),
            ("simple_benchmark", "[0, 0, 0, 0, 0]"),
            ("positive_returns", "[0, 0, 0, 0, 0]"),
            ("negative_returns", "negative_returns_expected_gpd_risk_result"),
            ("mixed_returns", "mixed_returns_expected_gpd_risk_result"),
            ("flat_line_1", "[0, 0, 0, 0]"),
            ("weekly_returns", "mixed_returns_expected_gpd_risk_result"),
            ("monthly_returns", "mixed_returns_expected_gpd_risk_result"),
        ],
        indirect=["returns", "expected"],
    )
    def test_gpd_risk_estimates(self, returns, expected):
        result = self.empyrical.gpd_risk_estimates_aligned(returns)
        for result_item, expected_item in zip(result, expected):
            np.testing.assert_almost_equal(result_item, expected_item, DECIMAL_PLACES)

    @pytest.mark.parametrize(
        "returns, window, expected",
        [
            ("empty_returns", 6, []),
            ("negative_returns", 6, [-0.2282, -0.2745, -0.2899, -0.2747]),
        ],
        indirect=["returns"],
    )
    def test_roll_max_drawdown(self, returns, window, expected):
        test = self.empyrical.roll_max_drawdown(returns, window=window)
        np.testing.assert_almost_equal(np.asarray(test), np.asarray(expected), 4)

        self.assert_indexes_match(test, returns[-len(expected) :])

    @pytest.mark.parametrize(
        "returns, window, expected",
        [
            ("empty_returns", 6, []),
            (
                "negative_returns",
                6,
                [-18.09162052, -26.79897486, -26.69138263, -25.72298838],
            ),
            (
                "mixed_returns",
                6,
                [7.57445259, 8.22784105, 8.22784105, -3.1374751],
            ),
        ],
        indirect=["returns"],
    )
    def test_roll_sharpe_ratio(self, returns, window, expected):
        test = self.empyrical.roll_sharpe_ratio(returns, window=window)
        np.testing.assert_almost_equal(
            np.asarray(test), np.asarray(expected), DECIMAL_PLACES
        )

        self.assert_indexes_match(test, returns[-len(expected) :])

    @pytest.mark.parametrize(
        "returns, factor_returns, expected",
        [
            ("empty_returns", "empty_returns", np.nan),
            ("one_return", "one_return", 1.0),
            ("mixed_returns", "mixed_returns", 1.0),
            ("all_negative_returns", "mixed_returns", -0.52257643222960259),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_capture_ratio(self, returns, factor_returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.capture(returns, factor_returns),
            expected,
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, factor_returns, expected",
        [
            ("empty_returns", "empty_returns", np.nan),
            ("one_return", "one_return", np.nan),
            ("mixed_returns", "mixed_returns", 1.0),
            ("all_negative_returns", "mixed_returns", 0.99956025703798634),
            ("positive_returns", "mixed_returns", -11.27400221),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_down_capture(self, returns, factor_returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.down_capture(returns, factor_returns),
            expected,
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, benchmark, window, expected",
        [
            (
                "empty_returns",
                "simple_benchmark",
                1,
                [(np.nan, np.nan)] * 9,
            ),
            ("one_return", "one_return", 1, [(np.nan, np.nan)]),
            (
                "mixed_returns",
                "negative_returns",
                6,
                [
                    (-0.97854954, -0.7826087),
                    (-0.9828927, -0.76156584),
                    (-0.93166924, -0.61682243),
                    (-0.99967288, -0.41311475),
                ],
            ),
            (
                "mixed_returns",
                "mixed_returns",
                6,
                [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)],
            ),
            (
                "mixed_returns",
                "-mixed_returns",
                6,
                [(0.0, -1.0), (0.0, -1.0), (0.0, -1.0), (0.0, -1.0)],
            ),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_roll_alpha_beta(self, returns, benchmark, window, expected):
        test = self.empyrical(
            return_types=(np.ndarray, pd.DataFrame),
        ).roll_alpha_beta(
            returns,
            benchmark,
            window,
        )
        if isinstance(test, pd.DataFrame):
            self.assert_indexes_match(test, benchmark[-len(expected) :])
            test = test.values

        alpha_test = [t[0] for t in test]
        beta_test = [t[1] for t in test]

        alpha_expected = [t[0] for t in expected]
        beta_expected = [t[1] for t in expected]

        np.testing.assert_almost_equal(
            np.asarray(alpha_test),
            np.asarray(alpha_expected),
            DECIMAL_PLACES,
        )

        np.testing.assert_almost_equal(
            np.asarray(beta_test),
            np.asarray(beta_expected),
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, factor_returns, window, expected",
        [
            ("empty_returns", "empty_returns", 1, []),
            ("one_return", "one_return", 1, np.nan),
            ("mixed_returns", "mixed_returns", 6, [1.0, 1.0, 1.0, 1.0]),
            (
                "positive_returns",
                "mixed_returns",
                6,
                [-0.00011389, -0.00025861, -0.00015211, -0.00689239],
            ),
            (
                "all_negative_returns",
                "mixed_returns",
                6,
                [
                    -6.38880246e-05,
                    -1.65241701e-04,
                    -1.65241719e-04,
                    -6.89541957e-03,
                ],
            ),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_roll_up_down_capture(self, returns, factor_returns, window, expected):
        test = self.empyrical.roll_up_down_capture(
            returns, factor_returns, window=window
        )
        np.testing.assert_almost_equal(
            np.asarray(test), np.asarray(expected), DECIMAL_PLACES
        )

    @pytest.mark.parametrize(
        "returns, factor_returns, window, expected",
        [
            ("empty_returns", "empty_returns", 1, []),
            ("one_return", "one_return", 1, [np.nan]),
            ("mixed_returns", "mixed_returns", 6, [1.0, 1.0, 1.0, 1.0]),
            (
                "positive_returns",
                "mixed_returns",
                6,
                [-11.2743862, -11.2743862, -11.2743862, -11.27400221],
            ),
            (
                "all_negative_returns",
                "mixed_returns",
                6,
                [0.92058591, 0.92058591, 0.92058591, 0.99956026],
            ),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_roll_down_capture(self, returns, factor_returns, window, expected):
        test = self.empyrical.roll_down_capture(returns, factor_returns, window=window)
        np.testing.assert_almost_equal(
            np.asarray(test), np.asarray(expected), DECIMAL_PLACES
        )

        self.assert_indexes_match(test, returns[-len(expected) :])

    @pytest.mark.parametrize(
        "returns, factor_returns, window, expected",
        [
            ("empty_returns", "empty_returns", 1, []),
            ("one_return", "one_return", 1, [1.0]),
            ("mixed_returns", "mixed_returns", 6, [1.0, 1.0, 1.0, 1.0]),
            (
                "positive_returns",
                "mixed_returns",
                6,
                [0.00128406, 0.00291564, 0.00171499, 0.0777048],
            ),
            (
                "all_negative_returns",
                "mixed_returns",
                6,
                [
                    -5.88144154e-05,
                    -1.52119182e-04,
                    -1.52119198e-04,
                    -6.89238735e-03,
                ],
            ),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_roll_up_capture(self, returns, factor_returns, window, expected):
        test = self.empyrical.roll_up_capture(returns, factor_returns, window=window)
        np.testing.assert_almost_equal(
            np.asarray(test), np.asarray(expected), DECIMAL_PLACES
        )

        self.assert_indexes_match(test, returns[-len(expected) :])

    @pytest.mark.parametrize(
        "returns, benchmark, expected",
        [
            ("empty_returns", "simple_benchmark", (np.nan, np.nan)),
            ("one_return", "one_return", (np.nan, np.nan)),
            (
                "mixed_returns[1:]",
                "negative_returns[1:]",
                (-0.9997853834885004, -0.71296296296296313),
            ),
            ("mixed_returns", "mixed_returns", (0.0, 1.0)),
            ("mixed_returns", "-mixed_returns", (0.0, -1.0)),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_down_alpha_beta(self, returns, benchmark, expected):
        down_alpha, down_beta = down_alpha_beta(returns, benchmark)

        np.testing.assert_almost_equal(down_alpha, expected[0], DECIMAL_PLACES)
        np.testing.assert_almost_equal(down_beta, expected[1], DECIMAL_PLACES)

    @pytest.mark.parametrize(
        "returns, benchmark, expected",
        [
            ("empty_returns", "simple_benchmark", (np.nan, np.nan)),
            ("one_return", "one_return", (np.nan, np.nan)),
            (
                "mixed_returns[1:]",
                "positive_returns[1:]",
                (0.432961242076658, 0.4285714285),
            ),
            ("mixed_returns", "mixed_returns", (0.0, 1.0)),
            ("mixed_returns", "-mixed_returns", (0.0, -1.0)),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_up_alpha_beta(self, returns, benchmark, expected):
        up_alpha, up_beta = up_alpha_beta(returns, benchmark)

        np.testing.assert_almost_equal(up_alpha, expected[0], DECIMAL_PLACES)
        np.testing.assert_almost_equal(up_beta, expected[1], DECIMAL_PLACES)

    @pytest.mark.parametrize(
        "returns, factor_returns, expected",
        [
            ("empty_returns", "empty_returns", np.nan),
            ("one_return", "one_return", np.nan),
            ("mixed_returns", "mixed_returns", 1.0),
            ("positive_returns", "mixed_returns", -0.0006756053495),
            ("all_negative_returns", "mixed_returns", -0.0004338236),
        ],
        indirect=["returns", "factor_returns"],
    )
    def test_up_down_capture(self, returns, factor_returns, expected):
        np.testing.assert_almost_equal(
            self.empyrical.up_down_capture(returns, factor_returns),
            expected,
            DECIMAL_PLACES,
        )

    @pytest.mark.parametrize(
        "returns, benchmark, expected",
        [
            ("empty_returns", "empty_returns", np.nan),
            ("one_return", "one_return", 1.0),
            ("mixed_returns", "mixed_returns", 1.0),
            ("positive_returns", "mixed_returns", 0.0076167762),
            ("all_negative_returns", "mixed_returns", -0.0004336328),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_up_capture(self, returns, benchmark, expected):
        np.testing.assert_almost_equal(
            self.empyrical.up_capture(returns, benchmark),
            expected,
            DECIMAL_PLACES,
        )

    def test_value_at_risk(self):
        value_at_risk = self.empyrical.value_at_risk

        returns = [1.0, 2.0]
        np.testing.assert_almost_equal(value_at_risk(returns, cutoff=0.0), 1.0)
        np.testing.assert_almost_equal(value_at_risk(returns, cutoff=0.3), 1.3)
        np.testing.assert_almost_equal(value_at_risk(returns, cutoff=1.0), 2.0)

        returns = [1, 81, 82, 83, 84, 85]
        np.testing.assert_almost_equal(value_at_risk(returns, cutoff=0.1), 41)
        np.testing.assert_almost_equal(value_at_risk(returns, cutoff=0.2), 81)
        np.testing.assert_almost_equal(value_at_risk(returns, cutoff=0.3), 81.5)

        # Test a returns stream of 21 data points at different cutoffs.
        returns = rand.normal(0, 0.02, 21)
        for cutoff in (0, 0.0499, 0.05, 0.20, 0.999, 1):
            np.testing.assert_almost_equal(
                value_at_risk(returns, cutoff),
                np.percentile(returns, cutoff * 100),
            )

    def test_conditional_value_at_risk(self):
        value_at_risk = self.empyrical.value_at_risk
        conditional_value_at_risk = self.empyrical.conditional_value_at_risk

        # A single-valued array will always just have a CVaR of its only value.
        returns = rand.normal(0, 0.02, 1)
        expected_cvar = returns[0]
        np.testing.assert_almost_equal(
            conditional_value_at_risk(returns, cutoff=0),
            expected_cvar,
        )
        np.testing.assert_almost_equal(
            conditional_value_at_risk(returns, cutoff=1),
            expected_cvar,
        )

        # Test a returns stream of 21 data points at different cutoffs.
        returns = rand.normal(0, 0.02, 21)

        for cutoff in (0, 0.0499, 0.05, 0.20, 0.999, 1):
            # Find the VaR based on our cutoff, then take the average of all
            # values at or below the VaR.
            var = value_at_risk(returns, cutoff)
            expected_cvar = np.mean(returns[returns <= var])

            np.testing.assert_almost_equal(
                conditional_value_at_risk(returns, cutoff),
                expected_cvar,
            )

    @property
    def empyrical(self):
        """
        This returns a wrapper around the empyrical module, so tests can
        perform input conversions or return type checks on each call to an
        empyrical function.

        Each test case subclass can override this property, so that all the
        same tests are run, but with different function inputs or type checks.

        This was done as part of enabling empyrical functions to work with
        inputs of either pd.Series or np.ndarray, with the expectation that
        they will return the same type as their input.

        Returns
        -------
        empyrical

        Notes
        -----
        Since some parameterized test parameters refer to attributes on the
        real empyrical module at class body scope, this property must be
        defined later in the body than those references. That way, the
        attributes are looked up on the empyrical module, not this property.

        e.g. empyrical.DAILY
        """
        return ReturnTypeEmpyricalProxy(self, (pd.Series, float))


class TestStatsArrays(TestStats):
    """
    Tests pass np.ndarray inputs to empyrical and assert that outputs are of
    type np.ndarray or float.

    """

    @property
    def empyrical(self):
        return PassArraysEmpyricalProxy(self, (np.ndarray, float))

    def assert_indexes_match(self, result, expected):
        pass


class TestStatsIntIndex(TestStats):
    """
    Tests pass int-indexed pd.Series inputs to empyrical and assert that
    outputs are of type pd.Series or float.

    This prevents a regression where we're indexing with ints into a pd.Series
    to find the last item and get a KeyError when the series is int-indexed.

    """

    @property
    def empyrical(self):
        return ConvertPandasEmpyricalProxy(
            self,
            (pd.Series, float),
            lambda obj: type(obj)(obj.values, index=np.arange(len(obj))),
        )

    def assert_indexes_match(self, result, expected):
        pass


@pytest.mark.usefixtures("set_helpers")
class TestHelpers(BaseTestClass):
    """
    Tests for helper methods and utils.
    """

    def test_roll_pandas(self):
        res = emutils.roll(
            self.returns,
            self.factor_returns,
            window=12,
            function=empyrical.alpha_aligned,
        )

        assert res.size == self.ser_length - self.window + 1

    def test_roll_ndarray(self):
        res = emutils.roll(
            self.returns.values,
            self.factor_returns.values,
            window=12,
            function=empyrical.alpha_aligned,
        )

        assert len(res), self.ser_length - self.window + 1

    def test_down(self):
        pd_res = emutils.down(
            self.returns, self.factor_returns, function=empyrical.capture
        )
        np_res = emutils.down(
            self.returns.values,
            self.factor_returns.values,
            function=empyrical.capture,
        )

        assert isinstance(pd_res, float)
        np.testing.assert_almost_equal(pd_res, np_res, DECIMAL_PLACES)

    def test_up(self):
        pd_res = emutils.up(
            self.returns, self.factor_returns, function=empyrical.capture
        )
        np_res = emutils.up(
            self.returns.values,
            self.factor_returns.values,
            function=empyrical.capture,
        )

        assert isinstance(pd_res, float)
        np.testing.assert_almost_equal(pd_res, np_res, DECIMAL_PLACES)

    def test_roll_bad_types(self):
        with pytest.raises(ValueError):
            emutils.roll(
                self.returns.values,
                self.factor_returns,
                window=12,
                function=empyrical.max_drawdown,
            )

    def test_roll_max_window(self):
        res = emutils.roll(
            self.returns,
            self.factor_returns,
            window=self.ser_length + 100,
            function=empyrical.max_drawdown,
        )
        assert res.size == 0


class Test2DStats:
    """
    Tests for functions that are capable of outputting a DataFrame.
    """

    def assert_indexes_match(self, result, expected):
        """
        Assert that two pandas objects have the same indices.

        This is a method instead of a free function so that we can override it
        to be a no-op in suites like TestStatsArrays that unwrap pandas objects
        into ndarrays.
        """
        pd.testing.assert_index_equal(result.index, expected.index)

        if isinstance(result, pd.DataFrame) and isinstance(expected, pd.DataFrame):
            pd.testing.assert_index_equal(result.columns, expected.columns)

    @pytest.mark.parametrize(
        "returns, starting_value, expected",
        [
            ("df_input", 0, "df_0_expected"),
            ("df_input", 100, "df_100_expected"),
            ("df_empty", 0, "df_empty"),
        ],
        indirect=["returns", "expected"],
    )
    def test_cum_returns_df(self, returns, starting_value, expected):
        cum_returns = self.empyrical.cum_returns(
            returns,
            starting_value=starting_value,
        )

        np.testing.assert_almost_equal(
            np.asarray(cum_returns),
            np.asarray(expected),
            4,
        )

        self.assert_indexes_match(cum_returns, returns)

    @pytest.mark.parametrize(
        "returns, starting_value, expected",
        [
            ("df_input", 0, "df_0_expected"),
            ("df_input", 100, "df_100_expected"),
        ],
        indirect=["returns", "expected"],
    )
    def test_cum_returns_final_df(self, returns, starting_value, expected):
        return_types = (pd.Series, np.ndarray)
        result = self.empyrical(return_types=return_types).cum_returns_final(
            returns,
            starting_value=starting_value,
        )
        np.testing.assert_almost_equal(np.array(result), expected.iloc[-1], 5)
        self.assert_indexes_match(result, expected.iloc[-1])

    @pytest.mark.parametrize(
        "returns, benchmark, expected",
        [
            ("empty_returns", "empty_returns", [np.nan, np.nan, np.nan]),
            ("positive_returns", "all_negative_returns", [1, np.nan, 1]),
            ("all_negative_returns", "positive_returns", [0, 0, np.nan]),
            ("mixed_returns", "mixed_returns", [0, 0, 0]),
            (
                "simple_benchmark",
                "simple_benchmark_w_noise",
                [0.666667, 0.5, 1.0],
            ),
        ],
        indirect=["returns", "benchmark"],
    )
    def test_batting_average(self, returns, benchmark, expected):
        return_types = (pd.Series, np.ndarray)
        batting_average = self.empyrical(return_types=return_types).batting_average(
            returns, benchmark
        )
        np.testing.assert_almost_equal(batting_average, expected, 4)

    @property
    def empyrical(self):
        """
        Returns a wrapper around the empyrical module so tests can
        perform input conversions or return type checks on each call to an
        empyrical function. See full explanation in TestStats.

        Returns
        -------
        empyrical

        """

        return ReturnTypeEmpyricalProxy(self, pd.DataFrame)


class Test2DStatsArrays(Test2DStats):
    """
    Tests pass np.ndarray inputs to empyrical and assert that outputs are of
    type np.ndarray.

    """

    @property
    def empyrical(self):
        return PassArraysEmpyricalProxy(self, np.ndarray)

    def assert_indexes_match(self, result, expected):
        pass


class ReturnTypeEmpyricalProxy(object):
    """
    A wrapper around the empyrical module which, on each function call, asserts
    that the type of the return value is in a given set.

    Also asserts that inputs were not modified by the empyrical function call.

    Calling an instance with kwargs will return a new copy with those
    attributes overridden.

    """

    def __init__(self, test_case, return_types):
        self._test_case = test_case
        self._return_types = return_types

    def __call__(self, **kwargs):
        dupe = copy(self)

        for k, v in kwargs.items():
            attr = "_" + k
            if hasattr(dupe, attr):
                setattr(dupe, attr, v)

        return dupe

    def __copy__(self):
        newone = type(self).__new__(type(self))
        newone.__dict__.update(self.__dict__)
        return newone

    def __getattr__(self, item):
        return self._check_input_not_mutated(
            self._check_return_type(getattr(empyrical, item))
        )

    def _check_return_type(self, func):
        @wraps(func)
        def check_return_type(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, tuple):
                tuple_result = result
            else:
                tuple_result = (result,)

            for r in tuple_result:
                assert isinstance(r, self._return_types)
            return result

        return check_return_type

    def _check_input_not_mutated(self, func):
        @wraps(func)
        def check_not_mutated(*args, **kwargs):
            # Copy inputs to compare them to originals later.
            arg_copies = [
                (i, arg.copy())
                for i, arg in enumerate(args)
                if isinstance(arg, (NDFrame, np.ndarray))
            ]
            kwarg_copies = {
                k: v.copy()
                for k, v in kwargs.items()
                if isinstance(v, (NDFrame, np.ndarray))
            }

            result = func(*args, **kwargs)

            # Check that inputs weren't mutated by func.
            for i, arg_copy in arg_copies:
                np.testing.assert_allclose(
                    args[i],
                    arg_copy,
                    atol=0.5 * 10 ** (-DECIMAL_PLACES),
                    err_msg="Input 'arg %s' mutated by %s" % (i, func.__name__),
                )
            for kwarg_name, kwarg_copy in kwarg_copies.items():
                np.testing.assert_allclose(
                    kwargs[kwarg_name],
                    kwarg_copy,
                    atol=0.5 * 10 ** (-DECIMAL_PLACES),
                    err_msg="Input '%s' mutated by %s" % (kwarg_name, func.__name__),
                )

            return result

        return check_not_mutated


class ConvertPandasEmpyricalProxy(ReturnTypeEmpyricalProxy):
    """
    A ReturnTypeEmpyricalProxy which also converts pandas NDFrame inputs to
    empyrical functions according to the given conversion method.

    Calling an instance with a truthy pandas_only will return a new instance
    which will skip the test when an empyrical function is called.

    """

    def __init__(self, test_case, return_types, convert, pandas_only=False):
        super(ConvertPandasEmpyricalProxy, self).__init__(test_case, return_types)
        self._convert = convert
        self._pandas_only = pandas_only

    def __getattr__(self, item):
        if self._pandas_only:
            pytest.skip(
                "empyrical.%s expects pandas-only inputs that have "
                "dt indices/labels" % item
            )

        func = super(ConvertPandasEmpyricalProxy, self).__getattr__(item)

        @wraps(func)
        def convert_args(*args, **kwargs):
            args = [
                self._convert(arg) if isinstance(arg, NDFrame) else arg for arg in args
            ]
            kwargs = {
                k: self._convert(v) if isinstance(v, NDFrame) else v
                for k, v in kwargs.items()
            }
            return func(*args, **kwargs)

        return convert_args


class PassArraysEmpyricalProxy(ConvertPandasEmpyricalProxy):
    """
    A ConvertPandasEmpyricalProxy which converts NDFrame inputs to empyrical
    functions to numpy arrays.

    Calls the underlying
    empyrical.[alpha|beta|alpha_beta]_aligned functions directly, instead of
    the wrappers which align Series first.

    """

    def __init__(self, test_case, return_types):
        super(PassArraysEmpyricalProxy, self).__init__(
            test_case,
            return_types,
            attrgetter("values"),
        )

    def __getattr__(self, item):
        if item in (
            "alpha",
            "beta",
            "alpha_beta",
            "beta_fragility_heuristic",
            "gpd_risk_estimates",
        ):
            item += "_aligned"

        return super(PassArraysEmpyricalProxy, self).__getattr__(item)
