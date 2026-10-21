import unittest
from unittest.mock import patch, Mock
import requests
import app
import api

PRICES = {'2. high': '12', '1. open': '10', '3. low': '9', '4. close': '11'}
class StockTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.symbols = patch('app.read_symbols', return_value=['IBM'])
        self.symbols.start()
        self.addCleanup(self.symbols.stop)
    def form(self, **kwargs):
        return dict(symbol='IBM', chart_type='line', time='daily', start='2024-01-01', end='2024-01-31', **kwargs)
    def test_daily_chart_renders(self):
        with patch('app.TIME_SERIES_DAILY', return_value={'Time Series (Daily)': {'2024-01-02': PRICES}}):
            response = self.client.post('/', data=self.form())
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<svg', response.data)
    def test_intraday_without_dates(self):
        with patch('app.TIME_SERIES_INTRADAY', return_value={'Time Series (5min)': {'2024-01-02 09:30:00': PRICES}}) as provider:
            response = self.client.post('/', data={'symbol':'IBM','chart_type':'bar','time':'intra','interval':'5'})
        provider.assert_called_once_with('IBM','5')
        self.assertIn(b'<svg', response.data)
    def test_invalid_dates_never_call_provider(self):
        with patch('app.TIME_SERIES_DAILY') as provider:
            response = self.client.post('/', data={**self.form(),'start':'2024-02-01'})
        provider.assert_not_called()
        self.assertIn(b'Start date must', response.data)
    def test_empty_and_unavailable_provider_show_message(self):
        with patch('app.TIME_SERIES_DAILY', return_value={}):
            self.assertIn(b'No prices', self.client.post('/', data=self.form()).data)
        with patch('app.TIME_SERIES_DAILY', side_effect=requests.Timeout):
            self.assertIn(b'unavailable', self.client.post('/', data=self.form()).data)
    def test_api_timeout_and_rate_limit_handling(self):
        response = Mock();response.json.return_value={'Information':'Rate limit'}
        with patch.dict('os.environ', {'ALPHAVANTAGE_API_KEY':'test-only'}), patch('api.requests.get', return_value=response) as get:
            with self.assertRaises(ValueError):api.TIME_SERIES_DAILY('IBM')
            self.assertEqual(get.call_args.kwargs['timeout'],20)

if __name__=='__main__': unittest.main()
