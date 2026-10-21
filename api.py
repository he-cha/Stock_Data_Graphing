"""Alpha Vantage client. Configure ALPHAVANTAGE_API_KEY outside source control."""
import os
import requests


def _series(function, symbol, interval=None):
    key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if not key:
        raise ValueError('Set ALPHAVANTAGE_API_KEY before requesting stock data.')
    params = {'function': function, 'symbol': symbol, 'apikey': key}
    if interval is not None:
        params['interval'] = f'{interval}min'
    response = requests.get('https://www.alphavantage.co/query', params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError('The data provider returned an invalid response.')
    if any(k in data for k in ('Error Message', 'Note', 'Information')):
        raise ValueError('The provider could not supply this series. Check symbol, API access and rate limits.')
    return data


def TIME_SERIES_INTRADAY(symbol, interval):
    return _series('TIME_SERIES_INTRADAY', symbol, interval)


def TIME_SERIES_DAILY(symbol):
    return _series('TIME_SERIES_DAILY', symbol)


def TIME_SERIES_WEEKLY(symbol):
    return _series('TIME_SERIES_WEEKLY', symbol)


def TIME_SERIES_MONTHLY(symbol):
    return _series('TIME_SERIES_MONTHLY', symbol)
