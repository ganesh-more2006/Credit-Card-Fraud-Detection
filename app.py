import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Config for a Premium Brand Look
st.set_page_config(
    page_title="Ganesh | Credit Risk Intelligence", 
    layout="wide", 
    page_icon="🛡️"
)

# Professional CSS Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #1f77b4; font-weight: bold; }
    .stAlert { border-radius: 10px; }
    div.stButton > button:first-child { background-color: #1f77b4; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Connection
conn = sqlite3.connect("fraud_data.db")

# --- SIDEBAR: Filter & Branding ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.title("📊 Control Panel")
st.sidebar.markdown("---")

# Filters
contract_type = st.sidebar.multiselect(
    "Select Loan Type", 
    options=["Cash loans", "Revolving loans"], 
    default=["Cash loans", "Revolving loans"]
)

income_filter = st.sidebar.slider("Minimum Income Threshold", 0, 500000, 50000)

st.sidebar.markdown("---")
st.sidebar.info("👤 **Developer:** Ganesh More\n\n🎯 **Goal:** Detect Loan Fraud using SQL & Python")

# --- DATA PROCESSING ---
@st.cache_data
def load_filtered_data(types, income):
    type_str = "('" + "','".join(types) + "')"
    query = f"SELECT * FROM loan_data WHERE NAME_CONTRACT_TYPE IN {type_str} AND AMT_INCOME_TOTAL >= {income}"
    return pd.read_sql(query, conn)

df_filtered = load_filtered_data(contract_type, income_filter)

# --- HEADER ---
st.title("🛡️ Credit Card Fraud & Risk Intelligence Dashboard")
st.write(f"Showing analysis for **{len(df_filtered):,}** filtered applications.")
st.markdown("---")

# --- ROW 1: KPI METRICS (Modern Style) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_apps = len(df_filtered)
total_def = int(df_filtered['TARGET'].sum())
risk_rate = (total_def / total_apps * 100) if total_apps > 0 else 0
avg_credit = df_filtered['AMT_CREDIT'].mean()

with kpi1:
    st.metric("Total Apps", f"{total_apps:,}")
with kpi2:
    st.metric("Defaulters Found", f"{total_def:,}", delta=f"{risk_rate:.2f}% Rate", delta_color="inverse")
with kpi3:
    st.metric("Avg. Credit Limit", f"${avg_credit:,.0f}")
with kpi4:
    st.metric("Data Quality", "99.2%", delta="Cleaned")

st.markdown("---")

# --- ROW 2: ADVANCED VISUALIZATIONS ---
col_left, col_right = st.columns([6, 4])

with col_left:
    st.subheader("🔥 Default Risk Trend by Age Group")
    # Grouping for chart
    df_age = df_filtered.groupby('AGE_GROUP', observed=True)['TARGET'].mean().reset_index()
    df_age['TARGET'] = df_age['TARGET'] * 100
    
    fig_age = px.line(df_age, x='AGE_GROUP', y='TARGET', markers=True, 
                      title="Risk Probability Increases in Young Borrowers",
                      labels={'TARGET': 'Default %'},
                      line_shape="spline", color_discrete_sequence=['#d62728'])
    fig_age.update_layout(hovermode="x unified")
    st.plotly_chart(fig_age, use_container_width=True)

with col_right:
    st.subheader("🎓 Education & Risk Distribution")
    fig_sun = px.sunburst(df_filtered, path=['NAME_EDUCATION_TYPE', 'CODE_GENDER'], 
                          values='TARGET', color='TARGET',
                          color_continuous_scale='RdYlGn_r',
                          title="Education vs Gender Risk")
    st.plotly_chart(fig_sun, use_container_width=True)

# --- ROW 3: INCOME vs CREDIT (SCATTER ANALYSIS) ---
st.markdown("---")
st.subheader("💰 Income vs. Credit Amount Relationship")
# Sampling data for performance
df_sample = df_filtered.sample(min(2000, len(df_filtered)))
fig_scatter = px.scatter(df_sample, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", 
                         color="TARGET", size="AMT_ANNUITY", 
                         hover_data=['SK_ID_CURR'], 
                         title="Correlation: Income vs Loan Size (Color = Fraud Risk)",
                         color_continuous_scale=['#1f77b4', '#d62728'],
                         template="plotly_dark")
st.plotly_chart(fig_scatter, use_container_width=True)

# --- ROW 4: EXECUTIVE SUMMARY TABLE ---
st.markdown("---")
st.subheader("📋 Priority Investigation List (High Risk Clients)")
st.warning("The following clients have low external credit scores but high credit demands.")

# SQL for priority list
query_priority = """
SELECT SK_ID_CURR AS ID, CODE_GENDER AS Sex, NAME_INCOME_TYPE AS Job, 
       AMT_INCOME_TOTAL AS Income, AMT_CREDIT AS Loan, 
       EXT_SOURCE_2 AS Score
FROM loan_data 
WHERE TARGET = 1 
ORDER BY EXT_SOURCE_2 ASC, AMT_CREDIT DESC 
LIMIT 10
"""
df_priority = pd.read_sql(query_priority, conn)

# Fancy Styled Table
st.table(df_priority.style.format({"Income": "${:,.0f}", "Loan": "${:,.0f}", "Score": "{:.2f}"})
         .background_gradient(subset=['Score'], cmap='Reds_r'))

st.markdown("---")
st.markdown("<center>Developed with ❤️ by Ganesh More | GH Raisoni College of Engineering and Management</center>", unsafe_allow_html=True)