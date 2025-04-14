import streamlit as st
import requests
import pandas as pd
import altair as alt


API_URL = "http://localhost:8000"

st.title("Market Returns Based on Economic Conditions")

# --- SESSION STATE SETUP ---
if "sliders_submitted" not in st.session_state:
    st.session_state.sliders_submitted = False

if "matching_dates" not in st.session_state:
    st.session_state.matching_dates = []

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# --- SLIDERS ---
with st.form("filters_form"):
    inflation = st.slider("Inflation", 0.0, 20.0, (2.0, 4.0))
    unemp = st.slider("Unemployment", 0.0, 15.0, (3.0, 6.0))
    brent = st.slider("Brent Crude", 0.0, 150.0, (50.0, 100.0))
    rate = st.slider("Interest Rate", 0.0, 20.0, (1.0, 5.0))
    coffee = st.slider("Coffee Prices Global Mild Arabica (cents per pound)", 0.0, 500.0, (80.0, 200.0))
    submitted = st.form_submit_button("Find Matching Dates")

if submitted:
    st.session_state.sliders_submitted = True
    params = {
        "inflation_min": inflation[0], "inflation_max": inflation[1],
        "unemp_min": unemp[0], "unemp_max": unemp[1],
        "brent_min": brent[0], "brent_max": brent[1],
        "rate_min": rate[0], "rate_max": rate[1],
        "coffee_min": coffee[0], "coffee_max": coffee[1],
    }

    try:
        res = requests.get(f"{API_URL}/dates", params=params)
        res.raise_for_status()
        dates = res.json().get("dates", [])
        st.session_state.matching_dates = dates
        st.session_state.selected_date = None  # Reset selection
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching dates: {e}")
        st.stop()

# --- DATE DROPDOWN ---
if st.session_state.sliders_submitted and st.session_state.matching_dates:
    selected = st.selectbox("Choose a matching start date", st.session_state.matching_dates)

    if selected != st.session_state.selected_date:
        st.session_state.selected_date = selected

# --- BAR CHART ---
if st.session_state.selected_date:
    try:
        returns_res = requests.get(f"{API_URL}/returns", params={"start_date": st.session_state.selected_date})
        returns_res.raise_for_status()
        data = pd.DataFrame(returns_res.json().get("returns", []))

        if not data.empty:
            # Rename columns for better display
            data = data.rename(columns={"return_3y": "3 Year", "return_5y": "5 Year"})
            st.write(f"% Returns From {st.session_state.selected_date}:")
            st.bar_chart(data.set_index("index")[["3 Year", "5 Year"]],stack=False)

            # --- INDEX DROPDOWN + LINE CHART ---
            selected_index = st.selectbox("Select an index to view performance trend", data["index"].unique())

            if selected_index:
                monthly_res = requests.get(f"{API_URL}/monthly_returns", params={"start_date": st.session_state.selected_date})
                monthly_res.raise_for_status()
                monthly_data = pd.DataFrame(monthly_res.json().get("monthly_returns", []))

                filtered = monthly_data[monthly_data["index"] == selected_index]

                if not filtered.empty:
                    filtered["performance_date"] = pd.to_datetime(filtered["performance_date"])
                    filtered = filtered.sort_values("performance_date")
                    # Build the Altair chart with tooltips
                    line_chart = alt.Chart(filtered).mark_line(point=True).encode(
                        x=alt.X("performance_date:T", title="Date"),
                        y=alt.Y("close_value:Q", title="Close Value"),
                        tooltip=[
                            alt.Tooltip("performance_date:T", title="Date"),
                            alt.Tooltip("close_value:Q", title="Close Value"),
                            alt.Tooltip("index:N", title="Index")
                        ]
                    ).properties(
                        width=700,
                        height=400,
                        title=f"Monthly Performance for {selected_index}"
                    ).interactive()

                    st.altair_chart(line_chart, use_container_width=True)
                else:
                    st.write("No monthly performance data available for the selected index.")

        else:
            st.write("No returns data available for that date.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching returns data: {e}")
