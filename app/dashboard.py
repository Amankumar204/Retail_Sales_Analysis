import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('superstore.csv', encoding='ISO-8859-1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Order Month'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Data")
regions = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
segments = st.sidebar.multiselect("Segment", df['Segment'].unique(), default=df['Segment'].unique())

filtered_df = df[
    df['Region'].isin(regions) &
    df['Category'].isin(categories) &
    df['Segment'].isin(segments)
]

# --- KPIs ---
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_margin = filtered_df['Profit Margin'].mean()

st.title("📊 Retail Sales Dashboard")
st.markdown("Use the sidebar to filter by Region, Category, and Segment.")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("📈 Total Profit", f"${total_profit:,.2f}")
col3.metric("📊 Avg Profit Margin", f"{avg_margin:.2%}")

st.markdown("---")

# --- TOGGLE ---
show_charts = st.checkbox("Show Visual Analysis", value=True)

if show_charts:
    # --- CHART 1: Monthly Sales Trend ---
    st.subheader("📅 Monthly Sales Trend")
    monthly_sales = filtered_df.groupby('Order Month')['Sales'].sum().reset_index()
    fig1 = px.line(monthly_sales, x='Order Month', y='Sales', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # --- CHART 2: Sub-Category Sales & Profit ---
    st.subheader("📦 Sub-Category Performance")
    subcat = filtered_df.groupby('Sub-Category')[['Sales', 'Profit']].sum().reset_index()
    fig2 = px.bar(subcat, x='Sub-Category', y='Sales', color='Profit', title='Sub-Category Sales vs Profit')
    st.plotly_chart(fig2, use_container_width=True)

    # --- CHART 3: Heatmap of Region vs Category ---
    st.subheader("🌍 Heatmap: Region vs Category Sales")
    heat_data = filtered_df.pivot_table(index='Region', columns='Category', values='Sales', aggfunc='sum')
    fig3 = px.imshow(heat_data, text_auto=True, aspect='auto', color_continuous_scale='Blues')
    st.plotly_chart(fig3, use_container_width=True)

# --- TOP PRODUCTS TABLE ---
st.subheader("🏆 Top 10 Products by Sales")
top_products = (
    filtered_df.groupby('Product Name')['Sales']
    .sum().sort_values(ascending=False)
    .head(10).reset_index()
)
st.dataframe(top_products, use_container_width=True)

# --- DOWNLOAD BUTTON ---
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_superstore_data.csv',
    mime='text/csv'
)