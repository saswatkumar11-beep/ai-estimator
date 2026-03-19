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

def detect_complexity(text):
    text = text.lower()
    if any(word in text for word in ["high", "critical", "complex"]):
        return "high"
    elif "medium" in text:
        return "medium"
    elif any(word in text for word in ["low", "simple"]):
        return "low"
    return None

def estimate_effort(config_files, macros, complexity):
    config_effort = {"low": 2, "medium": 4, "high": 8}
    macro_effort = {"low": 1, "medium": 2, "high": 3}
    buffer_factor = {"low": 0.10, "medium": 0.15, "high": 0.20}

    dev = config_files * config_effort[complexity]
    test = macros * macro_effort[complexity]
    analysis = 0.15 * dev
    documentation = 0.10 * dev
    buffer = buffer_factor[complexity] * (dev + test)

    total = dev + test + analysis + documentation + buffer

    df = pd.DataFrame({
        "Level": ["L0", "L1", "L2", "L3", "L4", "L5", "Total"],
        "Activity": [
            "MSP Analysis",
            "Customer Requirements",
            "Development",
            "Testing",
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

if st.button("Submit") and user_input:

    if st.session_state.step == 1:
        num = extract_number(user_input)
        if num:
            st.session_state.config = num
            st.session_state.step = 2
        else:
            st.warning("Please enter a number.")

    elif st.session_state.step == 2:
        num = extract_number(user_input)
        if num:
            st.session_state.macros = num
            st.session_state.step = 3
        else:
            st.warning("Please enter a number.")

    elif st.session_state.step == 3:
        comp = detect_complexity(user_input)
        if comp:
            st.session_state.complexity = comp

            df, total = estimate_effort(
                st.session_state.config,
                st.session_state.macros,
                st.session_state.complexity
            )

            st.success("✅ Estimation Complete!")

            st.write(f"**Total Effort:** {total} hours")
            st.dataframe(df)

            file = "estimation.xlsx"
            df.to_excel(file, index=False)

            with open(file, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="estimation.xlsx")

        else:
            st.warning("Please enter Low, Medium, or High.")

# Reset button
if st.button("🔄 Start Over"):
    st.session_state.step = 1
    st.session_state.config = None
    st.session_state.macros = None
    st.session_state.complexity = None