import folium
from folium.plugins import HeatMap


class HelperFunctions:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)

        return daily_orders_df

    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        })
        sum_spend_df = sum_spend_df.reset_index()
        sum_spend_df.rename(columns={
            "payment_value": "total_spend"
        }, inplace=True)

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        top_order = sum_order_items_df.sort_values(by='product_count', ascending=False).head(10)
        bot_order = sum_order_items_df.sort_values(by="product_count", ascending=True).head(10)

        return sum_order_items_df, top_order, bot_order

    def review_score_df(self):
        average_score = self.df['review_score'].mean()
        review_counts = self.df['review_score'].value_counts().sort_index()
        review_counts = review_counts.reindex(range(1, 6), fill_value=0)

        return average_score, review_counts

    def create_by_state_df(self):
        # state_customer_counts = self.df.groupby('geolocation_state')[
        #     'customer_count'].sum().reset_index()
        #
        # state_customer_counts.rename(columns={'geolocation_state': 'State', 'customer_count': 'Total_Customers'},
        #                              inplace=True)
        #
        # state_customer_counts = state_customer_counts.sort_values(by='Total_Customers', ascending=False)
        #
        # state_customer_counts= state_customer_counts['State'].value_counts()
        state_counts = self.df['geolocation_state'].value_counts()

        return state_counts

    def create_order_status(self):
        order_status_df = self.df["order_status"].value_counts().sort_values(ascending=False)
        most_common_status = order_status_df.idxmax()

        return order_status_df, most_common_status

class HelperMap:
    def __init__(self, df,st):
        self.df = df
        self.st = st

    def geo_df(self):
        geo_customer_grouped = self.df.groupby('geolocation_zip_code_prefix').agg({
            'geolocation_lat': 'median',
            'geolocation_lng': 'median',
            'customer_count': 'sum',
        }).reset_index()

        return geo_customer_grouped

    def show_map(self):
        geo_data = self.geo_df()
        heatmap_data = geo_data[['geolocation_lat', 'geolocation_lng', 'customer_count']].values
        m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)  # Centered in Brazil
        HeatMap(data=heatmap_data, radius=10, blur=15, max_zoom=1).add_to(m)

        return m

