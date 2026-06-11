import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

st.title("Care System Capacity Dashboard")

@st.cache_data
def load_data():
    hs = pd.read_csv("U_H_U_A_C_P.csv", index_col=0, parse_dates=True)
    
    return hs

hs = load_data()

st.write("Dataset Preview")
st.dataframe(hs)

#================
# Sidebar
#================
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", hs.index.min())
end_date = st.sidebar.date_input("End Date", hs.index.max())
hs = hs.loc[start_date:end_date]

# Metric Toggles
metric = st.sidebar.multiselect("Select Metric",["Total_System_Load", "Net Daily Intake", "Care Load Volatility Index","Backlog_Accumulation_Rate","Discharge_Offset_Ratio"], default=["Total_System_Load"])

st.line_chart(hs[metric])

#Time Granularity Filters
granularity = st.sidebar.selectbox("Time Granularity",["Daily", "Weekly", "Monthly"])

if granularity == "Weekly":
    display_hs = hs.resample("W").mean()

elif granularity == "Monthly":
    display_hs = hs.resample("M").mean()

else:
    display_hs = hs

st.line_chart(display_hs[metric])

#=================
# KPI CARDS
#=================

st.title("Welcome to the System Capacity Monitoring Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

# 1. Total Children Under Care - System-wide responsibility
col1.metric("Total Load", int(hs["Total_System_Load"].iloc[-1]))

# 2. Net Intake Pressure - Inflow vs outflow imbalance
col2.metric("Net Intake", int(hs["Net Daily Intake"].iloc[-1]))

# 3. Care Load Volatility Index - Stability of system
col3.metric("Volatility Index", round(hs["Care_Load_Volatility_Index"].iloc[-1], 3))

# 4. Backlog Accumulation Rate - Sustained care pressure
col4.metric("Backlog Rate", int(hs["Backlog_Accumulation_Rate"].iloc[-1]))

# 5.Discharge Offset Ratio - Ability to relieve load
col5.metric("Discharge_Offset_Ratio", round(hs["Discharge_Offset_Ratio"].iloc[-1], 3))

#========================
# System Load Overview Pane
#========================
st.subheader("System Load Overview")

fig1, ax1 = plt.subplots(figsize=(10,5))
sns.lineplot(data=hs["Total_System_Load"], ax=ax1)

ax1.set_title("Total System Load Trend")
st.pyplot(fig1)

#=========================
# CBP vs HHS Load Comparison
#=========================
st.subheader("CBP vs HHS Load Comparison")

fig2, ax2 = plt.subplots(figsize=(10,5))

sns.lineplot(data=hs["CBP_custody"], label="CBP", ax=ax2)
sns.lineplot(data=hs["HHS_care"], label="HHS", ax=ax2)

ax2.set_title("CBP vs HHS Load")
st.pyplot(fig2)

#============================
# Net Intake & Backlog Trends
#============================
st.subheader("Net Intake & Backlog Trends")

fig, ax = plt.subplots(figsize=(14,6))
sns.lineplot(data=hs,x=hs.index,y='Net Daily Intake',label='Net Intake Pressure',ax=ax)
sns.lineplot(data=hs,x=hs.index,y='Backlog_Accumulation_Rate',label='Backlog Accumulation Rate',ax=ax)
ax.set_title("Pressure & Backlog Trends")
ax.set_xlabel("Date")
ax.set_ylabel("Value")
plt.xticks(rotation=45)
st.pyplot(fig)

#============================
# Stress Heatmap
#============================
st.subheader("Stress Heatmap")

heatmap_data=hs.pivot_table(values='Total_System_Load',index=hs.index.month,columns=hs.index.year,aggfunc='mean')
fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(heatmap_data,cmap='Reds',annot=True,ax=ax)
st.pyplot(fig)

#===================================
# Metric Based Trend(User Selected)
#===================================
st.subheader("Data Quality Overview")

st.write("Missing Records:",hs['missing_flag'].sum())

st.write("Invalid Transfers:",hs['invalid_transfer_anomaly'].sum())

#===================================
# More Enhancements
#===================================
if hs['Backlog_Accumulation_Rate'].mean() > 100:
    st.warning("High backlog pressure detected!")

st.download_button("Download Filtered Data",hs.to_csv().encode(),"filtered_data.csv")