import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supplier Comparison", layout="wide")

st.title("Automatic Line Supplier Comparison")

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
    value=19.0
)

width = st.number_input(
    "Width (mm)",
    value=75.0
)

saws = st.number_input(
    "Number of Saws",
    min_value=1,
    value=2
)

# =====================================================

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

        waste = max(0.0, 100 - total)

        st.metric(
            "Calculated Waste %",
            f"{waste:.2f}%"
        )

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

# =====================================================

def calculate(data):

    q1_fraction = data["q1"] / 100

    if q1_fraction == 0:
        return None

    # Input volume needed
    input_needed = target_q1 / q1_fraction

    # Volumes produced from that input
    q1_volume = input_needed * data["q1"] / 100
    q1s_volume = input_needed * data["q1s"] / 100
    q2["q1s_volume = input_needed * data[ / 100

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

    # Throughput

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

    if input_m3_hour == 0:
        hours_needed = 0
    else:
        hours_needed = input_needed / input_m3_hour

    labour_cost = hours_needed * line_cost_hour

    material_cost = input_needed * data["price"]

    total_cost = labour_cost + material_cost

    return {
        "Input Needed m³": round(input_needed, 1),
        "Q1 Produced": round(q1_volume, 1),
        "Q1 Short": round(q1s_volume, 1),
        "Q2": round(q2_volume, 1),
        "Q3 (61mm)": round(q3_volume, 1),
        "Q4 (50mm)": round(q4_volume, 1),
        "Q5": round(q5_volume, 1),
        "True Waste m³": round(true_waste, 1),
        "Hours Needed": round(hours_needed, 1),
        "Labour Cost €": round(labour_cost, 0),
        "Material Cost €": round(material_cost, 0),
        "Total Cost €": round(total_cost, 0)
    }

result_a = calculate(supplier_a)
result_b = calculate(supplier_b)

if result_a and result_b:

    st.header("Results")

    results = pd.DataFrame({
        "Supplier A": result_a,
        "Supplier B": result_b
    })

    st.dataframe(results, use_container_width=True)

    st.header("Difference")

    extra_hours = (
        result_b["Hours Needed"]
        - result_a["Hours Needed"]
    )

    extra_labour = (
        result_b["Labour Cost €"]
        - result_a["Labour Cost €"]
    )

    extra_material = (
        result_b["Material Cost €"]
        - result_a["Material Cost €"]
    )

    extra_total = (
        result_b["Total Cost €"]
        - result_a["Total Cost €"]
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Extra Hours (B vs A)",
        f"{extra_hours:.1f}"
    )

    c2.metric(
        "Extra Total Cost €",
        f"{extra_total:,.0f}"
    )

    st.write("### Cost Breakdown Difference")

    st.write(
        f"Extra labour cost: €{extra_labour:,.0f}"
    )

    st.write(
        f"Extra material cost: €{extra_material:,.0f}"
    )

    chart = pd.DataFrame(
        {
            "Hours": [
                result_a["Hours Needed"],
                result_b["Hours Needed"]
            ]
        },
        index=["Supplier A", "Supplier B"]
    )

    st.bar_chart(chart)
