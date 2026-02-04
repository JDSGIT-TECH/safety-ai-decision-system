import pandas as pd
import numpy as np

# Configuration
N_ROWS = 250
START_TIME = "2025-01-01 08:00:00"
SEED = 42

np.random.seed(SEED)

#Generate timestamps
timestamps = pd.date_range(start = START_TIME, periods = N_ROWS, freq = "2min")

#Generate risk levels with escalation logic
risk_levels = []
warning_streaks = []
decisions = []

current_streak = 0

for _ in range(N_ROWS):
    roll = np.random.rand()

    if roll < 0.75:
        risk = 0
        current_streak = 0
        decision = "Normal"
    elif roll < 0.93:
        risk = 1
        current_streak += 1
        decision = "Warning"
    else:
        risk = 2
        current_streak += 1
        decision = "Critical"

    #Escalation Rule
    if current_streak >= 3 and risk == 1:
        risk = 2
        decision = "Critical"
    
    risk_levels.append(risk)
    warning_streaks.append(current_streak)
    decisions.append(decision)

#Build Dataframe
df = pd.DataFrame({
    "timestamp": timestamps,
    "system_decision": decisions,
    "warning_streak": warning_streaks,
    "risk_level": risk_levels
})

#Save Demo File
output_path = "outputs/demo_safety_timeline.csv"
df.to_csv(output_path, index=False)

print(f"✅ Demo safety timeline generated: {output_path}")
print("Rows: ", len(df))
print(df.head())

