import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load Data with Caching
@st.cache_data
def load_data():
    df = pd.read_csv('club_concierge_product_performance.csv', parse_dates=['BookingDate'])
    df['Month'] = df['BookingDate'].dt.to_period('M').astype(str)
    return df

# Initialize Session State
if 'filter_service' not in st.session_state:
    st.session_state['filter_service'] = 'All'

# Load Dataset
df = load_data()

# Page Config
st.set_page_config(page_title="Club Concierge Product Performance Dashboard", layout="wide")

# Title and Description
st.title("\U0001F4CA Club Concierge Product Performance & KPI Dashboard")
st.markdown("""
This interactive dashboard provides insights into booking trends, service performance, customer satisfaction, and operational efficiency. Use the filters below to explore the data and uncover actionable insights.
""")

# Sidebar Filters
with st.sidebar:
    st.header("Filters")
    service_list = ['All'] + sorted(df['Service'].unique().tolist())
    service_filter = st.selectbox("Select Service", service_list, index=0, key='filter_service')

    date_range = st.date_input("Select Date Range", [df['BookingDate'].min(), df['BookingDate'].max()])

# Apply Filters
filtered_df = df.copy()
if service_filter != 'All':
    filtered_df = filtered_df[filtered_df['Service'] == service_filter]

filtered_df = filtered_df[(filtered_df['BookingDate'] >= pd.to_datetime(date_range[0])) &
                          (filtered_df['BookingDate'] <= pd.to_datetime(date_range[1]))]

# KPI Metrics
total_bookings = filtered_df['BookingID'].nunique()
total_revenue = filtered_df['Revenue'].sum()
avg_revenue = filtered_df['Revenue'].mean()
avg_satisfaction = filtered_df['CustomerSatisfaction'].mean()

vip_revenue = filtered_df.loc[filtered_df['CustomerType'] == 'VIP Member', 'Revenue'].sum()
call_center_rate = filtered_df['HandledByCallCenter'].value_counts(normalize=True).get('Yes', 0) * 100

# KPI Display
col1, col2, col3 = st.columns(3)
col1.metric("Total Bookings", f"{total_bookings}")
col2.metric("Total Revenue", f"₦{total_revenue:,.0f}")
col3.metric("Avg Revenue per Booking", f"₦{avg_revenue:,.0f}")

col4, col5, col6 = st.columns(3)
col4.metric("Avg Satisfaction", f"{avg_satisfaction:.2f} ⭐")
col5.metric("VIP Revenue", f"₦{vip_revenue:,.0f}")
col6.metric("Call Center Handling", f"{call_center_rate:.1f}%")

# Charts: Monthly Trends
monthly_summary = filtered_df.groupby('Month').agg({
    'BookingID': 'nunique',
    'Revenue': 'sum',
    'CustomerSatisfaction': 'mean'
}).reset_index()

fig_bookings = px.line(monthly_summary, x='Month', y='BookingID', title='Monthly Bookings', markers=True)
fig_revenue = px.line(monthly_summary, x='Month', y='Revenue', title='Monthly Revenue', markers=True)
fig_satisfaction = px.line(monthly_summary, x='Month', y='CustomerSatisfaction', title='Monthly Satisfaction', markers=True)

st.plotly_chart(fig_bookings, use_container_width=True)
st.plotly_chart(fig_revenue, use_container_width=True)
st.plotly_chart(fig_satisfaction, use_container_width=True)

# Service Performance
service_perf = filtered_df.groupby('Service').agg({'BookingID':'nunique', 'Revenue':'sum'}).sort_values('Revenue', ascending=False).reset_index()
fig_service_rev = px.bar(service_perf, x='Service', y='Revenue', title='Revenue by Service', color='Service')
fig_service_book = px.bar(service_perf, x='Service', y='BookingID', title='Bookings by Service', color='Service')

st.plotly_chart(fig_service_rev, use_container_width=True)
st.plotly_chart(fig_service_book, use_container_width=True)

# Customer Type Distribution
cust_dist = filtered_df['CustomerType'].value_counts(normalize=True).reset_index()
cust_dist.columns = ['CustomerType', 'Percentage']
cust_dist['Percentage'] *= 100
fig_cust_pie = px.pie(cust_dist, values='Percentage', names='CustomerType', title='Customer Type Distribution', hole=0.4)

st.plotly_chart(fig_cust_pie, use_container_width=True)

# Call Center Distribution
call_dist = filtered_df['HandledByCallCenter'].value_counts().reset_index()
call_dist.columns = ['HandledByCallCenter', 'Count']
fig_call_pie = px.pie(call_dist, values='Count', names='HandledByCallCenter', title='Call Center Handling Share', hole=0.4)

st.plotly_chart(fig_call_pie, use_container_width=True)

st.markdown("---")
st.markdown("\n\n\n© 2025 Club Concierge Africa Data Dashboard by Rejoice Chinwendu")
