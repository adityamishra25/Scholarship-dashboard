# Student Welfare Scholarship — Data Pipeline

## `transform.ipynb` — Data Cleaning & Transformation Notebook

This Jupyter notebook loads raw district-wise student registry data, cleans and transforms it, merges it with payment and application records, and produces the final `master_dataset.csv` used by the Executive Dashboard.

---

## Workflow Overview

```
Raw CSV Files (5 Districts)
        +  payment_logs.csv
        +  application_status.csv
              │
              ▼
     [ transform.ipynb ]
              │
    ┌─────────┴──────────┐
    │   Clean & Merge    │
    └─────────┬──────────┘
              │
    ┌─────────┴──────────┐
    │  pipeline.db       │  ← SQLite backup
    │  master_dataset.csv│  ← Final output for dashboard
    └────────────────────┘
```

---

## Input Files

| File | Description |
|---|---|
| `registry_Agra.csv` | Student registry — Agra district |
| `registry_Kanpur.csv` | Student registry — Kanpur district |
| `registry_Lucknow.csv` | Student registry — Lucknow district |
| `registry_Prayagraj.csv` | Student registry — Prayagraj district |
| `registry_Varanasi.csv` | Student registry — Varanasi district |
| `payment_logs.csv` | All payment transactions |
| `application_status.csv` | Scholarship application statuses |

All input files should be placed in: `Desktop/data/`

---

## Steps Performed

### 1. Load Data
Reads all 5 district CSV files and the payment & application files using `pandas`.

### 2. Fix Column Names
Kanpur and Lucknow use different column names from the other districts. The notebook renames them to a standard format:

| Original Column | Standardised To |
|---|---|
| `category_type` | `category` |
| `district_name` | `district` |
| `grade_level` | `class` |
| `reg_date` | `registration_date` |

### 3. Combine All Districts
All 5 district tables are concatenated into a single `registry` table — **1,919,976 total students**.

### 4. Remove Duplicates
Duplicate rows are detected and dropped from the registry.

### 5. Clean Age & Class
- **Age:** Extracts numeric age using regex; flags values outside 5–25 as `None`
- **Class:** Standardises all class values to `Class 1` – `Class 12` format; invalid entries become `None`

### 6. Standardise Status Fields
- `application_status` → stripped and title-cased (e.g. `verified` → `Verified`)
- `payment_status` → stripped and title-cased (e.g. `failed` → `Failed`)

### 7. Key Metrics Check
Prints summary counts for:
- Students per district
- Application status breakdown
- Payment status breakdown
- ⚠ Negative payment transactions alert

### 8. Save to SQLite Database
All three cleaned tables (`registry`, `payments`, `applications`) are saved to `pipeline.db` for archival and querying.

### 9. Visualise District Distribution
A quick Plotly bar chart shows student count per district to validate the merge.

### 10. Merge Payment Data
Left-joins `payments` onto `registry` on `student_id`.

### 11. Merge Application Status
Left-joins `applications` onto the merged table on `student_id`.

### 12. Export Master Dataset
The final merged table is saved as:
```
Desktop/data/processed/master_dataset.csv
```

---

## Output Files

| File | Description |
|---|---|
| `processed/master_dataset.csv` | Final merged dataset — 1,919,976 rows × 15 columns |
| `pipeline.db` | SQLite database with all 3 cleaned tables |

---

## Output Dataset Columns

| Column | Description |
|---|---|
| `student_id` | Unique student identifier |
| `district` | District name |
| `category` | Student category (General / SC / ST) |
| `class` | Raw class value |
| `age` | Raw age value |
| `registration_date` | Date of registration |
| `age_clean` | Cleaned numeric age (5–25) |
| `class_clean` | Standardised class (Class 1–12) |
| `txn_id` | Payment transaction ID |
| `amount` | Payment amount (₹) |
| `payment_date` | Date of payment |
| `payment_status` | Success / Failed / Bounced / Processing |
| `app_id` | Application ID |
| `status` | Verified / Rejected / Pending / Unknown |
| `office_code` | Processing office code |

---

## Known Data Quality Issues

| Issue | Count | Action Needed |
|---|---|---|
| Negative payment amounts | 13,548 | Financial audit required |
| Invalid class codes (Class 13–20) | 1,92,352 | Source data correction needed |
| Missing transaction records | 7,75,440 | Students not yet processed |
| Unknown application status | 1,74,807 | Manual review required |
| Missing age (age_clean null) | 4,79,400 | Incomplete source records |

---

## Requirements

```
pip install pandas numpy plotly
```

---

## How to Run

1. Place all input CSV files in `Desktop/data/`
2. Open `transform.ipynb` in Jupyter (via Anaconda)
3. Run all cells top to bottom (`Kernel → Restart & Run All`)
4. Output will be saved to `Desktop/data/processed/master_dataset.csv`

---

## Project Structure

```
Desktop/data/
│
├── registry_Agra.csv
├── registry_Kanpur.csv
├── registry_Lucknow.csv
├── registry_Prayagraj.csv
├── registry_Varanasi.csv
├── payment_logs.csv
├── application_status.csv
│
├── transform.ipynb          ← This notebook
├── dashboard_app.py         ← Plotly Dash dashboard
├── pipeline.db              ← SQLite output
│
└── processed/
    └── master_dataset.csv   ← Final output
```

---

*Prepared for the Student Welfare Scholarship Portal — FY 2024*
