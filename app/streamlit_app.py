import os
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
# Page configuration (MUST be first Streamlit call)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Safety-Critical AI Decision System",
    layout="wide"
)


# ------------------------------------------------------------------
# Global constants
# ------------------------------------------------------------------
DEMO_DATA_PATH = "outputs/demo_safety_timeline.csv"

REQUIRED_COLUMNS = {
    "timestamp",
    "system_decision",
    "warning_streak",
    "risk_level",
}

DECISION_MAP = {"Normal": 0, "Warning": 1, "Critical": 2}
COLOR_MAP = {"Normal": "green", "Warning": "orange", "Critical": "red"}


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
@st.cache_data
def load_csv(path_or_file):
    try:
        return pd.read_csv(path_or_file, parse_dates=["timestamp"])
    except Exception:
        st.error(
            "❌ Failed to parse CSV.\n\n"
            "Ensure the file is a valid CSV and the `timestamp` column "
            "is in a readable datetime format."
        )
        st.stop()


def validate_schema(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        st.error(
            "❌ Invalid CSV schema detected.\n\n"
            f"Missing required columns: **{', '.join(missing)}**"
        )
        st.info(
            "Please upload a CSV that matches the expected schema "
            "shown in the sidebar."
        )
        return False

    return True


def generate_demo_data():
    if not os.path.exists(DEMO_DATA_PATH):
        st.error("Demo dataset not found.")
        st.stop()
    return load_csv(DEMO_DATA_PATH)


def show_expected_schema_sidebar():
    st.markdown("#### 📘 Expected CSV Schema")
    st.markdown(
        """
        **Required columns**

        | Column | Description |
        |------|------------|
        | `timestamp` | Time of decision |
        | `system_decision` | Normal / Warning / Critical |
        | `warning_streak` | Consecutive warning count |
        | `risk_level` | LOW / MEDIUM / HIGH |

        📌 Decision-level outputs only  
        📌 No PII or raw sensor data
        """
    )


# ------------------------------------------------------------------
# Header & safety notice
# ------------------------------------------------------------------
st.warning(
    "🔒 This dashboard is READ-ONLY. "
    "All outputs are historical replays. "
    "No live system control is exposed."
)

st.title("🛡️ Safety-Critical AI Decision System")
st.caption("Stage-1 Safety Gate → Stage-2 Severity → Temporal Escalation")

st.markdown(
    """
    This dashboard demonstrates a **multi-stage safety inference pipeline**
    using **historical decision replays only**.

    **Supported input modes:**
    - 🟢 Built-in demo data
    - 📤 Timeline CSV (system-wide evolution)
    - ▶️ Replay CSV (single-run analysis)

    No uploads are required to explore the demo.
    """
)


# ------------------------------------------------------------------
# Input mode selection
# ------------------------------------------------------------------
st.sidebar.header("📂 Data Source")

mode = st.sidebar.radio(
    "Select input type",
    ["Demo data", "Timeline CSV", "Replay CSV"]
)

df = None
data_source = None


# ------------------------------------------------------------------
# Data loading logic (single source of truth)
# ------------------------------------------------------------------
if mode == "Demo data":
    data_source = "demo"
    df = generate_demo_data()

elif mode == "Timeline CSV":
    data_source = "timeline"
    timeline_file = st.sidebar.file_uploader(
        "Upload safety timeline CSV", type=["csv"]
    )
    show_expected_schema_sidebar()
    if timeline_file:
        df = load_csv(timeline_file)

elif mode == "Replay CSV":
    data_source = "replay"
    replay_file = st.sidebar.file_uploader(
        "Upload safety replay CSV", type=["csv"]
    )
    show_expected_schema_sidebar()
    if replay_file:
        df = load_csv(replay_file)


# ------------------------------------------------------------------
# Guardrails
# ------------------------------------------------------------------
if df is None:
    st.info("Please select a data source to continue.")
    st.stop()

if not validate_schema(df):
    st.stop()

df = df.sort_values("timestamp")

st.caption(f"Data source: **{data_source}** | Rows: **{len(df)}**")


# ------------------------------------------------------------------
# Expected schema (documentation)
# ------------------------------------------------------------------
with st.expander("📘 Expected CSV Schema"):
    st.markdown(
        """
        **Required columns**

        | Column | Description |
        |------|------------|
        | `timestamp` | Time of decision |
        | `system_decision` | Normal / Warning / Critical |
        | `warning_streak` | Consecutive warning count |
        | `risk_level` | LOW / MEDIUM / HIGH |

        📌 Decision-level outputs only  
        📌 No raw sensor or PII data
        """
    )


# ------------------------------------------------------------------
# High-level metrics
# ------------------------------------------------------------------
st.header("📊 High-Level Safety Summary")
col1, col2, col3 = st.columns(3)

col1.metric("Normal", (df["system_decision"] == "Normal").sum())
col2.metric("Warning", (df["system_decision"] == "Warning").sum())
col3.metric("Critical", (df["system_decision"] == "Critical").sum())


# ------------------------------------------------------------------
# Timeline visualization
# ------------------------------------------------------------------
st.header("⏱️ Safety Decision Timeline")

fig, ax = plt.subplots(figsize=(14, 4))

ax.scatter(
    df["timestamp"],
    df["system_decision"].map(DECISION_MAP),
    c=df["system_decision"].map(COLOR_MAP),
    s=10,
)

ax.set_yticks([0, 1, 2])
ax.set_yticklabels(["Normal", "Warning", "Critical"])
ax.set_xlabel("Time")
ax.set_title("System Decision Over Time")

st.pyplot(fig)

st.markdown(
    """
    **Interpretation guidance**
    - Gradual transitions → stable system
    - Sudden CRITICAL spikes → investigate root cause
    - Long calm stretches → healthy operations
    """
)


# ------------------------------------------------------------------
# Warning cluster analysis
# ------------------------------------------------------------------
st.header("⚠️ Warning Cluster Analysis")

warning_df = df[df["system_decision"] == "Warning"]

fig2, ax2 = plt.subplots(figsize=(14, 4))
ax2.plot(
    warning_df["timestamp"],
    warning_df["warning_streak"],
    color="orange",
)

ax2.set_title("Warning Persistence Over Time")
ax2.set_ylabel("Consecutive Warning Count")
ax2.set_xlabel("Time")

st.pyplot(fig2)


# ------------------------------------------------------------------
# Calm period analysis
# ------------------------------------------------------------------
st.header("🌱 Calm Period Analysis")

df["is_calm"] = df["system_decision"] == "Normal"
df["calm_streak"] = (
    df["is_calm"]
    .astype(int)
    .groupby((~df["is_calm"]).cumsum())
    .cumsum()
)

fig3, ax3 = plt.subplots(figsize=(14, 4))
ax3.plot(
    df["timestamp"],
    df["calm_streak"],
    color="green",
)

ax3.set_title("Calm (Normal) Persistence Over Time")
ax3.set_ylabel("Consecutive Normal Count")
ax3.set_xlabel("Time")

st.pyplot(fig3)


# ------------------------------------------------------------------
# Final assessment
# ------------------------------------------------------------------
st.header("🧠 Operational Assessment")

st.markdown(
    """
    ### What this replay tells us

    ✔ Decisions are **stable**, not oscillatory  
    ✔ Warnings **cluster**, rather than flicker  
    ✔ Critical events are **rare and explainable**  
    ✔ Calm periods dominate — as expected in real systems  

    ### Conclusion

    The system behavior is **operationally realistic** and
    appropriate for **safety-first environments**, provided
    human oversight remains in the loop.
    """
)
