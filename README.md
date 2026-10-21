# Stock Data Visualizer

**Python · Flask · Alpha Vantage API · Pygal · Docker**

A web application for exploring open, high, low and closing stock prices as line or bar charts. Choose a stock, daily/weekly/monthly series and date range, or inspect intraday prices at 1, 5, 15, 30 or 60-minute intervals.

## What this demonstrates

- External API integration and transformation of time-series responses into SVG charts.
- Date-range filtering, chronological ordering and server-side form validation.
- Graceful handling of network failures, unavailable series and provider rate limits.
- Configuration through environment variables rather than a committed API key.

## Run locally

```bash
python -m venv .venv
# Activate the environment for your operating system.
pip install -r requirements.txt
```

Set `ALPHAVANTAGE_API_KEY` to your own provider key and optionally set `SECRET_KEY`. `.env.example` lists the names; running Python directly does not load `.env` automatically. Then run:

```bash
python app.py
```

Open http://localhost:5000. Data availability depends on your API access and limits; unavailable requests display an explanation. This is a visualization project, not a forecasting model.

For Docker, copy `.env.example` to `.env`, fill in the values, and run `docker compose up --build`. Open http://localhost:5005.

## Checks

```bash
python -m unittest discover -s tests -v
```

Five checks exercise daily/intraday rendering, invalid dates, unavailable/empty provider responses, and request timeout configuration. API calls are mocked; no live provider access or Docker build was tested in the portfolio cleanup.

## Improvements in this edition

Repaired the intraday function call and undefined data-key path, corrected timestamp filtering and form field visibility, added missing dependencies, displayed errors in the page, removed tracked bytecode, and replaced the hard-coded key with environment configuration. Rotate any previously committed provider key; deleting it from the latest source does not erase Git history.
