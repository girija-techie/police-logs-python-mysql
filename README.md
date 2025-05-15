# 🚦 Digital Ledger for Police Post Logs
A Streamlit-based interactive dashboard that analyzes and explores traffic stop records stored in a MySQL database. This tool provides insightful visualizations, deep query-based insights, and a smart prediction system for evaluating traffic stop outcomes.

## 📌 Features
- ✅ Interactive Data Exploration: Filter by age, gender, time, and more
- 📊 Visual Insights: Real-time bar charts for traffic violations
- 🔍 Dynamic SQL Queries: Choose from pre-built analytical questions
- 🤖 Prediction Interface: Get stop outcomes based on custom inputs
- 🧠 Window Functions & Subqueries: Advanced SQL analytics
- 🗃️ MySQL Integration: Efficient connection and data fetching

## ⚙️ Setup Instructions
### 🔧 Prerequisites
- Python 3.7+
- MySQL Server (with a database named `digital_ledger`)
- `traffic_records` table with appropriate schema

## 📦 Required Python Libraries
Install dependencies using:
```bash
pip install streamlit pandas numpy mysql-connector-python
```
## 🚀 Running the Application
Run the Streamlit app with:
```bash
streamlit run app.py
```
Replace app.py with the name of your script if different.
## 🧠 Application Modules
### 1.Dashboard Overview
- Displays entire traffic_records dataset
- Highlights traffic violations with filtering by:
  - Driver Age
  - Driver Gender
### 2.Query & Explore
- Select from 20+ analytical queries:
  - Top vehicles involved in drug-related stops
  - Gender distribution by country
  - Time-of-day analysis for arrests
  - Search and arrest rate trends by violation
### 3. Predict Outcome and Violation
- Enter inputs:
  - Date & Time
  - Country, Gender, Age, Race
  - Search Type & Duration
  - Drug-Related Status
  - Vehicle Number
- Predicts:
  - Violation committed
  - Outcome (arrested, warning, etc.)
  - Search conducted
  - Drug involvement
## 🗂️ Example Query Insights
Some of the built-in analytical queries include:
#### - 🕐 Time-based Analysis:
```bash
SELECT HOUR(stop_time), COUNT(*) FROM traffic_records GROUP BY HOUR(stop_time);
```
#### - 👮 Top 5 Violations with Highest Arrest Rate:
```bash
SELECT violation, COUNT(CASE WHEN is_arrested = 1 THEN 1 END) / COUNT(*) * 100 as arrest_rate FROM traffic_records GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5
```
#### -🌍 Drug-Related Stops by Country:
```bash
SELECT country_name, COUNT(CASE WHEN drugs_related_stop = 1 THEN 1 END) / COUNT(*) * 100 FROM traffic_records GROUP BY country_name
```
## 📊 Schema Reference
Table: `traffic_records`
| Column               | Type         | Description                      |
| -------------------- | ------------ | -------------------------------- |
| ID                   | int          | Primary Key (auto-increment)     |
| stop\_date           | date         | Date of stop                     |
| stop\_time           | time         | Time of stop                     |
| country\_name        | varchar(100) | Country of stop                  |
| driver\_gender       | char(1)      | Gender ('M' or 'F')              |
| driver\_age          | int          | Age of driver                    |
| driver\_race         | varchar(255) | Race of driver                   |
| violation\_raw       | varchar(255) | Raw violation text               |
| violation            | varchar(255) | Cleaned violation category       |
| search\_conducted    | tinyint(1)   | 1 if search was conducted        |
| search\_type         | varchar(255) | Type of search                   |
| stop\_outcome        | varchar(20)  | Outcome (arrested, warning, etc) |
| is\_arrested         | tinyint(1)   | 1 if arrested                    |
| stop\_duration       | varchar(20)  | Estimated stop time              |
| drugs\_related\_stop | tinyint(1)   | 1 if drug-related                |
| vehicle\_number      | char(10)     | License plate                    |

# Project Setup Guide

## 🔧 Setting Up the Python Environment

This guide walks you through setting up a virtual environment and installing required packages from `requirements.txt`.

### 1. Create a Virtual Environment

#### Windows
```bash
python -m venv env
.\env\Scripts\Activate.ps1
```

#### Linux/macOS
```bash
python3 -m venv env
source env/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### This is how to collect virtual environment packages to requirement.txt
### 3. Freeze Installed Packages
```bash
pip freeze > requirements.txt
```
## 🤝 Contributions
Pull requests are welcome! For major changes, please open an issue first.
## 📄 License
This project is open-source and available under the MIT License.
