# Threat-Intel-ETL

An Extract, Transform, Load (ETL) pipeline that pulls threat intelligence from AlienVault OTX, stores it in PostgreSQL, and visualizes it in Splunk dashboards.

## Overview

This project automates the collection and analysis of threat intelligence data:
- **Extract:** Fetches pulses and indicators from AlienVault Open Threat Exchange (OTX) using the `OTXv2` Python SDK.
- **Transform:** Processes OTX data into structured tables using Pandas.
- **Load:** Stores data in a PostgreSQL database (`threat_intel`).
- **Visualize:** Displays insights in Splunk via DB Connect with interactive dashboards.
- **Analyze:** Executes SQL queries to extract key metrics and sends results to LLMs (Grok and Claude) for advanced insights.

### Data
- **Pulses:** 7,128 records (top-level threat metadata).
- **Indicators:** 412,985 records (IoCs linked to pulses).

## Splunk Dashboard: Threat Intel Overview
Visualizes OTX threat intelligence with interactive panels:
![Splunk Dashboard: Threat Intel Overview](https://github.com/marky224/Threat-Intel-ETL/blob/main/images/Intel%20Overview%20Dashboard.jpg)
*Splunk Dashboard displaying threat intelligence visualizations, including Indicator Type Breakdown, Expired vs Active Indicators, and more.*

### Panels
1. Indicator Type Breakdown (Pie Chart):
    - Query:
      ```
      | dbxquery connection=threat_intel query="SELECT type, COUNT(*) as count FROM indicators GROUP BY type" | eval percentage=round(count/sum(count)*100, 2) | table type count percentage
      ```
    - Shows distribution of IoC types (e.g., 'IPv4', 'URL').

2. Expired vs Active Indicators (Pie Chart):
    - Query:
      ```
      | dbxquery connection=threat_intel query="SELECT CASE WHEN expiration < NOW() THEN 'Expired' ELSE 'Active' END as status, COUNT(*) as count FROM indicators WHERE expiration IS NOT NULL GROUP BY status" | eval percentage=round(count/sum(count)*100, 2)
      ```
    - Tracks indicator freshness.

3. Top Pulses by Indicator Count (Bar Chart):
    - Query:
      ```
      | dbxquery connection=threat_intel query="SELECT p.id, p.name, COUNT(i.id) as indicator_count FROM pulses p LEFT JOIN indicators i ON p.id = i.pulse_id GROUP BY p.id, p.name ORDER BY indicator_count DESC LIMIT 10"'
      ```
    - Highlights pulses with the most IoCs.

4. Targeted Countries (Bar Chart):
    - Query:
      ```
      | dbxquery connection=threat_intel query="SELECT targeted_countries FROM pulses" | spath input=targeted_countries | mvexpand targeted_countries | stats count by targeted_countries
      ```
    - Shows geographic threat focus.

5. Top Cybersecurity Tags (Bar Chart):
    - Query:
      ```
      | dbxquery connection=threat_intel query="SELECT tags FROM pulses" | spath input=tags | mvexpand tags | stats count by tags | sort -count | head 10
      ```
    - Identifies common threat themes.

### Features
- **Filter**: TLP dropdown for dynamic filtering (token: tlp_filter).
- **Layout**: Pie charts top, line chart middle, bar charts bottom.

### Usage
1. Run ETL: 'python main.py' to refresh data.
2. **View Dashboard**: Splunk > **Dashboards** > **Threat Intel Overview**.

## Project Structure
```
Threat-Intel-ETL/
├── main.py              # ETL pipeline entry point
├── setup_db.py          # Database schema setup
├── src/
│   ├── config.py        # OTX and DB config
│   ├── extract.py       # OTX data fetch
│   ├── transform.py     # Data processing
│   └── load.py          # PostgreSQL load
│   ├── sql_queries.py   # SQL queries for analysis
│   └── send_to_llms.py  # LLM integration for insights
├── images/              # Screenshots of IDE and dashboard
│   ├── pycharm_ide_screenshot.png
│   ├── splunk_dashboard_screenshot.png
│   ├── SQL-queries-python.jpg
│   ├── LLM-summary-python.jpg
├── requirements.txt     # Python dependencies
└── README.md
```
## Dependencies
- requests
- OTXv2
- psycopg2
- pandas
- anthropic

Install with:
```bash
pip install -r requirements.txt
```

## Prerequisites

- **Python 3.8+:** With dependencies (`requirements.txt`).
- **PostgreSQL 17:** Local instance.
- **Splunk Enterprise:** With Splunk DB Connect app.
- **Java JRE 11:** For DB Connect (e.g., OpenJDK from Adoptium).
- **OTX API Key:** From [otx.alienvault.com](https://otx.alienvault.com).
- **Grok API Key:** Visit [console.x.ai](https://console.x.ai), sign up or log in, and navigate to the API section to create a key. You may need to be a team owner or have a developer role to generate the key.
- **Claude API Key:** Sign up at the Anthropic Console, navigate to the API section, and generate a key. You may need to purchase credits or join a waitlist, as direct access can be limited.

## Setup
![PyCharm IDE with ETL Scripts](https://github.com/marky224/Threat-Intel-ETL/blob/main/images/Threat-ETL-Intel%20-%20Python.jpg)
*PyCharm IDE showing ETL scripts (main.py, setup_db.py, extract.py, transform.py) split-screen for development.*


### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/Threat-Intel-ETL.git
cd Threat-Intel-ETL
```

### 2. Install Python Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Environment
- Edit src/config.py with your credentials:
```python
# src/config.py
OTX_API_KEY = "your-64-character-otx-api-key"  # Get from OTX account
GROK_API_KEY = "your-grok-api-key"             # Get from console.x.ai
CLAUDE_API_KEY = "your-claude-api-key"         # Get from Anthropic ConsoleDB_CONFIG = {
    "dbname": "threat_intel",
    "user": "your-postgres-username",          # e.g., "postgres"
    "password": "your-postgres-password",      # e.g., a strong password
    "host": "localhost",
    "port": "5432"
}
```
- Note: Replace placeholders with your OTX API key and PostgreSQL credentials (e.g., postgres/N$zt8xHE!xaf5nREff worked in testing).

### 4. Set Up PostgreSQL
- Install PostgreSQL 17 (e.g., via installer on Windows).
- Create database:
```bash
psql -U your-postgres-username -c "CREATE DATABASE threat_intel;"
```
- Run setup_db.py to create tables:
bash
```
python setup_db.py
```
5. Run the ETL Pipeline
bash
```
python main.py
```
- Fetches OTX data, transforms it, and loads it into threat_intel.

### 6. Configure Splunk
1. **Install Splunk Enterprise**:
  - Download from 'splunk.com', install on Windows.
  - Default: 'http://localhost:8000', user: 'admin'.

2. **Install DB Connect**:
  - In Splunk: **Apps** > **Find More Apps** > “Splunk DB Connect” > Install.

3. **Set JRE Path**:
  - **DB Connect** > **Configuration** > **Settings** > **General**.
  - **JRE Installation Path**: 'C:\Program Files\Eclipse Adoptium\jre-11.0.26.4-hotspot'.

4. **Create Identity**:
  - **Configuration** > **Identities** > **New Identity**.
  - Name: 'postgres_threat_intel', Username: 'your-postgres-username', Password: 'your-postgres-password'.

5. **Create Connection**:
  - **Configuration** > **Databases** > **New Database Connection**.
  - Name: 'threat_intel', Type: PostgreSQL, Host: 'localhost', Port: '5432', Database: 'threat_intel', Identity: 'postgres_threat_intel'.
  - Test and save.

### 7. SQL Queries for Threat Analysis

The pipeline uses SQL queries to extract meaningful metrics from the PostgreSQL database, defined in `src/sql_queries.py`:

- **Total Pulses and Indicators:** Counts the total number of pulses and indicators.
- **Indicator Types:** Identifies the top 5 indicator types by count (e.g., FileHash-SHA256, domain).
- **Top Targeted Countries:** Lists the top 5 countries targeted by threats.
- **Top Threat Tags:** Identifies the top 5 tags (e.g., malware, phishing).
- **Expired vs. Active Indicators:** Counts expired and active indicators.
- **Top Pulse by Indicator Count:** Finds the pulse with the most associated indicators.
- **Pulse Trends Over Time:** Tracks pulses created each month over the last 6 months.
- **Top Industries:** Identifies the top 5 industries targeted by threats.

These queries were executed on May 15, 2025, producing results used for further analysis.

### 8. Leveraging LLMs for Insights

The pipeline sends query results to two LLMs—Grok (created by xAI) and Claude—for deeper insights, implemented in `src/send_to_llms.py`:

![LLM Summary Python Script](https://github.com/marky224/Threat-Intel-ETL/blob/main/images/LLM-summary-python.jpg)

*Results from the Python script for sending query results to LLMs for analysis.*

### Key Findings (as of May 15, 2025):

- **Total Pulses:** 7,128
- **Total Indicators:** 412,985
- **Active Indicators:** 412,817 (99.96%)
- **Top Indicator Type:** FileHash-SHA256 (134,393 indicators)
- **Top Targeted Countries:** United States (426 pulses), Ukraine (280), Russia (237)
- **Top Threat Tags:** Malware (608 pulses), Phishing (564), Ransomware (489)
- **Top Industries:** Government (838 pulses), Finance (381)
- **Top Pulse:** "Highway Robbery 2.0: How Attackers Are Exploiting Toll Systems in Phishing Scams" (29,930 indicators)

Both LLMs highlighted the need for enhanced protection against phishing and advanced persistent threats (APTs), especially for critical infrastructure and government systems.

## Notes
- **Data Volume:** 7,128 pulses, 412,985 indicators as of May 15, 2025.
- **Splunk Access**: Localhost:8000, admin credentials required.

## Contributing
Pull requests welcome! Focus on new visualizations, performance tweaks, or enhanced LLM analysis.
