"""Stock price visualization with validated inputs and provider error handling."""
import csv
import os
import secrets
from datetime import date, datetime
from pathlib import Path
import pygal
import requests
from flask import Flask, render_template, request, flash
from api import TIME_SERIES_DAILY, TIME_SERIES_INTRADAY, TIME_SERIES_MONTHLY, TIME_SERIES_WEEKLY

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
BASE_DIR = Path(__file__).resolve().parent


def read_symbols():
    with (BASE_DIR / 'stocks.csv').open(newline='') as csvfile:
        return sorted({row[0].strip() for row in csv.reader(csvfile) if row and row[0].strip()})


@app.route('/', methods=['GET', 'POST'])
def index():
    symbols = read_symbols()
    chart_svg = None
    if request.method == 'POST':
        try:
            symbol = request.form.get('symbol', '')
            kind = request.form.get('chart_type')
            period = request.form.get('time')
            interval = request.form.get('interval', '5')
            if symbol not in symbols or kind not in ('bar', 'line'):
                raise ValueError('Choose a valid symbol and chart type.')
            if period not in ('intra', 'daily', 'weekly', 'monthly'):
                raise ValueError('Choose a valid time series.')
            if period == 'intra' and interval not in ('1', '5', '15', '30', '60'):
                raise ValueError('Choose a valid intraday interval.')
            start = end = None
            if period != 'intra':
                start = date.fromisoformat(request.form.get('start', ''))
                end = date.fromisoformat(request.form.get('end', ''))
                if start > end:
                    raise ValueError('Start date must be on or before end date.')
            if period == 'intra':
                data = TIME_SERIES_INTRADAY(symbol, interval)
            else:
                data = {'daily': TIME_SERIES_DAILY, 'weekly': TIME_SERIES_WEEKLY,
                        'monthly': TIME_SERIES_MONTHLY}[period](symbol)
            key = next((k for k in data if 'Time Series' in k), None)
            series = data.get(key, {})
            rows = [(stamp, values) for stamp, values in sorted(series.items())
                    if (start is None or start <= datetime.fromisoformat(stamp).date())
                    and (end is None or datetime.fromisoformat(stamp).date() <= end)]
            if not rows:
                raise ValueError('No prices are available for this selection.')
            chart = (pygal.Bar if kind == 'bar' else pygal.Line)(x_label_rotation=45, show_dots=False)
            chart.title = f'{symbol} — {interval + " minute" if period == "intra" else period} prices'
            chart.x_labels = [stamp for stamp, _ in rows]
            for field, name in [('1. open', 'Open'), ('2. high', 'High'), ('3. low', 'Low'), ('4. close', 'Close')]:
                chart.add(name, [float(v[field]) for _, v in rows])
            chart_svg = chart.render(is_unicode=True)
        except requests.RequestException:
            flash('The stock data service is unavailable. Please try again later.')
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            flash(str(exc) if isinstance(exc, ValueError) else 'The stock data response could not be read.')
    return render_template('index.html', symbols=symbols, chart_svg=chart_svg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
