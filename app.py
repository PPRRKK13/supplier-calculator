import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Supplier Comparison Calculator",
    layout="wide"
)

st.title("Supplier Quality & Profitability Calculator")

# =====================================================
# GLOBAL SETTINGS
# =====================================================

st.sidebar.header("Production")

thickness = st.sidebar.number_input(
    "Thickness (mm)",
    min_value=0.0,
    value=19.0
)

width = st.sidebar.number_input(
    "Input Width (mm)",
    min_value=0.0,
    value=75.0
)

saws = st.sidebar.number_input(
    "Number of Saws",
    min_value=1,
    value=2
)

shifts = st.sidebar.number_input(
    "Number of Shifts",
    min_value=1,
    value=2
)

hours_per_shift = st.sidebar.number_input(
    "Hours per Shift per Month",
    min_value=1,
    value=160
)

# =====================================================
# LABOUR
# =====================================================

st.sidebar.header("Labour Costs")

operators = st.sidebar.number_input(
    "Operators",
    min_value=0,
    value=3
)

operator_salary = st.sidebar.number_input(
    "Operator Salary €/month",
    min_value=0.0,
    value=1800.0
)

forklift_drivers = st.sidebar.number_input(
    "Forklift Drivers",
    min_value=0,
    value=1
)

forklift_salary = st.sidebar.number_input(
    "Forklift Driver Salary €/month",
    min_value=0.0,
    value=1500.0
)

workers = st.sidebar.number_input(
    "Additional Workers",
    min_value=0,
    value=1
)

worker_salary = st.sidebar.number_input(
    "Worker Salary €/month",
    min_value=0.0,
    value=1500.0
)

# =====================================================
# MACHINE COSTS
# =====================================================

st.sidebar.header("Machine Costs €/month")

electricity = st.sidebar.number_input(
    "Electricity",
    min_value=0.0,
    value=0.0
)

maintenance = st.sidebar.number_input(
    "Maintenance",
    min_value=0.0,
    value=0.0
)

blades = st.sidebar.number_input(
    "Saw Blades",
    min_value=0.0,
    value=0.0
)

other_costs = st.sidebar.number_input(
    "Other Costs",
    min_value=0.0,
    value=0.0
)

# =====================================================
# SELLING PRICES
# =====================================================

st.header("Selling Prices (€/m³)")

p1, p2, p3 = st.columns(3)

with p1:
    q1_price = st.number_input("Q1 Price", value=0.0)
    q1s_price = st.number_input("Q1 Short Price", value=0.0)

with p2:
    q2_price = st.number_input("Q2 Price", value=0.0)
    q3_price = st.number_input("Q3 Price", value=0.0)

with p3:
    q4_price = st.number_input("Q4 Price", value=0.0)
    q5_price = st.number_input("Q5 Price", value=0.0)

PRICE_MAP = {
    "Q1": q1_price,
    "Q1S": q1s_price,
    "Q2": q2_price,
    "Q3": q3_price,
    "Q4": q4_price,
    "Q5": q5_price
}

# Q3 = 61 mm
# Q4 = 50 mm

WIDTH_FACTOR = {
    "Q1": 1.0,
    "Q1S": 1.0,
    "Q2": 1.0,
    "Q3": 61 / 75,
    "Q4": 50 / 75,
    "Q5": 1.0
}

# =====================================================
# SUPPLIER INPUT
# =====================================================

left, right = st.columns(2)

def supplier_input(container, supplier_name):

    with container:

        st.subheader(supplier_name)

        purchase_price = st.number_input(
            f"{supplier_name} Purchase Price €/m³",
            min_value=0.0,
            value=0.0,
            key=f"{supplier_name}_price"
        )

        speed = st.number_input(
            f"{supplier_name} Speed (m/min)",
            min_value=0.0,
            value=0.0,
            key=f"{supplier_name}_speed"
        )

        downtime = st.number_input(
            f"{supplier_name} Downtime %",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            key=f"{supplier_name}_downtime"
        )

        q1 = st.number_input(
            f"{supplier_name} Q1 %",
            value=0.0,
            key=f"{supplier_name}_q1"
        )

        q1s = st.number_input(
            f"{supplier_name} Q1 Short %",
            value=0.0,
            key=f"{supplier_name}_q1s"
        )

        q2 = st.number_input(
            f"{supplier_name} Q2 %",
            value=0.0,
            key=f"{supplier_name}_q2"
        )

        q3 = st.number_input(
            f"{supplier_name} Q3 %",
            value=0.0,
            key=f"{supplier_name}_q3"
        )

        q4 = st.number_input(
            f"{supplier_name} Q4 %",
            value=0.0,
            key=f"{supplier_name}_q4"
        )

        q5 = st.number_input(
            f"{supplier_name} Q5 %",
            value=0.0,
            key=f"{supplier_name}_q5"
        )

        total_quality = q1 + q1s + q2 + q3 + q4 + q5

        waste = max(0, 100 - total_quality)

        st.metric(
            "Calculated Waste %",
            f"{waste:.2f}"
        )

        if total_quality > 100:
            st.error("Quality percentages exceed 100%")

        return {
            "purchase": purchase_price,
            "speed": speed,
            "downtime": downtime,
            "quality": {
                "Q1": q1,
                "Q1S": q1s,
                "Q2": q2,
                "Q3": q3,
                "Q4": q4,
                "Q5": q5
            },
            "waste": waste
        }

supplier_a = supplier_input(left, "Supplier A")
supplier_b = supplier_input(right, "Supplier B")

# =====================================================
# COSTS
# =====================================================

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
    + other_costs
) / production_hours

# =====================================================
# CALC ENGINE
# =====================================================

def calculate(data):

    speed = data["speed"]
    purchase = data["purchase"]
    downtime = data["downtime"]
    quality = data["quality"]

    effective_speed = speed * (1 - downtime / 100)

    lm_hour = effective_speed * saws * 60

    input_m3_hour = (
        (thickness / 1000)
        * (width / 1000)
        * lm_hour
    )

    revenue_per_m3 = 0
    recovered_volume = 0

    for q in quality:

        share = quality[q] / 100

        factor = WIDTH_FACTOR[q]

        recovered_volume += share * factor

        revenue_per_m3 += (
            share
            * factor
            * PRICE_MAP[q]
        )

    revenue_hour = revenue_per_m3 * input_m3_hour

    material_hour = purchase * input_m3_hour

    profit_hour = (
        revenue_hour
        - material_hour
        - labour_hour
        - machine_hour
    )

    annual_profit = profit_hour * production_hours * 12

    return {
        "Input m³/h": round(input_m3_hour, 2),
        "Recovered %": round(recovered_volume * 100, 2),
        "Revenue €/m³": round(revenue_per_m3, 2),
        "Revenue €/h": round(revenue_hour, 2),
        "Profit €/h": round(profit_hour, 2),
        "Annual Profit €": round(annual_profit, 2)
    }

result_a = calculate(supplier_a)
result_b = calculate(supplier_b)

# =====================================================
# RESULTS
# =====================================================

st.header("Results")

results = pd.DataFrame(
    {
        "Supplier A": result_a,
        "Supplier B": result_b
    }
)

st.dataframe(results, use_container_width=True)

# =====================================================
# PROFIT DIFFERENCE
# =====================================================

st.header("Comparison")

profit_difference = (
    result_a["Profit €/h"]
    - result_b["Profit €/h"]
)

annual_difference = (
    result_a["Annual Profit €"]
    - result_b["Annual Profit €"]
)

c1, c2 = st.columns(2)

c1.metric(
    "Profit Difference €/hour",
    f"{profit_difference:,.2f}"
)

c2.metric(
    "Annual Difference €",
    f"{annual_difference:,.0f}"
)

# =====================================================
# CHART
# =====================================================

chart_df = pd.DataFrame(
    {
        "Profit €/h": [
            result_a["Profit €/h"],
            result_b["Profit €/h"]
        ]
    },
    index=["Supplier A", "Supplier B"]
)

st.bar_chart(chart_df)
