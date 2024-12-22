import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_folium import folium_static
from babel.numbers import format_currency

from helper_function import HelperFunctions, HelperMap

# Load cleaned data
all_df = pd.read_csv("dashboard/all_data.csv")
geo_df = pd.read_csv("dashboard/geo_cust.csv")

# all_df dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df["order_approved_at"] = pd.to_datetime(all_df["order_approved_at"])
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

min_date = all_df["order_approved_at"].min().date()
max_date = all_df["order_approved_at"].max().date()

# Sidebar
with st.sidebar:
    # Title
    st.title("Habellio Tifano")

    # Logo Image
    # st.image("./dashboard/streamlit-mark-light.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

function = HelperFunctions(main_df)
function2 = HelperFunctions(geo_df)
map_plot = HelperMap(geo_df, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df, top_order, bot_order = function.create_sum_order_items_df()
average_score, review_counts = function.review_score_df()
state_customer_counts = function2.create_by_state_df()
order_status, common_status = function.create_order_status()

# Title
st.header("Brazil E-Commerce Dashboard")

# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Comparison
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

# Top 10 products
sns.barplot(x='product_count', y='product_category_name_english', data=top_order, palette='summer', ax=ax[0])
ax[0].set_title('Top 10 Best-Selling Products', loc="center", fontsize=90)
ax[0].set_xlabel('Count',fontsize=80)
ax[0].set_ylabel('Product Category', fontsize=80)
ax[0].tick_params(axis ='y', labelsize=55)
ax[0].tick_params(axis ='x', labelsize=50)

# Bottom 10 products
sns.barplot(x='product_count', y='product_category_name_english', data=bot_order, palette='summer_r', ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('Count', fontsize=80)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Top 10 Least-Selling Products", loc="center", fontsize=90)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)

st.pyplot(fig)


# Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    total_reviews = review_counts.values.sum()
    st.markdown(f"Total Reviews: **{total_reviews}**")

with col2:
    avg_review = average_score
    st.markdown(f"Average Review Score: **{avg_review:.2f}**")


fig = plt.figure(figsize=(8, 6))

sns.barplot(x=review_counts.index.astype(str), y=review_counts.values, palette=["Blue" if score == review_counts.idxmax()
 else "Gray" for score in review_counts.index])
plt.title('Distribution of Review Scores')
plt.xlabel('Review Score')
plt.ylabel('Count')
plt.xticks(range(len(review_counts.index)), review_counts.index)

st.pyplot(fig)

# Demographic
st.subheader("Customer Demographic")
tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    fig = plt.figure(figsize=(10, 6))
    sns.barplot(
        x=state_customer_counts.index,
        y=state_customer_counts.values,
        palette=["Blue" if state == state_customer_counts.idxmax() else "Gray" for state in state_customer_counts.index]
    )
    plt.title('Customer Distribution by State')
    plt.xlabel('State')
    plt.ylabel('Customer Count')
    plt.xticks(rotation=45)
    st.pyplot(fig)


with tab2:
    folium_static(map_plot.show_map())