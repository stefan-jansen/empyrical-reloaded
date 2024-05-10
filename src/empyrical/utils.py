#
# Copyright 2018 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import errno
import warnings
from datetime import datetime
from functools import wraps, partial
from os import makedirs, environ
from os.path import expanduser, join, getmtime, isdir

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import as_strided
from pandas.tseries.offsets import BDay
from pytz import UTC

try:  # incompatible with Python 3.12
    from pandas_datareader import data as web
except ImportError:
    web = None

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    # fast versions
    import bottleneck as bn

    def _wrap_function(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            out = kwargs.pop("out", None)
            data = f(*args, **kwargs)
            if out is None:
                out = data
            else:
                out[()] = data

            return out

        return wrapped

    nanmean = _wrap_function(bn.nanmean)
    nanstd = _wrap_function(bn.nanstd)
    nansum = _wrap_function(bn.nansum)
    nanmax = _wrap_function(bn.nanmax)
    nanmin = _wrap_function(bn.nanmin)
    nanargmax = _wrap_function(bn.nanargmax)
    nanargmin = _wrap_function(bn.nanargmin)
except ImportError:
    # slower numpy
    nanmean = np.nanmean
    nanstd = np.nanstd
    nansum = np.nansum
    nanmax = np.nanmax
    nanmin = np.nanmin
    nanargmax = np.nanargmax
    nanargmin = np.nanargmin


def roll(*args, **kwargs):
    """
    Calculates a given statistic across a rolling time period.

    Parameters
    ----------
    returns : pd.Series or np.ndarray
        Daily returns of the strategy, noncumulative.
        - See full explanation in :func:`~empyrical.stats.cum_returns`.
    factor_returns (optional): float / series
        Benchmark return to compare returns against.
    function:
        the function to run for each rolling window.
    window (keyword): int
        the number of periods included in each calculation.
    (other keywords): other keywords that are required to be passed to the
        function in the 'function' argument may also be passed in.

    Returns
    -------
    np.ndarray, pd.Series
        depends on input type
        ndarray(s) ==> ndarray
        Series(s) ==> pd.Series

        A Series or ndarray of the results of the stat across the rolling
        window.

    """
    func = kwargs.pop("function")
    window = kwargs.pop("window")
    if len(args) > 2:
        raise ValueError("Cannot pass more than 2 return sets")

    if len(args) == 2:
        if not isinstance(args[0], type(args[1])):
            raise ValueError("The two returns arguments are not the same.")

    if isinstance(args[0], np.ndarray):
        return _roll_ndarray(func, window, *args, **kwargs)
    return _roll_pandas(func, window, *args, **kwargs)


def up(returns, factor_returns, **kwargs):
    """
    Calculates a given statistic filtering only positive factor return periods.

    Parameters
    ----------
    returns : pd.Series or np.ndarray
        Daily returns of the strategy, noncumulative.
        - See full explanation in :func:`~empyrical.stats.cum_returns`.
    factor_returns (optional): float / series
        Benchmark return to compare returns against.
    function:
        the function to run for each rolling window.
    (other keywords): other keywords that are required to be passed to the
        function in the 'function' argument may also be passed in.

    Returns
    -------
    Same as the return of the function
    """
    func = kwargs.pop("function")
    returns = returns[factor_returns > 0]
    factor_returns = factor_returns[factor_returns > 0]
    return func(returns, factor_returns, **kwargs)


def down(returns, factor_returns, **kwargs):
    """
    Calculates a given statistic filtering only negative factor return periods.

    Parameters
    ----------
    returns : pd.Series or np.ndarray
        Daily returns of the strategy, noncumulative.
        - See full explanation in :func:`~empyrical.stats.cum_returns`.
    factor_returns (optional): float / series
        Benchmark return to compare returns against.
    function:
        the function to run for each rolling window.
    (other keywords): other keywords that are required to be passed to the
        function in the 'function' argument may also be passed in.

    Returns
    -------
    Same as the return of the 'function'
    """
    func = kwargs.pop("function")
    returns = returns[factor_returns < 0]
    factor_returns = factor_returns[factor_returns < 0]
    return func(returns, factor_returns, **kwargs)


def _roll_ndarray(func, window, *args, **kwargs):
    data = []
    for i in range(window, len(args[0]) + 1):
        rets = [s[i - window : i] for s in args]
        data.append(func(*rets, **kwargs))
    return np.array(data)


def _roll_pandas(func, window, *args, **kwargs):
    data = {}
    index_values = []
    for i in range(window, len(args[0]) + 1):
        rets = [s.iloc[i - window : i] for s in args]
        index_value = args[0].index[i - 1]
        index_values.append(index_value)
        data[index_value] = func(*rets, **kwargs)
    return pd.Series(
        data,
        index=type(args[0].index)(index_values),
        dtype=np.float64,
    )


def cache_dir(environ=environ):
    try:
        return environ["EMPYRICAL_CACHE_DIR"]
    except KeyError:
        return join(
            environ.get(
                "XDG_CACHE_HOME",
                expanduser("~/.cache/"),
            ),
            "empyrical",
        )


def data_path(name):
    return join(cache_dir(), name)


def ensure_directory(path):
    """
    Ensure that a directory named "path" exists.
    """

    try:
        makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not isdir(path):
            raise


def get_utc_timestamp(dt):
    """
    Returns the Timestamp/DatetimeIndex
    with either localized or converted to UTC.

    Parameters
    ----------
    dt : Timestamp/DatetimeIndex
        the date(s) to be converted

    Returns
    -------
    same type as input
        date(s) converted to UTC
    """

    dt = pd.to_datetime(dt)
    try:
        dt = dt.tz_localize("UTC")
    except TypeError:
        dt = dt.tz_convert("UTC")
    return dt


_1_bday = BDay()


def _1_bday_ago():
    return pd.Timestamp.now().normalize() - _1_bday


def get_fama_french(
    start="1-1-1970",
    end=None,
    datasets=("F-F_Research_Data_Factors_daily", "F-F_Momentum_Factor_daily"),
):
    """
    Retrieve Fama-French factors via pandas-datareader
    Parameters
    ----------
    start: str or datetime or Timestamp, start date
    end: str or datetime or Timestamp, end date
    datasets: list of factors (default is the five factors)
    Returns
    -------
    pandas.DataFrame
        Percent change of Fama-French factors
    """
    if web is None:
        raise ImportError("pandas-datareader is required to fetch Fama-French data")

    if not isinstance(start, datetime):
        start = pd.Timestamp(start).date()
    if not isinstance(end, datetime):
        end = pd.Timestamp(end).date()

    ff_function = partial(
        web.DataReader,
        data_source="famafrench",
        start=start,
        end=end,
    )

    df = [ff_function(dataset)[0] for dataset in datasets]
    df = pd.concat(df, axis=1).dropna().div(100).rename(columns=str.strip)

    df.index = df.index.tz_localize("utc")
    return df


def get_returns_cached(filepath, update_func, latest_dt, **kwargs):
    """
    Get returns from a cached file if the cache is recent enough,
    otherwise, try to retrieve via a provided update function and
    update the cache file.
    Parameters
    ----------
    filepath : str
        Path to cached csv file
    update_func : function
        Function to call in case cache is not up-to-date.
    latest_dt : pd.Timestamp (tz=UTC)
        Latest datetime required in csv file.
    **kwargs : Keyword arguments
        Optional keyword arguments will be passed to update_func()
    Returns
    -------
    pandas.DataFrame
        DataFrame containing returns
    """

    update_cache = False

    try:
        mtime = getmtime(filepath)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        update_cache = True
    else:

        file_dt = pd.Timestamp(mtime, unit="s")

        if latest_dt.tzinfo:
            file_dt = file_dt.tz_localize("utc")

        if file_dt < latest_dt:
            update_cache = True
        else:
            returns = pd.read_csv(filepath, index_col=0, parse_dates=True)
            if returns.index.tz != UTC:
                returns.index = returns.index.tz_localize("UTC")

    if update_cache:
        returns = update_func(**kwargs)
        try:
            ensure_directory(cache_dir())
        except OSError as e:
            warnings.warn(
                "could not update cache: {}. {}: {}".format(
                    filepath,
                    type(e).__name__,
                    e,
                ),
                UserWarning,
            )

        try:
            returns.to_csv(filepath)
        except OSError as e:
            warnings.warn(
                "could not update cache {}. {}: {}".format(
                    filepath,
                    type(e).__name__,
                    e,
                ),
                UserWarning,
            )

    return returns


def load_portfolio_risk_factors(filepath_prefix=None, start=None, end=None):
    """
    Load risk factors Mkt-Rf, SMB, HML, Rf, and UMD.
    Data is stored in HDF5 file. If the data is more than 2
    days old, redownload from Dartmouth.
    Returns
    -------
    five_factors : pd.DataFrame
        Risk factors timeseries.
    """

    if start is None:
        start = "1/1/1970"
    if end is None:
        end = _1_bday_ago()

    start = get_utc_timestamp(start)
    end = get_utc_timestamp(end)

    if filepath_prefix is None:
        filepath = data_path("factors.csv")
    else:
        filepath = filepath_prefix

    five_factors = get_returns_cached(filepath, get_fama_french, end)

    return five_factors.loc[start:end]


def get_treasury_yield(start=None, end=None, period="3MO"):
    """
    Load treasury yields from FRED.

    Parameters
    ----------
    start : date, optional
        Earliest date to fetch data for.
        Defaults to earliest date available.
    end : date, optional
        Latest date to fetch data for.
        Defaults to latest date available.
    period : {'1MO', '3MO', '6MO', 1', '5', '10'}, optional
        Which maturity to use.
    Returns
    -------
    pd.Series
        Annual treasury yield for every day.
    """

    if start is None:
        start = "1970-01-01"
    if end is None:
        end = _1_bday_ago()

    treasury = web.DataReader(f"DGS{period}", data_source="fred", start=start, end=end)
    return treasury.ffill()


def get_symbol_returns_from_yahoo(symbol, start=None, end=None):
    """
    Wrapper for pandas.io.data.get_data_yahoo().
    Retrieves prices for symbol from yahoo and computes returns
    based on adjusted closing prices.

    Parameters
    ----------
    symbol : str
        Yahoo symbol name to load, e.g. 'SPY'
    start : pandas.Timestamp compatible, optional
        Start date of time period to retrieve
    end : pandas.Timestamp compatible, optional
        End date of time period to retrieve

    Returns
    -------
    pandas.DataFrame
        Returns of symbol in requested period.
    """

    try:

        px = yf.download(symbol, start=start, end=end)
        rets = px[["Adj Close"]].pct_change().dropna()
    except Exception as e:
        warnings.warn(
            "Yahoo Finance read failed: {}".format(e),
            UserWarning,
        )

    rets.index = rets.index.tz_localize("UTC")
    rets.columns = [symbol]
    return rets


def default_returns_func(symbol, start=None, end=None):
    """
    Gets returns for a symbol.
    Queries Yahoo Finance. Attempts to cache SPY.

    Parameters
    ----------
    symbol : str
        Ticker symbol, e.g. APPL.
    start : date, optional
        Earliest date to fetch data for.
        Defaults to earliest date available.
    end : date, optional
        Latest date to fetch data for.
        Defaults to latest date available.

    Returns
    -------
    pd.Series
        Daily returns for the symbol.
         - See full explanation in tears.create_full_tear_sheet (returns).
    """

    if start is None:
        start = "1970-01-01"
    if end is None:
        end = _1_bday_ago()

    start = get_utc_timestamp(start)
    end = get_utc_timestamp(end)

    if symbol == "SPY":
        filepath = data_path("spy.csv")
        rets = get_returns_cached(
            filepath,
            get_symbol_returns_from_yahoo,
            end,
            symbol="SPY",
            start="1/1/1970",
            end=datetime.now(),
        )
        rets = rets[start:end]
    else:
        rets = get_symbol_returns_from_yahoo(symbol, start=start, end=end)

    return rets[symbol]


def rolling_window(array, length, mutable=False):
    """
    Restride an array of shape

        (X_0, ... X_N)

    into an array of shape

        (length, X_0 - length + 1, ... X_N)

    where each slice at index i along the first axis is equivalent to

        result[i] = array[length * i:length * (i + 1)]

    Parameters
    ----------
    array : np.ndarray
        The base array.
    length : int
        Length of the synthetic first axis to generate.
    mutable : bool, optional
        Return a mutable array? The returned array shares the same memory as
        the input array. This means that writes into the returned array affect
        ``array``. The returned array also uses strides to map the same values
        to multiple indices. Writes to a single index may appear to change many
        values in the returned array.

    Returns
    -------
    out : np.ndarray

    Example
    -------
    >>> from numpy import arange
    >>> a = arange(25).reshape(5, 5)
    >>> a
    array([[ 0,  1,  2,  3,  4],
           [ 5,  6,  7,  8,  9],
           [10, 11, 12, 13, 14],
           [15, 16, 17, 18, 19],
           [20, 21, 22, 23, 24]])

    >>> rolling_window(a, 2)
    array([[[ 0,  1,  2,  3,  4],
            [ 5,  6,  7,  8,  9]],
    <BLANKLINE>
           [[ 5,  6,  7,  8,  9],
            [10, 11, 12, 13, 14]],
    <BLANKLINE>
           [[10, 11, 12, 13, 14],
            [15, 16, 17, 18, 19]],
    <BLANKLINE>
           [[15, 16, 17, 18, 19],
            [20, 21, 22, 23, 24]]])
    """
    if not length:
        raise ValueError("Can't have 0-length window")

    orig_shape = array.shape
    if not orig_shape:
        raise IndexError("Can't restride a scalar.")
    elif orig_shape[0] < length:
        raise IndexError(
            "Can't restride array of shape {shape} with"
            " a window length of {len}".format(
                shape=orig_shape,
                len=length,
            )
        )

    num_windows = orig_shape[0] - length + 1
    new_shape = (num_windows, length) + orig_shape[1:]

    new_strides = (array.strides[0],) + array.strides

    out = as_strided(array, new_shape, new_strides)
    out.setflags(write=mutable)
    return out


def _create_unary_vectorized_roll_function(function):
    def unary_vectorized_roll(arr, window, out=None, **kwargs):
        """
        Computes the {human_readable} measure over a rolling window.

        Parameters
        ----------
        arr : array-like
            The array to compute the rolling {human_readable} over.
        window : int
            Size of the rolling window in terms of the periodicity of the data.
        out : array-like, optional
            Array to use as output buffer.
            If not passed, a new array will be created.
        **kwargs
            Forwarded to :func:`~empyrical.{name}`.

        Returns
        -------
        rolling_{name} : array-like
            The rolling {human_readable}.
        """
        allocated_output = out is None

        if len(arr):
            out = function(
                rolling_window(_flatten(arr), min(len(arr), window)).T,
                out=out,
                **kwargs,
            )
        else:
            out = np.empty(0, dtype="float64")

        if allocated_output and isinstance(arr, pd.Series):
            out = pd.Series(out, index=arr.index[-len(out) :])

        return out

    unary_vectorized_roll.__doc__ = unary_vectorized_roll.__doc__.format(
        name=function.__name__,
        human_readable=function.__name__.replace("_", " "),
    )
    unary_vectorized_roll.__name__ = f"rolling_{function.__name__}"

    return unary_vectorized_roll


def _create_binary_vectorized_roll_function(function):
    def binary_vectorized_roll(lhs, rhs, window, out=None, **kwargs):
        """
        Computes the {human_readable} measure over a rolling window.

        Parameters
        ----------
        lhs : array-like
            The first array to pass to the rolling {human_readable}.
        rhs : array-like
            The second array to pass to the rolling {human_readable}.
        window : int
            Size of the rolling window in terms of the periodicity of the data.
        out : array-like, optional
            Array to use as output buffer.
            If not passed, a new array will be created.
        **kwargs
            Forwarded to :func:`~empyrical.{name}`.

        Returns
        -------
        rolling_{name} : array-like
            The rolling {human_readable}.
        """
        allocated_output = out is None

        if window >= 1 and len(lhs) and len(rhs):
            out = function(
                rolling_window(_flatten(lhs), min(len(lhs), window)).T,
                rolling_window(_flatten(rhs), min(len(rhs), window)).T,
                out=out,
                **kwargs,
            )
        elif allocated_output:
            out = np.empty(0, dtype="float64")
        else:
            out[()] = np.nan

        if allocated_output:
            if out.ndim == 1 and isinstance(lhs, pd.Series):
                out = pd.Series(out, index=lhs.index[-len(out) :])
            elif out.ndim == 2 and isinstance(lhs, pd.Series):
                out = pd.DataFrame(out, index=lhs.index[-len(out) :])
        return out

    binary_vectorized_roll.__doc__ = binary_vectorized_roll.__doc__.format(
        name=function.__name__,
        human_readable=function.__name__.replace("_", " "),
    )

    binary_vectorized_roll.__name__ = f"rolling_{function.__name__}"

    return binary_vectorized_roll


def _flatten(arr):
    return arr if not isinstance(arr, pd.Series) else arr.values


def _aligned_series(*many_series):
    """
    Return a new list of series containing the data in the input series, but
    with their indices aligned. NaNs will be filled in for missing values.

    Parameters
    ----------
    *many_series
        The series to align.

    Returns
    -------
    aligned_series : iterable[array-like]
        A new list of series containing the data in the input series, but
        with their indices aligned. NaNs will be filled in for missing values.

    """
    head = many_series[0]
    tail = many_series[1:]
    n = len(head)
    if isinstance(head, np.ndarray) and all(
        len(s) == n and isinstance(s, np.ndarray) for s in tail
    ):
        # optimization: ndarrays of the same length are already aligned
        return many_series

    # dataframe has no ``itervalues``
    return (v for _, v in pd.concat(map(_to_pandas, many_series), axis=1).items())


def _to_pandas(ob):
    """Convert an array-like to a pandas object.

    Parameters
    ----------
    ob : array-like
        The object to convert.

    Returns
    -------
    pandas_structure : pd.Series or pd.DataFrame
        The correct structure based on the dimensionality of the data.
    """
    if isinstance(ob, (pd.Series, pd.DataFrame)):
        return ob

    if ob.ndim == 1:
        return pd.Series(ob)
    elif ob.ndim == 2:
        return pd.DataFrame(ob)
    else:
        raise ValueError(
            "cannot convert array of dim > 2 to a pandas structure",
        )


def _adjust_returns(returns, adjustment_factor):
    """
    Returns the returns series adjusted by adjustment_factor. Optimizes for the
    case of adjustment_factor being 0 by returning returns itself, not a copy!

    Parameters
    ----------
    returns : pd.Series or np.ndarray
    adjustment_factor : pd.Series or np.ndarray or float or int

    Returns
    -------
    adjusted_returns : array-like
    """
    if isinstance(adjustment_factor, (float, int)) and adjustment_factor == 0:
        return returns
    return returns - adjustment_factor
