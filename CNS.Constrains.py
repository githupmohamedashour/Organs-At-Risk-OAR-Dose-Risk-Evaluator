# OAR Dose Risk Evaluator - Advanced Streamlit Version
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set up page
st.set_page_config(page_title="OAR Risk Evaluator (Advanced)", layout="wide")
st.title("🧠 Organs At Risk (OAR) Dose Risk Evaluator")
st.markdown("""
This advanced tool estimates the radiation risk to critical OARs based on entered dose parameters. 
Dose constraints are based on clinical guidelines and literature data (e.g., QUANTEC).
""")

# Dose constraints data
OAR_CONSTRAINTS = {
    "spinal_cord": {
        "max_dose": 50,
        "notes": ">50 Gy → increased risk of myelopathy"
    },
    "brainstem": {
        "max_dose": 54,
        "max_dose_10cc": 59,
        "notes": "1–10 cc ≤59 Gy → minimal risk"
    },
    "optic_nerve": {
        "max_dose": 55,
        "caution_dose": 60,
        "notes": "55–60 Gy → 3–7% risk; >60 Gy → 7–20% risk of RION"
    },
    "retina": {
        "max_dose": 45,
        "threshold": 30,
        "notes": "30–50 Gy → risk increases; >50 Gy → ~5% retinopathy risk"
    },
    "hippocampus": {
        "mean_dose_40pct": 7.3,
        "notes": ">7.3 Gy to 40% → potential memory decline"
    },
    "temporal_lobe": {
        "d2cc": 74,
        "notes": ">70 Gy → risk of TLI; D2cc >74 Gy → high risk"
    }
}

# Function for evaluation
def evaluate_oar(oar_name, dose, volume=None, dose_type="max"):
    oar = OAR_CONSTRAINTS.get(oar_name)
    if not oar:
        return "Unknown OAR", "No data"

    risk = "Undetermined"

    if oar_name == "brainstem" and volume and volume <= 10:
        if dose <= oar["max_dose_10cc"]:
            risk = "Low risk (<5%)"
        else:
            risk = "High risk (>10%)"

    elif oar_name == "optic_nerve":
        if dose <= oar["max_dose"]:
            risk = "Minimal risk"
        elif dose <= oar["caution_dose"]:
            risk = "Moderate risk (3–7%)"
        else:
            risk = "High risk (>10%)"

    elif oar_name == "retina":
        if dose <= oar["threshold"]:
            risk = "Negligible risk"
        elif dose <= oar["max_dose"]:
            risk = "Low risk (<5%)"
        else:
            risk = "Moderate to high risk (>5%)"

    elif oar_name == "hippocampus":
        if dose <= oar["mean_dose_40pct"]:
            risk = "Low risk of memory impairment"
        else:
            risk = "Potential memory decline"

    elif oar_name == "temporal_lobe":
        if dose <= oar["d2cc"]:
            risk = "Acceptable exposure"
        else:
            risk = "Increased risk of TLI"

    elif dose <= oar.get("max_dose", 100):
        risk = "Within safe limit"
    else:
        risk = "Exceeds safe limit"

    notes = oar.get("notes", "No notes available")
    return risk, notes

# Sidebar inputs
st.sidebar.header("Input Parameters")
oar_selected = st.sidebar.selectbox("Select OAR:", list(OAR_CONSTRAINTS.keys()))
dose_input = st.sidebar.slider("Dose (Gy):", 0.0, 80.0, 50.0)
volume_input = st.sidebar.number_input("Volume (cc, optional):", min_value=0.0, step=0.1, format="%.1f")
dose_type_input = st.sidebar.selectbox("Dose Type:", ["max", "mean", "d2cc"])

# Evaluation
risk_level, clinical_notes = evaluate_oar(oar_selected, dose_input, volume_input, dose_type_input)

st.subheader(f"📋 Evaluation Result for: {oar_selected.replace('_', ' ').title()}")
st.write(f"**Dose Entered**: {dose_input} Gy ({dose_type_input})")
if volume_input > 0:
    st.write(f"**Volume**: {volume_input} cc")
st.markdown(f"**🧠 Risk Assessment**: :red[{risk_level}]")
st.markdown(f"**📚 Clinical Notes**: {clinical_notes}")

# Generate illustrative DVH-like plot
# st.subheader("📈 Dose Volume Histogram (Illustrative Simulation)")
# dvh_volumes = np.linspace(0, 100, 100)
# dvh_doses = np.maximum(0, dose_input - dvh_volumes / 2)

# fig, ax = plt.subplots()
# sns.lineplot(x=dvh_doses, y=dvh_volumes, ax=ax)
# ax.invert_yaxis()
# ax.set_xlabel("Dose (Gy)")
# ax.set_ylabel("Volume (%)")
# ax.set_title(f"Simulated DVH for {oar_selected.replace('_', ' ').title()}")
# st.pyplot(fig)

# DataTable of constraints
st.subheader("📑 Dose Constraint Summary")
data_for_df = []
for oar, info in OAR_CONSTRAINTS.items():
    max_dose = info.get("max_dose", info.get("d2cc", info.get("mean_dose_40pct", "N/A")))
    data_for_df.append([oar.replace('_', ' ').title(), max_dose, info.get("notes", "")])

df_constraints = pd.DataFrame(data_for_df, columns=["OAR", "Dose Constraint (Gy)", "Notes"])
st.dataframe(df_constraints, use_container_width=True)

# Optional future enhancements
st.markdown("---")
st.markdown("📌 *Future version will support DICOM RTSTRUCT import and patient-specific DVH analysis.*")
