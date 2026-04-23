import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="CA Work Diary Live", layout="centered")

st.title("📱 CA Office Work Diary (LIVE)")

# -----------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import json
from oauth2client.service_account import ServiceAccountCredentials

creds_dict = st.secrets["gcp_service_account"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

sheet = client.open("WorkDiary").sheet1

# -----------------------------
# LOAD DATA
# -----------------------------
data = sheet.get_all_records()
df = pd.DataFrame(data)

# -----------------------------
# STAFF LIST
# -----------------------------
staff_data = {
    "Hitesh": "Partner",
    "Rahul": "Article",
    "Sneha": "Employee",
    "Amit": "Article"
}

# -----------------------------
# FUNCTION: CALCULATE HOURS
# -----------------------------
def calculate_hours(time_in, time_out):
    try:
        if time_out.strip() == "":
            return 0
        t1 = datetime.strptime(time_in, "%H:%M")
        t2 = datetime.strptime(time_out, "%H:%M")
        return round((t2 - t1).seconds / 3600, 2)
    except:
        return 0

# -----------------------------
# WHO IS WORKING
# -----------------------------
st.subheader("🟢 Who is Working Today")

today = str(datetime.today().date())

if not df.empty:
    working_df = df[(df["Date"] == today) & (df["Status"] == "Working")]

    if not working_df.empty:
        for _, row in working_df.iterrows():
            st.success(f"{row['Name']} ({row['Role']}) - Since {row['Time In']}")
    else:
        st.info("No active work entries")

# -----------------------------
# ENTRY FORM
# -----------------------------
st.subheader("➕ Add Work Entry")

name = st.selectbox("Select Person", list(staff_data.keys()))
role = staff_data[name]

st.write(f"Role: **{role}**")

date = st.date_input("Date", datetime.today())

time_in = st.text_input("Time In (HH:MM)")
time_out = st.text_input("Time Out (Leave blank if working)")

client_name = st.text_input("Client Name")

work_type = st.selectbox(
    "Work Type",
    ["Audit", "GST", "Income Tax", "Accounting", "ROC", "Other"]
)

description = st.text_area("Work Description")

if st.button("Save Entry"):
    hours = calculate_hours(time_in, time_out)
    status = "Working" if time_out.strip() == "" else "Completed"

    new_row = [
        str(date), name, role, time_in, time_out,
        client_name, work_type, description,
        hours, status
    ]

    sheet.append_row(new_row)

    st.success(f"✅ Saved | Hours: {hours}")

# -----------------------------
# TODAY VIEW
# -----------------------------
st.subheader("📊 Today's Work")

if not df.empty:
    today_df = df[df["Date"] == today]
    st.dataframe(today_df, use_container_width=True)

# -----------------------------
# MONTHLY REPORT
# -----------------------------
st.subheader("📅 Monthly Report")

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

    month_list = df["Date"].dt.to_period("M").dropna().astype(str).unique()

    selected_month = st.selectbox("Select Month", sorted(month_list))

    monthly_df = df[df["Date"].dt.to_period("M").astype(str) == selected_month]

    summary = monthly_df.groupby("Name").agg({
        "Working Hours": "sum",
        "Work Type": "count"
    }).reset_index()

    summary.columns = ["Name", "Total Hours", "Total Entries"]

    st.dataframe(summary, use_container_width=True)