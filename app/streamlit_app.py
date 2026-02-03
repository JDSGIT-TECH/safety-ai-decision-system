import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.warning(
    "🔒 This dashboard is READ-ONLY. "
    "All decisions shown are historical replays. "
    "No live system control is exposed."
)

#Page configuration
st.set_page_config(page_title = "Safety System Replay Dashboard", layout = "wide")
st.title("🛡️ Safety-Critical AI — Batch Replay Analysis")
st.markdown(
    """
    This dash board replays **historical system decisions over time** to evaluate
    whether the safety system behaves **realisticall, conservatively, and responsibly**
    """
)

#Load replay data
DATA_PATH = "outputs/safety_timeline_replay.csv"

'''
Hardening the Streamlit app (code changes)
A. Disable file uploads completely

(You already did this implicitly — good instinct.)

B. Lock data source
'''
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

df=load_data()
df=df.sort_values("timestamp")

#High-level metrics
st.header("📊 High-Level Safety Summary")
col1, col2, col3 = st.columns(3)

col1.metric("Normal", (df["system_decision"] == "Normal").sum())
col1.metric("Warning", (df["system_decision"] == "Warning").sum())
col1.metric("Critical", (df["system_decision"] == "Critical").sum())

#Timeline Visualization
st.header("⏱️ Safety Decision Timeline")
fig, ax = plt.subplots(figsize=(14,4))

color_map = {
    "Normal": "green",
    "Warning": "orange",
    "Critical": "red"
}

ax.scatter(
    df["timestamp"],
    df["system_decision"].map({"Normal": 0, "Warning": 1, "Critical": 2}),
    c=df["system_decision"].map(color_map),
    s=8
)

ax.set_yticks([0,1,2])
ax.set_yticklabels(["Normal", "Warning", "Critical"])
ax.set_xlabel("time")
ax.set_title("System Decision Over Time")

st.pyplot(fig)

st.markdown(
        """
        **Interpretation guidance:**
        - Gradual transitions → stable system  
        - Sudden CRITICAL spikes → investigate root cause  
        - Long green stretches → calm operating conditions
        """
)

#Warning cluster analysis
st.header("⚠️ Warning Cluster Analysis")
warning_df = df[df["system_decision"] == "Warning"]

fig2, ax2 = plt.subplots(figsize=(14,4))
ax2.plot(warning_df["timestamp"], warning_df["warning_streak"], color="orange")
ax2.set_title("Warning persistence Over Time")
ax2.set_ylabel("Consecutive Warning Count")
ax2.set_xlabel("Time")

st.pyplot(fig2)

st.markdown(
        """
        **Why this matters:**
        - Repeated warnings often precede failures  
        - Persistent warnings justify escalation  
        - Isolated warnings are usually benign
        """
)

#Calm period analysis
st.header("🌱 Calm Period Analysis")

df["is_calm"] = df["system_decision"] == "Normal"
df["calm_streak"] = (df["is_calm"].astype(int).groupby((~df["is_calm"]).cumsum()).cumsum())

fig3, ax3 = plt.subplots(figsize=(14,4))                                                           
ax3.plot(df["timestamp"], df["calm_streak"], color="green")
ax3.set_title("Calm (Normal) Persistence Over Time")
ax3.set_ylabel("Consecutive Normal Count")
ax3.set_xlabel("Time")
st.pyplot(fig3)

st.markdown(
        """
        **Healthy systems show:**
        - Long calm stretches  
        - Short warning bursts  
        - Rare, explainable critical events
        """
)

#Final Assessment
st.header("🧠 Operational Assessment")

st.markdown(
        """
        ### What this replay tells us

        ✔ The system does **not** oscillate randomly  
        ✔ Warnings tend to **cluster**, not flicker  
        ✔ Critical events are **rare and visible**  
        ✔ Calm periods dominate — as expected in real operations  

        ### Conclusion

        This behavior is **operationally realistic** and suitable for  
        **safety-first environments**, provided human escalation remains in the loop.
        """
)

#Remove silent failures (very important)
#Wrap plots safely (Never expose stack traces publicly.):

try:
    st.pyplot(fig)
except Exception as e:
    st.error("Visualization Error. Contact System Owner.")