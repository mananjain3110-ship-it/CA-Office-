import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Work Diary Test", layout="centered")

st.title("🧪 Work Diary (Testing Mode)")

# -----------------------------
# Session Storage (Temporary)
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Name", "Role", "Time In", "Time Out",
        "Client", "Work Type", "Description", "Hours", "Status"
    ])

df = st.session_state.data

# -----------------------------
# Staff List
# -----------------------------
staff = {
    "Hitesh": "Partner",
    "Rahul": "Article",
    "Sneha": "Employee"
}

# -----------------------------
# Time Calculation
# -----------------------------
def calc_hours(t1, t2):
    try:
        if t2.strip() == "":
            return 0
        t1 = datetime.strptime(t1, "%H:%M")
        t2 = datetime.strptime(t2, "%H:%M")
        return round((t2 - t1).seconds / 3600, 2)
    except:
        return 0

# -----------------------------
# Entry Form
# -----------------------------
st.subheader("➕ Add Entry")

name = st.selectbox("Select Person", list(staff.keys()))
role = staff[name]

date = st.date_input("Date", datetime.today())
time_in = st.text_input("Time In (HH:MM)")
time_out = st.text_input("Time Out")

client = st.text_input("Client")
work = st.selectbox("Work Type", ["Audit", "GST", "IT", "Other"])
desc = st.text_area("Description")

if st.button("Save"):
    hours = calc_hours(time_in, time_out)
    status = "Working" if time_out == "" else "Completed"

    new_row = pd.DataFrame([{
        "Date": str(date),
        "Name": name,
        "Role": role,
        "Time In": time_in,
        "Time Out": time_out,
        "Client": client,
        "Work Type": work,
        "Description": desc,
        "Hours": hours,
        "Status": status
    }])

    st.session_state.data = pd.concat([df, new_row], ignore_index=True)
    st.success("Saved!")

# -----------------------------
# Display
# -----------------------------
st.subheader("📊 Data (Temporary)")
st.dataframe(st.session_state.data, use_container_width=True)
