import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Supplier Profit Calculator",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("Supplier Quality & Profitability Calculator")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Production")

thickness = st.sidebar.number_input(
    "Thickness (mm)",
    value=19.0
)

input_width = st.sidebar.number_input(
    "Input Width (mm)",
    value=75.0
)

saws = st.sidebar.number_input(
    "Number of Saws",
    value=2,
    step=1
)

shifts = st.sidebar.number_input(
    "Shifts",
    value=2,
    step=1
)

hours_per_shift = st.sidebar.number_input(
    "Hours per Shift per Month",
    value=160
)

# --------------------------------------------------
# LABOUR
# --------------------------------------------------

st.sidebar.header("Labour")

operators = st.sidebar.number_input(
    "Operators",
    value=3
)

operator_salary = st.sidebar.number_input(
    "Operator Salary €/month",
    value=1800
)

forklift_drivers = st.sidebar.number_input(
    "Forklift Drivers",
    value=1
)

forklift_salary = st.sidebar.number_input(
    "Forklift Salary €/month",
    value=1500
)

workers = st.sidebar.number_input(
    "Workers",
    value=1
)

worker_salary = st.sidebar.number_input(
    "Worker Salary €/month",
    value=1500
)

# --------------------------------------------------
# MACHINE COSTS
# --------------------------------------------------

st.sidebar.header("Monthly Machine Costs")

electricity = st.sidebar.number_input(
    "Electricity",
    value=0
)

maintenance = st.sidebar.number_input(
    "Maintenance",
    value=0
)

blades = st.sidebar.number_input(
    "Saw Blades",
    value=0
)

overhead = st.sidebar.number_input(
    "Other Costs",
    value=0
)

# --------------------------------------------------
# SELLING PRICES
# --------------------------------------------------

st.header("Selling Prices €/m³")

c1, c2, c3, c4 = st.columns(4)

with c1:
    q1_price = st.number_input("Q1", value=650.0)
    q1s_price = st.number_input("Q1 Short", value=500.0)

with c2:
    q2_price = st.number_input("Q2", value=400.0)
    q3_price = st.number_input("Q3", value=250.0)

with c3:
    q4_price = st.number_input("Q4", value=120.0)
    q5_price = st.number_input("Q5", value=700.0)

with c4:
    waste_price = st.number_input("Waste", value=0.0)

PRICE_MAP = {
    "Q1": q1_price,
    "Q1S": q1s_price,
    "Q2": q2_price,
    "Q3": q3_price,
    "Q4": q4_price,
    "Q5": q5_price,
    "WASTE": waste_price
}

# Q3 = 61 mm
# Q4 = 50 mm
WIDTH_FACTOR = {
    "Q1": 75 / 75,
    "Q1S": 75 / 75,
    "Q2": 75 / 75,
    "Q3": 61 / 75,
    "Q4": 50 / 75,
    "Q5": 75 / 75,
    "WASTE": 0
}

# --------------------------------------------------
# SUPPLIER INPUTS
# --------------------------------------------------

left, right = st.columns(2)

def supplier_form(container, supplier_name):

    with container:

        st.subheader(supplier_name)

        purchase_price = st.number_input(
            f"{supplier_name} Purchase Price €/m³",
            value=235.0,
            key=f"price_{supplier_name}"
        )

        speed = st.number_input(
            f"{supplier_name} Speed m/min",
            value=38.5 if supplier_name == "Supplier A" else 34.0,
            key=f"speed_{supplier_name}"
        )

        downtime = st.number_input(
            f"{supplier_name} Downtime %",
            value=5.0,
            key=f"downtime_{supplier_name}"
        )

        st.write("Quality Distribution %")

        q1 = st.number_input(
            f"{supplier_name} Q1 %",
            value=66.0 if supplier_name == "Supplier A" else 57.0,
            key=f"q1_{supplier_name}"
        )

        q1s = st.number_input(
            f"{supplier_name} Q1 Short %",
            value=8.0,
            key=f"q1s_{supplier_name}"
        )

        q2 = st.number_input(
            f"{supplier_name} Q2 %",
            value=10.0,
            key=f"q2_{supplier_name}"
        )

        q3 = st.number_input(
            f"{supplier_name} Q3 %",
            value=6.0,
            key=f"q3_{supplier_name}"
        )

        q4 = st.number_input(
            f"{supplier_name} Q4 %",
            value=4.0,
            key=f"q4_{supplier_name}"
        )

        q5 = st.number_input(
            f"{supplier_name} Q5 %",
            value=3.0,
            key=f"q5_{supplier_name}"
        )

        waste = st.number_input(
            f"{supplier_name} Waste %",
            value=3.0,
            key=f"waste_{supplier_name}"
        )

        mix = {
            "Q1": q1,
            "Q1S": q1s,
            "Q2": q2,
            "Q3": q3,
            "Q4": q4,
            "Q5": q5,
            "WASTE": waste
        }

        return {
            "purchase": purchase_price,
            "speed": speed,
            "downtime": downtime,
            "mix": mix
        }

supplier_a = supplier_form(left, "Supplier A")
supplier_b = supplier_form(right, "Supplier B")

# --------------------------------------------------
# COSTS
# --------------------------------------------------

production_hours = shifts * hours_per_shift

labour_month = (
    operators * operator_salary
    + forklift_drivers * forklift_salary
    + workers * worker_salary
) * shifts

labour_hour = labour_month / production_hours

machine_hour = (
    electricity
    + maintenance
    + blades
    + overhead
) / production_hours

# --------------------------------------------------
# CALCULATION
# --------------------------------------------------

def calculate_supplier(data):

    speed = data["speed"]
    downtime = data["downtime"]
    purchase = data["purchase"]
    mix = data["mix"]

    effective_speed = speed * (1 - downtime / 100)

    running_meters_hour = effective_speed * saws * 60

    input_m3_hour = (
        (thickness / 1000)
        * (input_width / 1000)
        * running_meters_hour
    )

    revenue_per_input_m3 = 0
    recovered_percent = 0

    for quality, pct in mix.items():

        share = pct / 100

        factor = WIDTH_FACTOR[quality]

        sellable_volume = share * factor

        recovered_percent += sellable_volume

        revenue_per_input_m3 += (
            sellable_volume
            * PRICE_MAP[quality]
        )

    
