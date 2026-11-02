# FinTrack Flask Frontend Upgrade

## Files
- `web_app.py`: Flask backend and SQLite API. It uses the existing `finance.db` in this folder.
- `templates/index.html`: HTML structure.
- `static/css/style.css`: responsive premium dark fintech styling.
- `static/js/app.js`: interactive charts, form submission, search and transaction history.
- `requirements_web.txt`: Flask dependency.

## Run on macOS
From the folder containing `web_app.py` and `finance.db`:
```bash
python -m pip install -r requirements_web.txt
python web_app.py
```
Open http://127.0.0.1:5000

Keep your existing Streamlit `app.py` and `finance.db`; this Flask version runs separately.
The dashboard reads the existing SQLite table and expects these columns:
`id, transaction_date, transaction_type, amount, category, description`.
