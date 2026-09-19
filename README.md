# APL Logistics — Delivery Performance & Delay Risk Dashboard

Project 3 for the Unified Mentor Business Analyst internship.

## Objective

Analyze delivery performance, delay risk and logistics efficiency using the supplied APL Logistics dataset.

## Core calculation

**Delivery Gap = Days for shipping (real) − Days for shipment (scheduled)**

- Delayed: Delivery Gap > 0
- On-time: Delivery Gap = 0
- Early: Delivery Gap < 0

## Dashboard modules

1. Delivery Performance Overview
2. Delay Risk Analysis
3. Shipping Mode Efficiency
4. Regional & Market Diagnostics
5. Customer Segment Impact

## Filters

- Shipping Mode
- Order Region
- Market
- Customer Segment

The supplied dataset does not contain a date field, so a date-range filter is not implemented in this version.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

This project can be deployed using Streamlit Community Cloud after the repository is pushed to GitHub.

## Data handling note

The source dataset contains customer-identification fields. The dashboard intentionally does not display customer names, street addresses or ZIP codes.
