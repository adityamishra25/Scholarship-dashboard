# Student Welfare Scholarship Dashboard
## Senior Official Executive Dashboard — FY 2024

---

## Quick Start

### 1. Install Dependencies
```
pip install dash plotly pandas
```

### 2. Place Your Data
Ensure the CSV is at:
```
C:\Users\aditya_m\Desktop\data\processed\master_dataset.csv
```
(The app auto-detects this path)

### 3. Run the Dashboard
```
python dashboard_app.py
```

### 4. Open in Browser
```
http://localhost:8050
```

---

## What the Dashboard Shows

### 🚨 Critical Alerts Banner
- Negative-amount transactions (financial anomalies)
- Applications stuck in "Unknown" status
- Combined payment failure + bounce rate

### 📊 7 KPI Cards
| Metric | Description |
|---|---|
| Total Students | 1.92M across 5 districts |
| Total Disbursed | Sum of all positive payments (₹ Crores) |
| Verified % | Share of verified applications |
| Rejection Rate ⚠ | Flagged red — ~18% rejection |
| Pending Review ⚠ | Applications awaiting decision |
| Payment Failures ⚠ | Failed + Bounced combined |
| Anomalous Transactions ⚠ | Negative-amount records |

### 📈 6 Visualizations
1. **Application Status by District** — stacked bar (Verified / Rejected / Pending / Unknown)
2. **Payment Status Donut** — Success / Processing / Failed / Bounced
3. **Monthly Registration Trend** — 2024 full-year line chart
4. **Status by Category** — General / SC / ST breakdown
5. **Office-wise Rejection Rate** — colour-coded bar for 15 offices
6. **Disbursement Amount Distribution** — histogram of payment amounts

### 📋 District Summary Table
Sortable table with: Total, Verified, Rejected, Pending, Unknown, Disbursed, Rejection Rate, Payment Failure Rate, Negative Amount count — per district.

---

## Key Findings for Senior Officials

| Issue | Magnitude |
|---|---|
| Applications with Unknown status | 174,807 (9.1%) |
| Negative-amount transactions | 13,548 |
| Overall rejection rate | ~18.2% |
| Payment failure + bounce rate | ~29.8% |
| Pending (unresolved) applications | ~18.2% |

All 5 districts (Agra, Varanasi, Prayagraj, Lucknow, Kanpur) show similar patterns — indicating systemic rather than district-specific issues.
