
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wise Ops Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Operational_Analyst_Take_Home_Task.csv")
    datetime_cols = [
        'CASE_CREATED_TIME', 'CASE_BACKLOG_ENTRY_TIME',
        'HANDLING_TIME_START', 'HANDLING_TIME_END'
    ]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    df['HANDLING_DURATION_MIN'] = (df['HANDLING_TIME_END'] - df['HANDLING_TIME_START']).dt.total_seconds() / 60
    df['BACKLOG_DELAY_MIN'] = (df['HANDLING_TIME_START'] - df['CASE_BACKLOG_ENTRY_TIME']).dt.total_seconds() / 60
    df['CASE_AGE_AT_REVIEW_MIN'] = (df['HANDLING_TIME_START'] - df['CASE_CREATED_TIME']).dt.total_seconds() / 60
    df['REVIEW_DATE'] = df['HANDLING_TIME_END'].dt.date

    # Clean data
    valid_df = df[
        (df['HANDLING_DURATION_MIN'] >= 0) &
        (df['BACKLOG_DELAY_MIN'] >= 0) &
        (df['CASE_AGE_AT_REVIEW_MIN'] >= 0)
    ]
    duration_caps = valid_df[['HANDLING_DURATION_MIN', 'BACKLOG_DELAY_MIN', 'CASE_AGE_AT_REVIEW_MIN']].quantile(0.99)
    filtered_df = valid_df[
        (valid_df['HANDLING_DURATION_MIN'] <= duration_caps['HANDLING_DURATION_MIN']) &
        (valid_df['BACKLOG_DELAY_MIN'] <= duration_caps['BACKLOG_DELAY_MIN']) &
        (valid_df['CASE_AGE_AT_REVIEW_MIN'] <= duration_caps['CASE_AGE_AT_REVIEW_MIN'])
    ]
    return filtered_df

df = load_data()

st.title("📊 Operational Analytics Dashboard – Wise")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Reviews", f"{df.shape[0]:,}")
col2.metric("Unique Agents", df['ACTOR_ID'].nunique())
col3.metric("Avg Handling Time", f"{df['HANDLING_DURATION_MIN'].mean():.2f} min")

st.markdown("---")

# Daily Review Volume
st.subheader("📅 Daily Review Volume")
daily_vol = df.groupby('REVIEW_DATE')['REVIEW_ID'].count()
fig, ax = plt.subplots(figsize=(12, 4))
daily_vol.plot(ax=ax)
ax.set_ylabel("Reviews")
st.pyplot(fig)

# Handling Duration Distribution
st.subheader("⏱️ Handling Time Distribution")
fig, ax = plt.subplots(figsize=(10, 4))
sns.histplot(df['HANDLING_DURATION_MIN'], bins=100, kde=True, ax=ax)
ax.set_xlabel("Handling Time (min)")
st.pyplot(fig)

# Backlog Delay
st.subheader("🧺 Backlog Delay Distribution")
fig, ax = plt.subplots(figsize=(10, 4))
sns.histplot(df['BACKLOG_DELAY_MIN'], bins=100, kde=True, ax=ax)
ax.set_xlabel("Backlog Delay (min)")
st.pyplot(fig)

# Top Agents
st.subheader("👩‍💻 Top 10 Agents by Reviews")
top_agents = df.groupby('ACTOR_ID')['REVIEW_ID'].count().sort_values(ascending=False).head(10)
fig, ax = plt.subplots()
top_agents.plot(kind='barh', ax=ax, color="#4c72b0")
ax.set_xlabel("Review Count")
st.pyplot(fig)

# Case Type Breakdown
st.subheader("📋 Case Type Distribution")
case_type_pct = df['CASE_TYPE'].value_counts(normalize=True) * 100
fig, ax = plt.subplots()
case_type_pct.plot(kind='bar', ax=ax, color=["#4c72b0", "#55a868", "#c44e52"])
ax.set_ylabel("Percentage")
st.pyplot(fig)

# TYPE_THREE Explorer
st.subheader("🔍 TYPE_THREE Case Insights")
type3 = df[df['CASE_TYPE'] == 'TYPE_THREE']
st.write("Total TYPE_THREE Reviews:", type3.shape[0])
col1, col2 = st.columns(2)
col1.metric("Avg Handling Time", f"{type3['HANDLING_DURATION_MIN'].mean():.2f} min")
col2.metric("Median Backlog Delay", f"{type3['BACKLOG_DELAY_MIN'].median():.2f} min")
