import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Ecommerce Consumer Behavior Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Ecommerce Consumer Behavior Dashboard")
st.caption("""MGMT 504 — Programming for Business Analytics
Fall 2025
Team Project — Ecommerce Consumer Behavior Dashboard
Contributors: Allison Gelman, Samantha Barron, Emily Kilman, Haley Caricati, & Jordan Fishler""")

with st.expander("ℹ️ About This Dashboard", expanded=True):
    st.markdown("""
    ### 📊 Ecommerce Consumer Behavior Dashboard

    This interactive dashboard analyzes a simulated ecommerce dataset to uncover patterns 
    in customer behavior. It allows users to explore relationships between customer demographics,
    purchase frequency, spending habits, and brand loyalty.

    #### 💡 Features
    - Filter by **product category**, **purchase channel**, **gender**, and **income level**
    - View **key performance metrics** (revenue, avg. purchase, customer count)
    - Analyze **revenue by category**, **purchase preferences**, and **demographic trends**
    - Explore **behavioral relationships** like purchase frequency vs. amount

    #### 🎯 Goal
    Provide business insights that support better marketing strategies, product targeting, 
    and customer retention.

    Use the sidebar filters to interact with the data!
    """)


# =====================
# LOAD DATA
# =====================
@st.cache_data
def load_data(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        st.error(f"CSV file not found: {csv_path}. "
                 f"Make sure it is in the same folder as app.py.")
        return None
    df = pd.read_csv(path)
    return df

df = load_data("ecommerce_consumer_behavior.csv")  # <-- Change if your file has a different name

if df is None:
    st.stop()

# Convert Purchase_Amount to numeric (remove $ and convert to float)
if "Purchase_Amount" in df.columns:
    df["Purchase_Amount"] = (
        df["Purchase_Amount"]
        .replace('[\$,]', '', regex=True)
        .astype(float)
    )

st.subheader("Dataset Preview")
st.dataframe(df.head())
st.write(f"Rows: **{df.shape[0]}**, Columns: **{df.shape[1]}**")

# =====================
# SIDEBAR FILTERS
# =====================
st.sidebar.header("Filter Data")

def get_options(col_name):
    if col_name in df.columns:
        return sorted(df[col_name].dropna().unique())
    return []

purchase_channels = get_options("Purchase_Channel")
categories = get_options("Purchase_Category")
genders = get_options("Gender")
income_levels = get_options("Income_Level")

selected_channel = st.sidebar.multiselect(
    "Purchase Channel",
    options=purchase_channels,
    default=purchase_channels if purchase_channels else []
)

selected_category = st.sidebar.multiselect(
    "Product Category",
    options=categories,
    default=categories if categories else []
)

selected_gender = st.sidebar.multiselect(
    "Gender",
    options=genders,
    default=genders if genders else []
)

selected_income = st.sidebar.multiselect(
    "Income Level",
    options=income_levels,
    default=income_levels if income_levels else []
)

filtered_df = df.copy()

if selected_channel:
    filtered_df = filtered_df[filtered_df["Purchase_Channel"].isin(selected_channel)]
if selected_category:
    filtered_df = filtered_df[filtered_df["Purchase_Category"].isin(selected_category)]
if selected_gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]
if selected_income:
    filtered_df = filtered_df[filtered_df["Income_Level"].isin(selected_income)]

st.sidebar.markdown("---")
st.sidebar.write(f"Filtered rows: **{filtered_df.shape[0]}**")

# =====================
# KPI CARDS
# =====================
st.markdown("### Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["Purchase_Amount"].sum() if "Purchase_Amount" in filtered_df.columns else 0
avg_purchase = filtered_df["Purchase_Amount"].mean() if "Purchase_Amount" in filtered_df.columns else 0
num_customers = filtered_df["Customer_ID"].nunique() if "Customer_ID" in filtered_df.columns else filtered_df.shape[0]
avg_frequency = filtered_df["Frequency_of_Purchase"].mean() if "Frequency_of_Purchase" in filtered_df.columns else 0

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Unique Customers", f"{num_customers:,}")
col3.metric("Avg Purchase Amount", f"${avg_purchase:,.2f}")
col4.metric("Avg Purchase Frequency", f"{avg_frequency:.2f} / month")

# =====================
# TABS
# =====================
tab_overview, tab_demo, tab_behavior = st.tabs(
    ["📌 Overview", "👥 Demographics", "📈 Behavior"]
)

# ----- TAB 1: OVERVIEW -----
with tab_overview:
    st.subheader("Revenue by Product Category")
    if "Purchase_Category" in filtered_df.columns and "Purchase_Amount" in filtered_df.columns:
        category_rev = (
            filtered_df.groupby("Purchase_Category")["Purchase_Amount"]
            .sum()
            .reset_index()
            .sort_values("Purchase_Amount", ascending=False)
        )
        fig_cat = px.bar(category_rev, x="Purchase_Category", y="Purchase_Amount",
                         title="Total Revenue by Category")
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Purchases by Channel")
    if "Purchase_Channel" in filtered_df.columns:
        channel_counts = filtered_df["Purchase_Channel"].value_counts().reset_index()
        channel_counts.columns = ["Purchase_Channel", "Count"]
        fig_channel = px.pie(channel_counts, names="Purchase_Channel", values="Count",
                             title="Share of Purchases by Channel")
        st.plotly_chart(fig_channel, use_container_width=True)

# ----- TAB 2: DEMOGRAPHICS -----
with tab_demo:
    st.subheader("Customer Demographics")

    colA, colB = st.columns(2)

    with colA:
        if "Age" in filtered_df.columns:
            fig_age = px.histogram(filtered_df, x="Age", nbins=10, title="Age Distribution")
            st.plotly_chart(fig_age, use_container_width=True)

    with colB:
        if "Gender" in filtered_df.columns:
            gender_counts = filtered_df["Gender"].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]
            fig_gender = px.bar(gender_counts, x="Gender", y="Count",
                                title="Customers by Gender")
            st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown("---")

    if "Income_Level" in filtered_df.columns and "Purchase_Amount" in filtered_df.columns:
        income_rev = (
            filtered_df.groupby("Income_Level")["Purchase_Amount"]
            .mean().reset_index().sort_values("Purchase_Amount", ascending=False)
        )
        fig_income = px.bar(income_rev, x="Income_Level", y="Purchase_Amount",
                            title="Avg Purchase Amount by Income Level")
        st.plotly_chart(fig_income, use_container_width=True)

# ----- TAB 3: BEHAVIOR -----
with tab_behavior:
    st.subheader("Purchase Frequency vs Amount")
    if "Frequency_of_Purchase" in filtered_df.columns and "Purchase_Amount" in filtered_df.columns:
        fig_scatter = px.scatter(
            filtered_df,
            x="Frequency_of_Purchase",
            y="Purchase_Amount",
            color="Purchase_Category" if "Purchase_Category" in filtered_df.columns else None,
            title="Frequency vs Purchase Amount"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Average Brand Loyalty by Category")
    if "Brand_Loyalty" in filtered_df.columns and "Purchase_Category" in filtered_df.columns:
        loyalty = (
            filtered_df.groupby("Purchase_Category")["Brand_Loyalty"]
            .mean().reset_index().sort_values("Brand_Loyalty", ascending=False)
        )
        fig_loyalty = px.bar(loyalty, x="Purchase_Category", y="Brand_Loyalty",
                             title="Avg Brand Loyalty by Category")
        st.plotly_chart(fig_loyalty, use_container_width=True)

# ======================
# PERSONAL SHOPPING INSIGHTS
# ======================
st.subheader("🛒 Personalized Shopping Insights")

age_input = st.selectbox("Select Your Age Group:", sorted(df["Age"].unique()))
income_input = st.selectbox("Select Your Income Level:", sorted(df["Income_Level"].unique()))
channel_input = st.selectbox("Preferred Purchase Channel:", sorted(df["Purchase_Channel"].unique()))
category_input = st.selectbox("Preferred Product Category:", sorted(df["Product_Category"].unique()))

if st.button("Get My Insights"):
    user_segment = df[
        (df["Age"] == age_input) &
        (df["Income_Level"] == income_input) &
        (df["Purchase_Channel"] == channel_input)
    ]

    if user_segment.empty:
        st.warning("No exact match — showing closest matches instead.")
        user_segment = df[df["Income_Level"] == income_input]

    avg_spending = user_segment["Purchase_Amount"].mean()
    top_category = user_segment["Product_Category"].mode()[0]
    avg_frequency = user_segment["Purchase_Frequency"].mean()

    overall_avg_spending = df["Purchase_Amount"].mean()
    overall_avg_frequency = df["Purchase_Frequency"].mean()

    st.success("### 🎯 Personalized Insights Just for You")
    st.markdown(f"""
    **Shoppers like you typically…**
    - 💵 Spend **${avg_spending:.2f}** per purchase
    - ⭐ Prefer **{top_category}**
    - 🔁 Order **{avg_frequency:.1f}** times per month
    """)

    # Comparison Chart
    compare_df = pd.DataFrame({
        "Metric": ["Avg Spending", "Purchase Frequency"],
        "You": [avg_spending, avg_frequency],
        "All Shoppers": [overall_avg_spending, overall_avg_frequency]
    })

    fig_compare = px.bar(compare_df, x="Metric", y=["You", "All Shoppers"], barmode="group",
                         title="📊 You vs. Other Shoppers")
    st.plotly_chart(fig_compare)

    # AI-style Recommendation System
    st.subheader("💡 Recommendation")
    if avg_spending > overall_avg_spending and avg_frequency > overall_avg_frequency:
        rec = "🔥 You're a high-value frequent shopper — personalized loyalty rewards recommended!"
    elif avg_spending > overall_avg_spending:
        rec = "💰 You love premium purchases — consider exclusive membership perks."
    elif avg_frequency > overall_avg_frequency:
        rec = "🌟 Frequent shopper — subscription bundles could save you more!"
    else:
        rec = "💡 Look for seasonal deals and personalized offers to maximize value."

    st.info(rec)

    # Downloadable PDF (as a text export for now)
    report_text = f'''
    Personalized Shopper Report:
    Age Group: {age_input}
    Income Level: {income_input}
    Preferred Channel: {channel_input}
    Avg Purchase Amount: ${avg_spending:.2f}
    Most Purchased Category: {top_category}
    Monthly Order Frequency: {avg_frequency:.1f}
    Recommendation: {rec}
    '''

    st.download_button("📥 Download My Report", report_text, file_name="shopping_insights.txt")


# =====================
# CUSTOM STYLING
# =====================
st.markdown("""
<style>
/* Clean card look for key metrics */
[data-testid="metric-container"] {
    background: rgba(28, 131, 225, 0.1);
    border-radius: 12px;
    padding: 10px;
    margin: 6px;
}

/* Title styling */
h1 {
    font-weight: 700;
}

/* Hide Streamlit branding footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
