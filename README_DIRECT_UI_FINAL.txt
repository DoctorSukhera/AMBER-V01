# AMBER V0.1 — DIRECT UI FINAL

This version removes embedded infographic PNGs from the application.

Only one image asset remains:
- `assets/hitsz_logo.png`

Everything else is built directly in Streamlit / HTML / CSS / Plotly:
- Home scientific rationale
- research workflow
- Calculator workflow
- Molecular workflow
- Validation dashboards
- Development sequence
- project credits

## Public pages
1. Home
2. AMBER Calculator
3. DNA Compass / Method
4. Model & Validation
5. About AMBER

## Calculator behavior
The calculator uses a Streamlit form.
Nothing is calculated automatically.
The user must click `CALCULATE AMBER SCORE`.

The report download button is rendered outside the form, avoiding
`StreamlitInvalidLayoutContextError`.

## Scientific safety
No real AMBER AUC, sensitivity, specificity, thresholds, calibration
statistics or model-lock date are claimed in V0.1.

## Deploy
Upload/replace:
- app.py
- requirements.txt
- assets/hitsz_logo.png
