import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supplier Comparison", layout="wide")

st.title("Supplier Comparison Calculator")

# -----------------------------
# GLOBAL INPUTS
# -----------------------------

st.header("Production Settings")

target_q1 = st.number_input(
    "Target Q1 Production (m³)",
    min_value=1.0,
    value=600.0
)

line_cost_hour = st.number_input(
    "Line Cost per Hour (€)",
    min_value=0.0,
    value=52.5
)

thickness = st.number_input(
    "Thickness (mm)",
    min_value=1.0,
    value=19.0
)

width = st.number_input(
    "Width (mm)",
    min_value=1.0,
    value=75.0
)

saws = st.number_input(
    "Number of Saws",
    min_value=1,
    value=2
)

# -----------------------------
# SUPPLIER INPUTS
# -----------------------------

col1, col2 = st.columns(2)


def supplier_form(col, name):

    with col:

        st.subheader(name)

        price = st.number_input(
            f"{name} Price €/m³",
            value=235.0,
            key=f"{name}_price"
        )

        speed = st.number_input(
            f"{name} Speed (m/min)",
            value=0.0,
            key=f"{name}_speed"
        )

        q1 = st.number_input(
            f"{name} Q1 %",
            value=0.0,
            key=f"{name}_q1"
        )

        q1s = st.number_input(
            f"{name} Q1 Short %",
            value=0.0,
            key=f"{name}_q1s"
        )

        q2 = st.number_input(
            f"{name} Q2 %",
            value=0.0,
            key=f"{name}_q2"
        )

        q3 = st.number_input(
            f"{name} Q3 %",
            value=0.0,
            key=f"{name}_q3"
        )

        q4 = st.number_input(
            f"{name} Q4 %",
            value=0.0,
            key=f"{name}_q4"
        )

        q5 = st.number_input(
            f"{name} Q5 %",
            value=0.0,
            key=f"{name}_q5"
        )

        total = q1 + q1s + q2 + q3 + q4 + q5
        waste = max(0, 100 - total)

        st.metric("Calculated Waste %", f"{waste:.2f}")

        return {
            "price": price,
            "speed": speed,
            "q1": q1,
            "q1s": q1s,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5,
            "waste": waste
        }


supplier_a = supplier_form(col1, "Supplier A")
supplier_b = supplier_form(col2, "Supplier B")


# -----------------------------
# CALCULATIONS
# -----------------------------

def calculate(data):

    if data["q1"] <= 0:
        return None

    input_needed = target_q1 / (data["q1"] / 100)

    q1_volume = input_needed * data["q1"] / 100
    q1s_volume = input_needed * data["q1s"] / 100
    q2_volume = input_needed * data["q2"] / 100

    q3_volume = (
        input_needed
        * data["q3"] / 100
        * (61 / 75)
    )

    q4_volume = (
        input_needed
        * data["q4"] / 100
        * (50 / 75)
    )

    q5_volume = input_needed * data["q5"] / 100

    total_sellable = (
        q1_volume
        + q1s_volume
        + q2_volume
        + q3_volume
        + q4_volume
        + q5_volume
    )

    true_waste = input_needed - total_sellable

    cross_section = (
        (thickness / 1000)
        * (width / 1000)
    )

    input_m3_hour = (
        data["speed"]
        * saws
        * 60
        * cross_section
    )

    if input_m3_hour > 0:
        hours_needed = input_
