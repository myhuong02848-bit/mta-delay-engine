# NYC Subway Operational Delay & Bottleneck Analysis Engine

[🔗 Click here to view the live interactive reports](https://myhuong02848-bit.github.io/mta-delay-engine/)

An end-to-end data engineering and analytical pipeline designed to ingest, clean, index, and analyze multi-year NYC MTA subway delay datasets (2020–2024). The project replaces manual spreadsheet workflows with an automated Python pipeline, relational SQLite indexing, SQL window functions, and interactive visualizations to uncover operational bottlenecks across shared transit corridors.

---

## Architecture & Data Flow

1. Database (Storage & Ingestion)
    - Raw Data: MTA data (csv) from data.ny.gov
    - Automated Ingestion (schema cast & clean)
    - Relational SQLite (B-Tree Composite Indexes)
2. Analytical Engine (SQL)
    - Window Functions (LAG) + Interlining Bottlenecks
3. Report
    - Interactive Reports (Plotly)

---

## Key Features

- **Automated Data Pipeline (`src/ingest.py`):** Object-oriented ingestion module that standardizes inconsistent headers, handles missing records, and normalizes datetime formats.
- **Relational Storage & Indexing:** Direct writes to SQLite with composite B-Tree indexes (`line`, `year_month`) for sub-millisecond query retrieval.
- **Advanced SQL Analytics (`src/analyze.py`):** Executes window functions (`LAG() OVER()`), Month-over-Month (MoM) growth calculations, and line contribution metrics.
- **Interactive Visual Reporting (`src/visualize.py`):** Generates standalone interactive Plotly visualizations for line-by-line distribution and time-series trends.
- **Automated Testing Suite (`tests/test_ingestion.py`):** Unit testing using `pytest` to ensure schema validation, numeric casting, and database persistence reliability.

---

## Key Operational Insights

- **Systemic Bottleneck Line:** The **N Line** recorded the highest cumulative delay volume (**171,808 delays**), primarily driven by interlining merge conflicts and shared trunk line dependencies along Broadway.
- **Peak Operational Disruption:** **July 2022** marked the peak delay month (**46,482 delays**), corresponding with rapid post-pandemic ridership recovery and seasonal track maintenance.
- **Concentration:** Delay distributions are highly concentrated in a small subset of shared interline corridors rather than evenly distributed across independent routes.

---

## Tech Stack

- **Language:** Python 3.9+
- **Data Engineering:** `pandas`, `numpy`, `openpyxl`
- **Database & Querying:** SQLite3, SQL Window Functions
- **Visualization:** `plotly`
- **Testing:** `pytest`

---

## Project Structure

mta-delay-engine/
├── data/
│   ├── raw/                 # Source MTA delay dataset (data.gov)
│   └── processed/           # SQLite database (mta_delays.db)
├── reports/                 # Generated interactive HTML visualizations
├── src/
│   ├── ingest.py            # Ingestion, schema validation, database loader
│   ├── analyze.py           # SQL analytics & window function metrics
│   └── visualize.py         # Plotly interactive chart generation
├── tests/
│   └── test_ingestion.py    # Pytest unit test suite
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation# mta-delay-engine
