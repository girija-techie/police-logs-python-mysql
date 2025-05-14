import streamlit as st
import pandas as pd
import numpy as np
import mysql.connector
from datetime import time, date
import re # regular expression

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    port = 3307
)

cursor = mydb.cursor()

cursor.execute("USE digital_ledger;")


def get_data(query):

    cursor.execute(query)
    rows = cursor.fetchall() # assign table data
    column_names = [i[0] for i in cursor.description] # assign column names -> List

    df = pd.DataFrame(rows, columns=column_names)
 
    return df # output is dataframe

st.title("Digital Ledger for Police Post Logs")
st.header("🚦 Traffic Records")

tableRecords = get_data("SELECT * FROM traffic_records;")
st.dataframe(tableRecords)

st.header("📊 Traffic Violation Insights at a Glance")
 
age_df = get_data("SELECT DISTINCT(driver_age) FROM traffic_records ORDER BY driver_age;")

# Create two columns
c1, c2 = st.columns(2)

with c1:
    sa = st.selectbox('Driver Age',list(age_df["driver_age"]),index=0)

with c2:
    # Mapping for display and internal value
    gender_options = {
        "Male": "M",
        "Female": "F"
    }
    sg_label = st.selectbox('Driver Gender', list(gender_options.keys()),index=0)
    sg = gender_options[sg_label]

# create bar chart
barChart = get_data(f"SELECT violation, COUNT(violation) FROM `traffic_records` WHERE driver_age = {sa} and driver_gender = '{sg}' GROUP BY violation;")
barChart = barChart.set_index('violation')
st.bar_chart(barChart)

st.header("🧮 Query & Explore")

queries_dict = {
    "What are the top 10 vehicles involved in drug-related stops?": "SELECT * FROM traffic_records LIMIT 10",
    "Which vehicles were most frequently searched?": "SELECT vehicle_number, COUNT(*) AS search_count FROM traffic_records WHERE search_conducted = 1 GROUP BY vehicle_number ORDER BY search_count DESC LIMIT 10",
    "Which driver age group had the highest arrest rate?": "SELECT driver_age, COUNT(*) AS arrest_count from traffic_records WHERE is_arrested = 1 GROUP BY driver_age ORDER BY arrest_count DESC LIMIT 10",
    "What is the gender distribution of drivers stopped in each country?": "SELECT country_name, driver_gender, COUNT(*) as stop_count from traffic_records GROUP BY country_name, driver_gender",
    "Which race and gender combination has the highest search rate?": "SELECT driver_gender, driver_race, COUNT(CASE WHEN search_conducted = 1 THEN 1 END) * 1.0 / COUNT(*) as search_rate FROM `traffic_records` GROUP BY driver_gender, driver_race ORDER BY search_rate DESC LIMIT 1",
    "What time of day sees the most traffic stops?": "SELECT HOUR(stop_time) AS stop_hour, COUNT(*) AS stop_count FROM traffic_records GROUP BY stop_hour ORDER BY stop_count DESC LIMIT 1",
    "What is the average stop duration for different violations?": "SELECT ROUND(AVG(stop_duration)) as average_duration, violation FROM traffic_records GROUP BY violation ORDER BY average_duration DESC",
    "Are stops during the night more likely to lead to arrests?": "SELECT CASE WHEN HOUR(stop_time) BETWEEN 6 AND 17 THEN 'Day' ELSE 'Night' END AS time_of_day, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests, ROUND(100.0 * SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percent FROM traffic_records GROUP BY time_of_day",
    "Which violations are most associated with searches or arrests?": "SELECT violation, search_conducted, is_arrested, COUNT(*) as violation_count FROM traffic_records WHERE search_conducted = 1 OR is_arrested = 1 GROUP BY violation ORDER BY violation_count DESC LIMIT 1",
    "Which violations are most common among younger drivers (<25)?": "SELECT violation, driver_age, COUNT(*) as violation_count FROM traffic_records WHERE driver_age < 25 GROUP BY violation ORDER BY violation_count DESC;",
    "Is there a violation that rarely results in search or arrest?": "SELECT violation, COUNT(*) as rare_violation_count FROM traffic_records WHERE search_conducted = 1 or is_arrested = 1 GROUP BY violation ORDER BY rare_violation_count ASC LIMIT 1",
    "Which countries report the highest rate of drug-related stops?": "SELECT country_name, COUNT(CASE WHEN drugs_related_stop = 1 THEN 1 END) / COUNT(*) * 100 as 'drugs_stop_rate in %' FROM traffic_records GROUP BY country_name ORDER BY 'drugs_stop_rate in %' DESC LIMIT 1;",
    "What is the arrest rate by country and violation?": "SELECT country_name, violation, COUNT(CASE WHEN is_arrested = 1 THEN 1 END) / COUNT(*) * 100 as 'arrest_rate in %' FROM traffic_records GROUP BY country_name, violation",
    "Which country has the most stops with search conducted?": "SELECT country_name, COUNT(*) as stop_count FROM traffic_records WHERE search_conducted = 1 GROUP BY country_name ORDER BY stop_count DESC LIMIT 1",
    "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)":"select country_name, stop_year, total_stops, arrest_count from (SELECT country_name, YEAR(stop_date) AS stop_year, COUNT(*) over (PARTITION by country_name) as total_stops, COUNT(case when is_arrested = 1 THEN 1 END) over (PARTITION BY country_name) AS arrest_count FROM traffic_records) as country_based_counts GROUP BY country_name, stop_year;",
    "Driver Violation Trends Based on Age and Race (Join with Subquery)":"SELECT * FROM ( SELECT CASE WHEN driver_age < 18 THEN 'Under 18' WHEN driver_age BETWEEN 18 AND 24 THEN '18-24' WHEN driver_age BETWEEN 25 AND 34 THEN '25-34' WHEN driver_age BETWEEN 35 AND 44 THEN '35-44' WHEN driver_age BETWEEN 45 AND 54 THEN '45-54' WHEN driver_age BETWEEN 55 AND 64 THEN '55-64' ELSE '65+' END AS age_group, driver_race, violation, COUNT(*) AS total_stops FROM traffic_records GROUP BY age_group, driver_race, violation ) AS v JOIN ( SELECT DISTINCT violation FROM traffic_records ) AS ref_violations ON v.violation = ref_violations.violation ORDER BY v.age_group, v.driver_race, v.total_stops DESC",
    "Time Period Analysis of Stops (Joining with Date Functions), Number of Stops by Year,Month, Hour of the Day":"SELECT YEAR(stop_date) AS stop_year, MONTH(stop_date) AS stop_month, HOUR(stop_time) AS stop_hour, COUNT(*) AS stop_count, ROW_NUMBER() OVER (PARTITION BY YEAR(stop_date) ORDER BY MONTH(stop_date), HOUR(stop_time)) AS monthly_rank FROM traffic_records WHERE stop_date IS NOT NULL AND stop_time IS NOT NULL GROUP BY YEAR(stop_date), MONTH(stop_date), HOUR(stop_time) ORDER BY stop_year, stop_month, stop_hour",
    "Violations with High Search and Arrest Rates (Window Function)":"SELECT violation, total_arrest / COUNT(*) AS arrest_rate, total_search / COUNT(*) AS search_rate FROM (SELECT violation, COUNT(CASE WHEN is_arrested = 1 THEN 1 END) OVER (PARTITION BY violation) AS total_arrest, COUNT(CASE WHEN search_conducted = 1 THEN 1 END) OVER (PARTITION BY violation) AS total_search FROM traffic_records) AS violation_details GROUP BY violation ORDER BY arrest_rate, search_rate",
    "Driver Demographics by Country (Age, Gender, and Race)":"SELECT country_name, driver_gender, driver_race, CASE WHEN driver_age < 18 THEN 'under 18' WHEN driver_age BETWEEN 18 and 25 THEN '18-25' WHEN driver_age BETWEEN 26 and 35 THEN '26-35' WHEN driver_age BETWEEN 36 AND 45 THEN '36-45' WHEN driver_age BETWEEN 46 and 55 THEN '45-55' WHEN driver_age BETWEEN 56 and 65 THEN '56-65' ELSE '65+' END as age_group, COUNT(*) as violation_count FROM traffic_records GROUP BY country_name, driver_gender, driver_age, age_group ORDER BY country_name, driver_gender, driver_age, age_group",
    "Top 5 Violations with Highest Arrest Rates": "SELECT violation, COUNT(CASE WHEN is_arrested = 1 THEN 1 END) / COUNT(*) * 100 as arrest_rate FROM traffic_records GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5"
    }

question = st.selectbox('Select Query', list(queries_dict.keys()),index=0)

query = queries_dict[question]

qs_df = get_data(query)

st.dataframe(qs_df)


st.header("🧠 Predict Outcome and Violation")

def convert_duration(text):
    if "Min" in text:
        if "+" in text:
            # Handle "60+ Min"
            number = re.findall(r"\d+", text)
            return f"more than {number[0]} minutes"
        elif "-" in text:
            # Handle "0-15 Min"
            return re.sub(r"(\d+)-(\d+)\s*Min", r"\1 to \2 minutes", text)
    return text  # Return as-is if it doesn't match

with st.form("my_form", clear_on_submit=False):

    # Date input
    selected_date = st.date_input(
        "Select a date",
        value=date.today(),  # default value
        min_value=date(2019, 12, 31),
        max_value=date(2030, 12, 31)
    )

    # Time input
    selected_time = st.time_input(
        "Select a time",
        value=time(12, 0), # default is 12:00 PM
        step=60 
    )

    # Countries list from DB
    country_df = get_data("SELECT DISTINCT(country_name) FROM traffic_records ORDER BY country_name")
    selected_country = st.selectbox('Choose Country Name',["-- Select an option --"] + list(country_df["country_name"]),index=0)

    # Genders list
    gender_name = st.selectbox('Choose Driver Gender', ["-- Select an option --"] + list(gender_options.keys()),index=0)
    selected_gender = ''
    if(gender_name != "-- Select an option --"):
        selected_gender = gender_options[gender_name]

    # Age list from DB
    selected_age = st.selectbox('Choose Driver Age',["-- Select an option --"] + list(age_df["driver_age"]),index=0)

    # Race list from DB
    race_df = get_data("SELECT DISTINCT(driver_race) FROM traffic_records ORDER BY driver_race")
    selected_race = st.selectbox('Choose Driver Race',["-- Select an option --"] + list(race_df["driver_race"]),index=0)

    search_conduct_dict = {
        'Yes': 1, 
        'No': 0
    }
    search_conducted = st.selectbox('Was a Search Conducted',["-- Select an option --"] + list(search_conduct_dict.keys()),index=0)
    if(search_conducted != "-- Select an option --"):
        is_search_conducted = search_conduct_dict[search_conducted]

    search_type_df = get_data("SELECT DISTINCT(search_type) FROM traffic_records ORDER BY search_type")
    selected_search_type = st.selectbox('Choose Search Type',["-- Select an option --"] + list(search_type_df["search_type"]))

    drug_related = st.selectbox('Was it Drug Related',["-- Select an option --"] + list(search_conduct_dict.keys()),index=0)
    if(drug_related != "-- Select an option --"):
        is_drug_related = search_conduct_dict[drug_related]

    stop_duration_df = get_data("SELECT DISTINCT(stop_duration) FROM traffic_records ORDER BY stop_duration")
    selected_stop_duration = st.selectbox('Choose Search Type',["-- Select an option --"] + list(stop_duration_df["stop_duration"]))

    entered_vehicle_number = st.text_input("Enter Vehicle Number", key="my_input")

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

    # Prediction queries
    if submitted:
        prediction_query = "SELECT *, DATE_FORMAT(stop_time, '%h:%i %p') AS readable_time FROM traffic_records WHERE "
        conditions = []
        if(selected_date):
            conditions.append(f"stop_date = '{selected_date}'")
        
        if(selected_time):
            conditions.append(f"stop_time = '{selected_time}'")
        
        if(selected_country != '-- Select an option --'):
            conditions.append(f"country_name = '{selected_country}'")
        
        if(selected_gender != '-- Select an option --' and selected_gender != ''):
            conditions.append(f"driver_gender = '{selected_gender}'")
            
        if(selected_age != '-- Select an option --'):
            conditions.append(f"driver_age = {selected_age}")

        if(selected_race != '-- Select an option --'):
            conditions.append(f"driver_race = '{selected_race}'")
        
        if(selected_search_type != '-- Select an option --'):
            conditions.append(f"search_type = '{selected_search_type}'")

        if(search_conducted != '-- Select an option --'):
            conditions.append(f"search_conducted = {is_search_conducted}")

        if(drug_related != '-- Select an option --'):
            conditions.append(f"drugs_related_stop = {is_drug_related}")

        if(selected_stop_duration != '-- Select an option --'):
            conditions.append(f"stop_duration = '{selected_stop_duration}'")

        if(entered_vehicle_number != ''):
            conditions.append(f"vehicle_number = '{entered_vehicle_number.upper()}'")

        final_query = prediction_query + " and ".join(conditions) + " LIMIT 1"

        st.write(prediction_query)
        st.write(" and ".join(conditions))
        st.write(" LIMIT 1")
        st.write(final_query)

        query_df = get_data(final_query)
        if len(query_df):
            data = query_df.iloc[0]
            st.write(f"A **{data['driver_age']}-year-old {'male' if data['driver_gender'] == 'M' else 'female'} driver** was stopped at **{data['readable_time']}** for **{data['violation'].lower() if data['violation'] != 'Other' else 'unspecified'}** reason. {'He' if data['driver_gender'] == 'M' else 'She'} was **{data['stop_outcome'].lower()}** {'with search conducted' if data['search_conducted'] == 1 else 'without a search being conducted'}. The stop lasted between **{convert_duration(data['stop_duration'])}** and the case was **{'related to drugs(💊)' if data['drugs_related_stop'] == 1 else 'not related to drugs'}**.")
        else:
            st.write("No Results Found")


