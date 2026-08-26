# Dash Interactive Dashboard (demo)

This repository contains a small interactive Dash app demonstrating:
- Slicers: multi-select dropdowns and checkboxes
- Range slider (numeric range)
- Clickable chart (click a bar to filter another chart)
- Cross-filtering between charts and a simple detail table

Demo uses Plotly's built-in `tips` dataset (so no data file is required). Replace the data with your CSV by changing the `df = px.data.tips()` line to `pd.read_csv("data/yourfile.csv")`.

Quick run (local)
1. Create virtualenv and install:
   ```
   python -m venv venv
   source venv/bin/activate   # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt
   ```
2. Run:
   ```
   python app.py
   ```
3. Open http://127.0.0.1:8050

Docker
1. Build:
   ```
   docker build -t dash-demo .
   ```
2. Run:
   ```
   docker run -p 8050:8050 dash-demo
   ```
3. Open http://127.0.0.1:8050

What the UI does
- Left column: controls (Days multi-select, Sex, Smoker, Total bill range, Clear selection)
- Top chart: bar chart showing counts grouped by Day; clicking a bar focuses/filters the details to that day
- Middle chart: scatter (total bill vs tip) that updates based on filters and bar clicks
- Bottom: table showing first matching rows

Notes
- The app exposes `server` (so it works with gunicorn in Docker / Render / Heroku).
- For production, we'll likely want to adjust worker count, enable logging, and optionally use a small reverse proxy.

Next actions I can do for you
- Add a GitHub Actions workflow to deploy to Heroku or Render on push (I'll add the workflow file and instructions to set required repo secrets).
- Replace sample data with your CSV (you can upload it or I can add a placeholder `data/sample.csv`).
- Add additional charts (time series, KPIs, maps), download CSV/export, authentication, or layout improvements.
