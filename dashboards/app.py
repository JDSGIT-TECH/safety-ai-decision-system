import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout = "wide")
st.title("🛡️ Safety-Critical Anomaly Detection Dashboard")

df= pd.read_csv('data/processed/telemetry_with_ensemble.csv')

st.sidebar.header("Model Selection")
model_option = st.sidebar.selectbox(
    "Choose Anomaly Signal",
    [
        "iso_anomaly",
        "lof_anomaly",
        "svm_anomaly",
        "ensemble_or",
        "ensemble_vote",
        "ensemble_tiered"
    ]
    )

# Summary Statistics
st.subheader("📊 Anomaly Summary Statistics")
st.write(df[model_option].value_counts())

#Scatter Plot
st.subheader("🔍 Anomaly Scatter Plot (Temperature vs Vibration)")
fig, ax = plt.subplots(figsize=(7,5))
sns.scatterplot(
    x=df["temperature"],
    y=df["vibration"],
    hue=df[model_option],
    palette={0:"blue", 1:"red"},
    alpha=0.6,
    ax=ax
)
ax.set_title(f"Anomaly Detection using {model_option}")
st.pyplot(fig)

# Time Series Plot
st.subheader("⏱️ Anomlies over time (Temperature)")

fig2, ax2 = plt.subplots(figsize=(12,4))
ax2.plot(df["timestamp"], df["temperature"], label="Temperature", alpha=0.5)
ax2.scatter(
    df.loc[df[model_option]==1, "timestamp"],
    df.loc[df[model_option]==1, "temperature"],
    color='red',
    s=10,
    label="Anomaly"
)
ax2.legend()
st.pyplot(fig2)

#Recommendation Panel
st.subheader("✅ System Recommendation")

if df[model_option].sum() > 200:
    st.error("⚠️ High anomaly rate — enter SAFE-DEGRADED MODE")
elif df[model_option].sum() > 50:
    st.warning("⚠️ Moderate anomalies — monitor closely")
else:
    st.success("✅ SSystem behavior within acceptable range")
    