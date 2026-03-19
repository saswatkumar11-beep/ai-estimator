import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AI Effort Estimator", layout="centered")

st.title("🤖 AI Effort Estimation Agent")

# -------------------------------
# Helper Functions
# -------------------------------

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else None

def detect_level(text):
    text = text.lower()
    if any(word in text for word in ["high", "critical", "complex"]):
        return "high"
    elif "medium" in text:
        return "medium"
    elif any(word in text for word in ["low", "simple"]):
        return "low"
    return None

# -------------------------------
# Estimation Logic (Enhanced)
# -------------------------------

def estimate_effort(config_files, macros, complexity, criticality):
    
    # -------------------------------
    # Base Effort
    # -------------------------------
    base_dev = config_files * 4
    base_test = macros * 2

    # -------------------------------
    # Multipliers
    # -------------------------------
    complexity_factor = {"low": 0.8, "medium": 1.0, "high": 1.5}
    criticality_factor = {"low": 1.0, "medium": 1.2, "high": 1.5}

    # -------------------------------
    # Development Effort
    # -------------------------------
    dev = base_dev * complexity_factor[complexity] * criticality_factor[criticality]

    # -------------------------------
    # Testing Effort (Enhanced)
    # -------------------------------
    testing_multiplier = 1.3  # accounts for extended testing effort
    test = base_test * complexity_factor[complexity] * criticality_factor[criticality] * testing_multiplier

    # -------------------------------
    # Analysis Effort (Enhanced)
    # MSP + CDS + DCR + Walkthrough
    # -------------------------------
    analysis_factor = 0.30
    presentation_overhead = 2  # hours for panel walkthrough

    analysis = (analysis_factor * dev) + presentation_overhead

    # -------------------------------
    # Documentation
    # -------------------------------
    documentation = 0.10 * dev

    # -------------------------------
    # Buffer / Risk
    # -------------------------------
    buffer = 0.15 * (dev + test)

    # -------------------------------
    # Total Effort
    # -------------------------------
    total = dev + test + analysis + documentation + buffer

    # -------------------------------
    # Output Table
    # -------------------------------
    df = pd.DataFrame({
        "Level": ["L0", "L1", "L2", "L3", "L4", "L5", "Total"],
        "Activity": [
            "MSP/CDS/DCR Analysis + Walkthrough",
            "Customer Requirements",
            "Development",
            "Testing (Extended)",
            "Documentation",
            "Buffer",
            "Total Effort"
        ],
        "Effort (hrs)": [
            round(analysis, 2),
            round(analysis, 2),
            round(dev, 2),
            round(test, 2),
            round(documentation, 2),
            round(buffer, 2),
            round(total, 2)
        ]
    })

    return df, total

# -------------------------------
# Session State
# -------------------------------

if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.config = None
    st.session_state.macros = None
    st.session_state.complexity = None
    st.session_state.criticality = None

# -------------------------------
# Chat UI
# -------------------------------

user_input = st.text_input("💬 Your response:")

if st.session_state.step == 1:
    st.write("👉 How many configuration files need changes?")
elif st.session_state.step == 2:
    st.write("👉 How many macros need testing?")
elif st.session_state.step == 3:
    st.write("👉 What is the complexity? (Low / Medium / High)")
elif st.session_state.step == 4:
    st.write("👉 What is the criticality? (Low / Medium / High)")

if st.button("Submit") and user_input:

    if st.session_state.step == 1:
        num = extract_number(user_input)
        if num:
            st.session_state.config = num
            st.session_state.step = 2
        else:
            st.warning("Please enter a valid number.")

    elif st.session_state.step == 2:
        num = extract_number(user_input)
        if num:
            st.session_state.macros = num
            st.session_state.step = 3
        else:
            st.warning("Please enter a valid number.")

    elif st.session_state.step == 3:
        comp = detect_level(user_input)
        if comp:
            st.session_state.complexity = comp
            st.session_state.step = 4
        else:
            st.warning("Please enter Low, Medium, or High.")

    elif st.session_state.step == 4:
        crit = detect_level(user_input)
        if crit:
            st.session_state.criticality = crit

            df, total = estimate_effort(
                st.session_state.config,
                st.session_state.macros,
                st.session_state.complexity,
                st.session_state.criticality
            )

            st.success("✅ Estimation Complete!")

            st.write(f"### ⏱️ Total Effort: {round(total,2)} hours")

            st.write("### 📊 Effort Breakdown")
            st.dataframe(df)

            file = "estimation.xlsx"
            df.to_excel(file, index=False)

            with open(file, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="estimation.xlsx")

        else:
            st.warning("Please enter Low, Medium, or High.")

# -------------------------------
# Reset Button
# -------------------------------

if st.button("🔄 Start Over"):
    st.session_state.step = 1
    st.session_state.config = None
    st.session_state.macros = None
    st.session_state.complexity = None
    st.session_state.criticality = None