
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="RetailPulse | Business Intelligence",
    page_icon="📊",
    layout="wide",
)

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"

st.title("📊 RetailPulse")
st.caption("Retail Business Intelligence & Analytics Platform")

# -----------------------------
# Load dashboard summaries
# -----------------------------
@st.cache_data
def load_data():
    kpis = pd.read_csv(OUTPUT_DIR / "overall_kpi_summary.csv")
    monthly = pd.read_csv(OUTPUT_DIR / "monthly_sales_summary.csv")
    countries = pd.read_csv(OUTPUT_DIR / "country_sales_summary.csv")
    products = pd.read_csv(OUTPUT_DIR / "product_sales_summary.csv")
    segments = pd.read_csv(OUTPUT_DIR / "customer_segment_summary.csv")

    return kpis, monthly, countries, products, segments


try:
    kpis, monthly, countries, products, segments = load_data()
except FileNotFoundError:
    st.error(
        "Dashboard data files are missing. "
        "Please run: python src/create_dashboard_data.py"
    )
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------

# Sidebar navigation
with st.sidebar:
    st.title("RetailPulse")
    st.caption("Business Intelligence Platform")
    st.divider()

    page = option_menu(
        menu_title="MAIN MENU",
        options=[
            "Executive Overview",
            "Sales Analytics",
            "Product Analytics",
            "Customer Analytics",
            "Customer Segmentation",
            "Geographic Analytics",
            "Order Analytics",
            "Returns & Cancellations",
            "Time Intelligence",
            "Machine Learning",
            "Business Insights",
            "Data Explorer",
            "RFM Customer Segmentation",
            "Demand Forecasting",
            "Inventory Optimization",
        ],
        icons=[
            "speedometer2",
            "graph-up-arrow",
            "box-seam",
            "people",
            "pie-chart",
            "globe",
            "receipt",
            "arrow-counterclockwise",
            "calendar3",
            "cpu",
            "lightbulb",
            "database",
            "graph-up-arrow",
            "boxes-stacked",
        ],
        menu_icon="grid",
        default_index=0,
        orientation="vertical",
    )

    st.divider()
    st.caption("RetailPulse | Analytics")
    st.sidebar.info("Data source: Online Retail II dataset")

# -----------------------------
# Overview page
# -----------------------------
if page == "Executive Overview":
    st.subheader("Business Overview")
    st.write(
        "Explore sales performance, orders, customers, "
        "products, and customer segments."
    )

    kpi = kpis.iloc[0]

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Sales",
        f"{kpi['TotalSales']:,.2f}",
    )

    col2.metric(
        "Total Orders",
        f"{int(kpi['TotalOrders']):,}",
    )

    col3.metric(
        "Unique Customers",
        f"{int(kpi['TotalCustomers']):,}",
    )

    col4.metric(
        "Products",
        f"{int(kpi['TotalProducts']):,}",
    )

    st.divider()

    # Monthly sales chart
    st.subheader("Monthly Sales Trend")

    monthly = monthly.sort_values("YearMonth")

    fig_monthly = px.line(
        monthly,
        x="YearMonth",
        y="TotalSales",
        markers=True,
        title="Sales by Month",
        labels={
            "YearMonth": "Month",
            "TotalSales": "Sales Value",
        },
    )

    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Sales Value",
        hovermode="x unified",
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

    # Country and customer segment charts
    left, right = st.columns(2)

    with left:
        st.subheader("Top 10 Countries")

        top_countries = countries.nlargest(10, "TotalSales")

        fig_country = px.bar(
            top_countries.sort_values("TotalSales"),
            x="TotalSales",
            y="Country",
            orientation="h",
            title="Countries by Sales",
            labels={"TotalSales": "Sales Value"},
        )

        st.plotly_chart(fig_country, use_container_width=True)

    with right:
        st.subheader("Customer Segments")

        fig_segments = px.pie(
            segments,
            names="CustomerSegment",
            values="TotalCustomers",
            hole=0.45,
            title="Customers by Segment",
        )

        st.plotly_chart(fig_segments, use_container_width=True)

    # Top products table
    st.subheader("Top 10 Products by Sales")

    top_products = products.nlargest(10, "TotalSales")

    st.dataframe(
        top_products[
            ["StockCode", "Description", "TotalSales", "TotalQuantity"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Note: Sales value is revenue, not profit. "
        "Customer segments are based on the current rule-based approach."
    )

# -----------------------------
# Sales Analytics Dashboard
# -----------------------------
elif page == "Sales Analytics":
    st.title("Sales Analytics")
    st.caption("Analyze revenue, orders, and sales trends.")

    # Load transaction-level sales data
    @st.cache_data
    def load_sales_data():
        file_path = (
            PROJECT_DIR
            / "data"
            / "processed"
            / "retailpulse_sales_features.csv"
        )

        df = pd.read_csv(file_path, parse_dates=["InvoiceDate"])
        df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
        return df

    try:
        sales_data = load_sales_data()
    except FileNotFoundError:
        st.error("Sales dataset not found. Check the processed data folder.")
        st.stop()

    # Sidebar filters
    st.subheader("Filters")

    countries_list = sorted(sales_data["Country"].dropna().unique())

    selected_countries = st.multiselect(
        "Select countries",
        options=countries_list,
        default=["United Kingdom"] if "United Kingdom" in countries_list else [],
    )

    available_months = sorted(sales_data["YearMonth"].unique())

    selected_months = st.multiselect(
        "Select months",
        options=available_months,
        default=available_months,
    )

    filtered_sales = sales_data.copy()

    if selected_countries:
        filtered_sales = filtered_sales[
            filtered_sales["Country"].isin(selected_countries)
        ]
    else:
        filtered_sales = filtered_sales.iloc[0:0]

    if selected_months:
        filtered_sales = filtered_sales[
            filtered_sales["YearMonth"].isin(selected_months)
        ]
    else:
        filtered_sales = filtered_sales.iloc[0:0]

    # Sales KPIs
    total_sales = filtered_sales["Sales"].sum()
    total_orders = filtered_sales["Invoice"].nunique()
    total_quantity = filtered_sales["Quantity"].sum()
    total_customers = filtered_sales["Customer ID"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"{total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Quantity Sold", f"{total_quantity:,}")
    col4.metric("Customers", f"{total_customers:,}")

    st.divider()

    # Monthly sales chart
    st.subheader("Monthly Sales Trend")

    monthly_summary = (
        filtered_sales.groupby("YearMonth", as_index=False)
        .agg(
            TotalSales=("Sales", "sum"),
            TotalOrders=("Invoice", "nunique"),
        )
        .sort_values("YearMonth")
    )

    if not monthly_summary.empty:
        fig_sales = px.line(
            monthly_summary,
            x="YearMonth",
            y="TotalSales",
            markers=True,
            title="Monthly Revenue",
            labels={
                "YearMonth": "Month",
                "TotalSales": "Sales Revenue",
            },
        )
        st.plotly_chart(fig_sales, use_container_width=True)

        fig_orders = px.bar(
            monthly_summary,
            x="YearMonth",
            y="TotalOrders",
            title="Monthly Orders",
            labels={
                "YearMonth": "Month",
                "TotalOrders": "Orders",
            },
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    else:
        st.warning("No sales found for the selected filters.")

    # Country summary
    st.subheader("Sales Summary by Country")

    if not filtered_sales.empty:
        country_summary = (
            filtered_sales.groupby("Country", as_index=False)
            .agg(
                TotalSales=("Sales", "sum"),
                TotalOrders=("Invoice", "nunique"),
                TotalQuantity=("Quantity", "sum"),
            )
            .sort_values("TotalSales", ascending=False)
        )

        st.dataframe(
            country_summary,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Sales represent transaction revenue, not profit. "
        "Results update according to the selected filters."
    )

# -----------------------------
# Product Analytics Dashboard
# -----------------------------

# -----------------------------
# Product Analytics Dashboard
# -----------------------------
elif page == "Product Analytics":
    st.title("Product Analytics")
    st.caption("Explore product revenue and identify top-performing products.")

    @st.cache_data
    def load_product_data():
        file_path = OUTPUT_DIR / "product_sales_summary.csv"
        return pd.read_csv(file_path)

    try:
        product_data = load_product_data()
    except FileNotFoundError:
        st.error("Product summary file not found in the outputs folder.")
        st.stop()

    # Detect columns in the summary file
    columns = product_data.columns.tolist()

    product_col = next(
        (c for c in columns if c.lower() in
         ["description", "product", "productname", "product_name"]),
        None,
    )
    sales_col = next(
        (c for c in columns if "sales" in c.lower() or "revenue" in c.lower()),
        None,
    )

    if product_col is None or sales_col is None:
        st.warning("Could not automatically identify product and sales columns.")
        st.write("Available columns:", columns)
        st.dataframe(product_data, use_container_width=True, hide_index=True)
    else:
        product_data[sales_col] = pd.to_numeric(
            product_data[sales_col], errors="coerce"
        ).fillna(0)

        product_data = product_data.sort_values(
            sales_col, ascending=False
        )

        st.subheader("Product Performance Overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("Products", f"{product_data[product_col].nunique():,}")
        col2.metric("Total Product Revenue", f"{product_data[sales_col].sum():,.2f}")
        col3.metric("Top Product Revenue", f"{product_data[sales_col].max():,.2f}")

        st.divider()

        top_n = st.slider(
            "Number of top products to display",
            min_value=5,
            max_value=30,
            value=10,
            step=5,
        )

        top_products = product_data.head(top_n)

        st.subheader(f"Top {top_n} Products by Revenue")

        fig = px.bar(
            top_products.sort_values(sales_col),
            x=sales_col,
            y=product_col,
            orientation="h",
            title="Highest-Revenue Products",
            labels={
                sales_col: "Sales Revenue",
                product_col: "Product",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Product Sales Table")
        st.dataframe(
            top_products,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Revenue is calculated from transaction sales; it is not profit."
        )

# -----------------------------
# Customer Analytics Dashboard
# -----------------------------
elif page == "Customer Analytics":
    st.title("Customer Analytics")
    st.caption("Understand customer spending and purchasing behaviour.")

    @st.cache_data
    def load_customer_data():
        file_path = (
            PROJECT_DIR
            / "data"
            / "processed"
            / "retailpulse_customer_features.csv"
        )
        return pd.read_csv(file_path)

    try:
        customer_data = load_customer_data()
    except FileNotFoundError:
        st.error("Customer features file not found.")
        st.stop()

    st.subheader("Customer Overview")

    customer_col = "Customer ID"
    monetary_col = "CustomerMonetary"
    frequency_col = "CustomerFrequency"

    required_cols = [customer_col, monetary_col, frequency_col]

    if not all(col in customer_data.columns for col in required_cols):
        st.error("Required customer columns are missing.")
        st.write("Available columns:", customer_data.columns.tolist())
    else:
        customer_data[monetary_col] = pd.to_numeric(
            customer_data[monetary_col], errors="coerce"
        ).fillna(0)

        customer_data[frequency_col] = pd.to_numeric(
            customer_data[frequency_col], errors="coerce"
        ).fillna(0)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Customers",
            f"{customer_data[customer_col].nunique():,}",
        )
        col2.metric(
            "Total Customer Revenue",
            f"{customer_data[monetary_col].sum():,.2f}",
        )
        col3.metric(
            "Average Customer Revenue",
            f"{customer_data[monetary_col].mean():,.2f}",
        )

        st.divider()

        st.subheader("Top Customers by Revenue")

        top_n = st.slider(
            "Number of customers to display",
            min_value=5,
            max_value=30,
            value=10,
            step=5,
        )

        top_customers = customer_data.sort_values(
            monetary_col, ascending=False
        ).head(top_n)

        fig = px.bar(
            top_customers,
            x=customer_col,
            y=monetary_col,
            title="Top Customers by Revenue",
            labels={
                customer_col: "Customer ID",
                monetary_col: "Customer Revenue",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Purchase Frequency Distribution")

        fig_frequency = px.histogram(
            customer_data,
            x=frequency_col,
            nbins=30,
            title="Customer Purchase Frequency",
            labels={frequency_col: "Purchase Frequency"},
        )
        st.plotly_chart(fig_frequency, use_container_width=True)

        st.subheader("Customer Details")

        st.dataframe(
            top_customers,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Customer revenue represents recorded sales, not profit. "
            "Customer frequency is based on the prepared dataset's definition."
        )

# -----------------------------
# Customer Segmentation Dashboard
# -----------------------------
elif page == "Customer Segmentation":
    st.title("Customer Segmentation")
    st.caption("Explore customer groups and their spending behaviour.")

    @st.cache_data
    def load_segmentation_data():
        file_path = OUTPUT_DIR / "customer_segment_summary.csv"
        return pd.read_csv(file_path)

    try:
        segment_data = load_segmentation_data()
    except FileNotFoundError:
        st.error("Customer segment summary file not found.")
        st.stop()

    st.subheader("Customer Segment Overview")

    st.write("Available columns:", segment_data.columns.tolist())

    segment_col = next(
        (
            c for c in segment_data.columns
            if "segment" in c.lower()
        ),
        None,
    )

    count_col = next(
        (
            c for c in segment_data.columns
            if "customer" in c.lower() and
            ("count" in c.lower() or "number" in c.lower())
        ),
        None,
    )

    if segment_col is None:
        st.warning("Could not identify the customer segment column.")
        st.dataframe(segment_data, use_container_width=True)
    else:
        st.subheader("Customer Groups")

        if count_col:
            total_customers = segment_data[count_col].sum()
            st.metric("Customers Across Segments", f"{total_customers:,.0f}")

            fig = px.pie(
                segment_data,
                names=segment_col,
                values=count_col,
                title="Customer Distribution by Segment",
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)

            fig_bar = px.bar(
                segment_data,
                x=segment_col,
                y=count_col,
                title="Customers in Each Segment",
                labels={
                    segment_col: "Customer Segment",
                    count_col: "Number of Customers",
                },
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info(
                "The customer count column was not detected automatically. "
                "Check the available columns below."
            )

        st.subheader("Segment Summary")
        st.dataframe(
            segment_data,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Segments are rule-based categories, not machine-learning churn predictions."
    )

# -----------------------------
# Geographic Analytics Dashboard
# -----------------------------
elif page == "Geographic Analytics":
    st.title("Geographic Analytics")
    st.caption("Analyze sales performance across countries.")

    @st.cache_data
    def load_country_data():
        file_path = OUTPUT_DIR / "country_sales_summary.csv"
        return pd.read_csv(file_path)

    try:
        country_data = load_country_data()
    except FileNotFoundError:
        st.error("Country sales summary file not found.")
        st.stop()

    # Detect relevant columns
    columns = country_data.columns.tolist()

    country_col = next(
        (c for c in columns if c.lower() == "country"),
        None,
    )
    sales_col = next(
        (c for c in columns if "sales" in c.lower() or "revenue" in c.lower()),
        None,
    )
    orders_col = next(
        (c for c in columns if "order" in c.lower()),
        None,
    )

    if country_col is None or sales_col is None:
        st.error("Could not identify country and sales columns.")
        st.write("Available columns:", columns)
        st.dataframe(country_data, use_container_width=True)
    else:
        country_data[sales_col] = pd.to_numeric(
            country_data[sales_col], errors="coerce"
        ).fillna(0)

        country_data = country_data.sort_values(
            sales_col, ascending=False
        )

        st.subheader("Geographic Performance Overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("Countries", f"{country_data[country_col].nunique():,}")
        col2.metric("Total Sales", f"{country_data[sales_col].sum():,.2f}")
        col3.metric("Leading Country", str(country_data.iloc[0][country_col]))

        if orders_col:
            st.caption(
                "Order counts are shown using the order metric available "
                "in the country summary."
            )

        st.divider()

        top_n = st.slider(
            "Number of top countries",
            min_value=5,
            max_value=min(30, len(country_data)),
            value=min(10, len(country_data)),
        )

        top_countries = country_data.head(top_n)

        st.subheader(f"Top {top_n} Countries by Sales")

        fig = px.bar(
            top_countries.sort_values(sales_col),
            x=sales_col,
            y=country_col,
            orientation="h",
            title="Country Sales Comparison",
            labels={
                sales_col: "Sales Revenue",
                country_col: "Country",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Country Sales Share")

        fig_pie = px.pie(
            top_countries,
            names=country_col,
            values=sales_col,
            title=f"Sales Distribution — Top {top_n} Countries",
            hole=0.4,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Country Sales Table")
        st.dataframe(
            country_data,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Sales represent revenue, not profit. "
        "Country comparisons use the prepared country summary."
    )

# -----------------------------
# Order Analytics Dashboard
# -----------------------------
elif page == "Order Analytics":
    st.title("Order Analytics")
    st.caption("Explore order value, quantity, and purchasing patterns.")

    @st.cache_data
    def load_order_data():
        file_path = (
            PROJECT_DIR
            / "data"
            / "processed"
            / "retailpulse_sales_features.csv"
        )
        df = pd.read_csv(file_path, parse_dates=["InvoiceDate"])
        return df

    try:
        order_data = load_order_data()
    except FileNotFoundError:
        st.error("Sales features dataset not found.")
        st.stop()

    required_cols = ["Invoice", "Sales", "Quantity", "InvoiceDate"]

    if not all(col in order_data.columns for col in required_cols):
        st.error("Required order columns are missing.")
        st.write("Available columns:", order_data.columns.tolist())
    else:
        order_summary = (
            order_data.groupby("Invoice", as_index=False)
            .agg(
                OrderValue=("Sales", "sum"),
                TotalQuantity=("Quantity", "sum"),
                OrderDate=("InvoiceDate", "min"),
                Items=("StockCode", "count"),
            )
            .sort_values("OrderValue", ascending=False)
        )

        st.subheader("Order Overview")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Orders", f"{len(order_summary):,}")
        col2.metric(
            "Total Revenue",
            f"{order_summary['OrderValue'].sum():,.2f}",
        )
        col3.metric(
            "Average Order Value",
            f"{order_summary['OrderValue'].mean():,.2f}",
        )
        col4.metric(
            "Average Items per Order",
            f"{order_summary['Items'].mean():,.1f}",
        )

        st.divider()

        st.subheader("Order Value Distribution")

        fig_hist = px.histogram(
            order_summary,
            x="OrderValue",
            nbins=40,
            title="How Order Values Are Distributed",
            labels={"OrderValue": "Order Revenue"},
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("Top Orders by Revenue")

        top_n = st.slider(
            "Number of top orders",
            min_value=5,
            max_value=30,
            value=10,
            step=5,
        )

        top_orders = order_summary.head(top_n)

        fig_bar = px.bar(
            top_orders,
            x="Invoice",
            y="OrderValue",
            title="Highest-Value Orders",
            labels={
                "Invoice": "Invoice Number",
                "OrderValue": "Order Revenue",
            },
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Order Details")
        st.dataframe(
            top_orders,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Order metrics are calculated from the prepared valid-sales dataset. "
        "Revenue is not profit."
    )

# -----------------------------
# Returns & Cancellations Dashboard
# -----------------------------
elif page == "Returns & Cancellations":
    st.title("Returns & Cancellations")
    st.caption("Monitor cancelled transactions and returned quantities.")

    @st.cache_data
    def load_transaction_data():
        file_path = (
            PROJECT_DIR
            / "data"
            / "processed"
            / "retailpulse_enriched.csv"
        )
        df = pd.read_csv(file_path, parse_dates=["InvoiceDate"])
        return df

    try:
        transaction_data = load_transaction_data()
    except FileNotFoundError:
        st.error("Enriched transaction dataset not found.")
        st.stop()

    required_cols = ["Invoice", "Quantity", "Price", "IsCancelled"]

    if not all(col in transaction_data.columns for col in required_cols):
        st.error("Required cancellation columns are missing.")
        st.write("Available columns:", transaction_data.columns.tolist())
    else:
        transaction_data["Sales"] = (
            transaction_data["Quantity"] * transaction_data["Price"]
        )

        cancelled_data = transaction_data[
            transaction_data["IsCancelled"].astype(str).str.lower().isin(
                ["true", "1"]
            )
        ].copy()

        total_transactions = len(transaction_data)
        cancelled_transactions = len(cancelled_data)
        cancellation_rate = (
            cancelled_transactions / total_transactions * 100
            if total_transactions else 0
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Cancelled Lines", f"{cancelled_transactions:,}")
        col2.metric("Cancellation Line Rate", f"{cancellation_rate:.2f}%")
        col3.metric(
            "Cancelled Invoice Count",
            f"{cancelled_data['Invoice'].nunique():,}",
        )

        st.divider()

        st.subheader("Cancellation Trend by Month")

        if not cancelled_data.empty:
            cancelled_data["YearMonth"] = (
                cancelled_data["InvoiceDate"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_cancelled = (
                cancelled_data.groupby("YearMonth", as_index=False)
                .agg(
                    CancelledLines=("Invoice", "size"),
                    CancelledInvoices=("Invoice", "nunique"),
                )
                .sort_values("YearMonth")
            )

            fig = px.line(
                monthly_cancelled,
                x="YearMonth",
                y="CancelledLines",
                markers=True,
                title="Cancelled Transaction Lines by Month",
                labels={
                    "YearMonth": "Month",
                    "CancelledLines": "Cancelled Lines",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Cancellation Records")

            st.dataframe(
                cancelled_data[
                    [
                        "Invoice",
                        "InvoiceDate",
                        "Description",
                        "Quantity",
                        "Price",
                        "Sales",
                        "Country",
                    ]
                ].head(1000),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No cancelled records were found.")

        st.caption(
            "The cancellation rate above is based on transaction lines, "
            "not unique orders. Negative quantities and cancellation "
            "records are not necessarily equivalent to confirmed refunds."
        )

# -----------------------------
# Time Intelligence Dashboard
# -----------------------------
elif page == "Time Intelligence":
    st.title("Time Intelligence")
    st.caption("Analyze monthly, quarterly, and yearly sales trends.")

    @st.cache_data
    def load_time_data():
        file_path = (
            PROJECT_DIR
            / "data"
            / "processed"
            / "retailpulse_sales_features.csv"
        )
        return pd.read_csv(file_path, parse_dates=["InvoiceDate"])

    try:
        time_data = load_time_data()
    except FileNotFoundError:
        st.error("Sales features dataset not found.")
        st.stop()

    required_cols = ["InvoiceDate", "Sales", "Invoice"]

    if not all(col in time_data.columns for col in required_cols):
        st.error("Required date and sales columns are missing.")
        st.write("Available columns:", time_data.columns.tolist())
    else:
        time_data["Sales"] = pd.to_numeric(
            time_data["Sales"], errors="coerce"
        ).fillna(0)

        time_data["Year"] = time_data["InvoiceDate"].dt.year
        time_data["Quarter"] = (
            time_data["InvoiceDate"].dt.to_period("Q").astype(str)
        )
        time_data["YearMonth"] = (
            time_data["InvoiceDate"].dt.to_period("M").astype(str)
        )

        st.subheader("Choose Time Period")

        period_type = st.selectbox(
            "Group sales by",
            ["Monthly", "Quarterly", "Yearly"],
        )

        if period_type == "Monthly":
            period_col = "YearMonth"
        elif period_type == "Quarterly":
            period_col = "Quarter"
        else:
            period_col = "Year"

        time_summary = (
            time_data.groupby(period_col, as_index=False)
            .agg(
                TotalSales=("Sales", "sum"),
                TotalOrders=("Invoice", "nunique"),
            )
            .sort_values(period_col)
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"{time_data['Sales'].sum():,.2f}")
        col2.metric("Periods", f"{len(time_summary):,}")
        col3.metric(
            "Average Revenue per Period",
            f"{time_summary['TotalSales'].mean():,.2f}",
        )

        st.divider()

        st.subheader(f"{period_type} Sales Trend")

        fig_sales = px.line(
            time_summary,
            x=period_col,
            y="TotalSales",
            markers=True,
            title=f"{period_type} Revenue Trend",
            labels={
                period_col: "Time Period",
                "TotalSales": "Sales Revenue",
            },
        )
        st.plotly_chart(fig_sales, use_container_width=True)

        st.subheader(f"{period_type} Order Trend")

        fig_orders = px.bar(
            time_summary,
            x=period_col,
            y="TotalOrders",
            title=f"{period_type} Order Count",
            labels={
                period_col: "Time Period",
                "TotalOrders": "Orders",
            },
        )
        st.plotly_chart(fig_orders, use_container_width=True)

        st.subheader("Time Summary Table")
        st.dataframe(
            time_summary,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Revenue is transaction sales, not profit. "
        "Quarterly and yearly values are grouped using calendar periods."
    )

# -----------------------------
# Machine Learning Dashboard
# -----------------------------
elif page == "Machine Learning":
    import joblib

    st.title("Machine Learning")
    st.caption("Explore customer risk classification using historical behaviour.")

    MODEL_PATH = PROJECT_DIR / "models" / "customer_risk_model.pkl"
    CUSTOMER_PATH = (
        PROJECT_DIR
        / "data"
        / "processed"
        / "retailpulse_customer_features.csv"
    )

    if not MODEL_PATH.exists():
        st.warning("Customer model not found. Train the model first.")
        st.code("python src/train_customer_model.py")
        st.stop()

    if not CUSTOMER_PATH.exists():
        st.error("Customer features dataset not found.")
        st.stop()

    @st.cache_resource
    def load_customer_risk_model(model_path):
        return joblib.load(model_path)

    @st.cache_data
    def load_ml_customers(file_path):
        return pd.read_csv(file_path)

    model = load_customer_risk_model(str(MODEL_PATH))
    ml_customers = load_ml_customers(str(CUSTOMER_PATH))

    required_features = [
        "CustomerMonetary",
        "CustomerFrequency",
        "DaysSinceLastPurchase",
    ]

    if not all(col in ml_customers.columns for col in required_features):
        st.error("Required customer features are missing.")
        st.stop()

    ml_customers = ml_customers.dropna(
        subset=required_features
    ).copy()

    ml_customers["RiskPrediction"] = model.predict(
        ml_customers[required_features]
    )

    ml_customers["RiskCategory"] = ml_customers[
        "RiskPrediction"
    ].map({
        0: "Lower Risk",
        1: "Higher Risk",
    })

    st.subheader("Customer Risk Overview")

    total_customers = len(ml_customers)
    higher_risk = int((ml_customers["RiskPrediction"] == 1).sum())
    lower_risk = total_customers - higher_risk
    risk_percentage = (
        higher_risk / total_customers * 100
        if total_customers else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Customers Analysed", f"{total_customers:,}")
    col2.metric("Higher-Risk Rule Matches", f"{higher_risk:,}")
    col3.metric("Higher-Risk Share", f"{risk_percentage:.1f}%")

    st.divider()

    st.subheader("Risk Group Distribution")

    risk_summary = (
        ml_customers["RiskCategory"]
        .value_counts()
        .rename_axis("Risk Category")
        .reset_index(name="Customers")
    )

    fig = px.pie(
        risk_summary,
        names="Risk Category",
        values="Customers",
        title="Customer Risk Classification",
        hole=0.4,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Explore Customer Risk")

    risk_filter = st.selectbox(
        "Select risk group",
        ["All Customers", "Higher Risk", "Lower Risk"],
    )

    displayed_customers = ml_customers.copy()

    if risk_filter != "All Customers":
        displayed_customers = displayed_customers[
            displayed_customers["RiskCategory"] == risk_filter
        ]

    display_columns = [
        "Customer ID",
        "CustomerMonetary",
        "CustomerFrequency",
        "DaysSinceLastPurchase",
        "RiskCategory",
    ]

    st.dataframe(
        displayed_customers[display_columns].sort_values(
            "DaysSinceLastPurchase",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "This is a rule-based risk classification model, not a validated "
        "future-churn predictor. Higher risk means the historical rule "
        "matched: at least 180 days since last purchase and no more than "
        "2 purchases. It does not establish that a customer will churn."
    )

# -----------------------------
# Business Insights Dashboard
# -----------------------------
elif page == "Business Insights":
    st.title("Business Insights")
    st.caption("Discover key findings and actionable business observations.")

    @st.cache_data
    def load_business_insights():
        monthly_path = OUTPUT_DIR / "monthly_sales_summary.csv"
        country_path = OUTPUT_DIR / "country_sales_summary.csv"
        product_path = OUTPUT_DIR / "product_sales_summary.csv"
        segment_path = OUTPUT_DIR / "customer_segment_summary.csv"

        monthly = pd.read_csv(monthly_path)
        countries = pd.read_csv(country_path)
        products = pd.read_csv(product_path)
        segments = pd.read_csv(segment_path)

        return monthly, countries, products, segments

    try:
        monthly, countries, products, segments = load_business_insights()
    except FileNotFoundError as error:
        st.error(f"Required summary file not found: {error}")
        st.stop()

    # Detect columns automatically
    def find_column(data, possible_names):
        for col in data.columns:
            if col.lower() in possible_names:
                return col
        return None

    sales_col = next(
        (c for c in monthly.columns
         if "sales" in c.lower() or "revenue" in c.lower()),
        None,
    )
    country_col = find_column(countries, {"country"})
    country_sales_col = next(
        (c for c in countries.columns
         if "sales" in c.lower() or "revenue" in c.lower()),
        None,
    )
    product_sales_col = next(
        (c for c in products.columns
         if "sales" in c.lower() or "revenue" in c.lower()),
        None,
    )

    st.subheader("Key Business Findings")

    if sales_col and not monthly.empty:
        monthly[sales_col] = pd.to_numeric(
            monthly[sales_col], errors="coerce"
        ).fillna(0)

        best_month = monthly.loc[monthly[sales_col].idxmax()]
        col1, col2 = st.columns(2)

        col1.metric(
            "Highest-Revenue Period",
            str(best_month.iloc[0]),
        )
        col2.metric(
            "Highest Period Revenue",
            f"{best_month[sales_col]:,.2f}",
        )

        st.info(
            f"The highest recorded revenue period in the monthly summary "
            f"is {best_month.iloc[0]}, with revenue of "
            f"{best_month[sales_col]:,.2f}."
        )

    if (
        country_col
        and country_sales_col
        and not countries.empty
    ):
        countries[country_sales_col] = pd.to_numeric(
            countries[country_sales_col], errors="coerce"
        ).fillna(0)

        leading_country = countries.loc[
            countries[country_sales_col].idxmax()
        ]

        st.success(
            f"Leading country by recorded revenue: "
            f"{leading_country[country_col]} "
            f"({leading_country[country_sales_col]:,.2f})."
        )

    if product_sales_col and not products.empty:
        products[product_sales_col] = pd.to_numeric(
            products[product_sales_col], errors="coerce"
        ).fillna(0)

        best_product = products.loc[
            products[product_sales_col].idxmax()
        ]

        st.info(
            f"Highest-revenue product: {best_product.iloc[0]} "
            f"with recorded revenue of {best_product[product_sales_col]:,.2f}."
        )

    st.divider()

    st.subheader("Monthly Revenue Overview")

    if sales_col and not monthly.empty:
        fig = px.line(
            monthly,
            x=monthly.columns[0],
            y=sales_col,
            markers=True,
            title="Revenue Changes Over Time",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Country Performance")

    if country_col and country_sales_col and not countries.empty:
        top_countries = countries.sort_values(
            country_sales_col, ascending=False
        ).head(10)

        fig_country = px.bar(
            top_countries,
            x=country_sales_col,
            y=country_col,
            orientation="h",
            title="Top 10 Countries by Revenue",
        )
        st.plotly_chart(fig_country, use_container_width=True)

    st.subheader("Customer Segment Summary")
    st.dataframe(
        segments,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "These are descriptive insights from historical data. "
        "Revenue is not profit, and historical trends do not guarantee "
        "future performance."
    )

# -----------------------------
# Data Explorer Dashboard
# -----------------------------
elif page == "Data Explorer":
    st.title("Data Explorer")
    st.caption("Search, filter, inspect, and download retail transaction data.")

    @st.cache_data
    def load_explorer_data():
        file_path = (
            PROJECT_DIR
            / "data"
            / "processed"
            / "retailpulse_enriched.csv"
        )
        return pd.read_csv(file_path)

    try:
        explorer_data = load_explorer_data()
    except FileNotFoundError:
        st.error("Enriched retail dataset not found.")
        st.stop()

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", f"{len(explorer_data):,}")
    col2.metric("Total Columns", f"{len(explorer_data.columns):,}")
    col3.metric(
        "Missing Values",
        f"{int(explorer_data.isna().sum().sum()):,}",
    )

    st.divider()

    st.subheader("Filter Transactions")

    filtered_data = explorer_data.copy()

    if "Country" in filtered_data.columns:
        country_options = sorted(
            filtered_data["Country"].dropna().unique().tolist()
        )
        selected_countries = st.multiselect(
            "Select countries",
            options=country_options,
            default=[],
            placeholder="Choose one or more countries",
        )

        if selected_countries:
            filtered_data = filtered_data[
                filtered_data["Country"].isin(selected_countries)
            ]

    if "Description" in filtered_data.columns:
        search_text = st.text_input(
            "Search product description",
            placeholder="Enter a product keyword",
        )

        if search_text.strip():
            filtered_data = filtered_data[
                filtered_data["Description"]
                .fillna("")
                .str.contains(search_text, case=False, regex=False)
            ]

    if "InvoiceDate" in filtered_data.columns:
        date_values = pd.to_datetime(
            filtered_data["InvoiceDate"], errors="coerce"
        )
        valid_dates = date_values.dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            date_range = st.date_input(
                "Invoice date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range
                filtered_data = filtered_data[
                    date_values.dt.date.between(start_date, end_date)
                ]

    st.subheader("Filtered Transaction Records")
    st.write(f"Showing **{len(filtered_data):,}** rows")

    preview_rows = st.slider(
        "Number of rows to preview",
        min_value=10,
        max_value=100,
        value=20,
        step=10,
    )

    st.dataframe(
        filtered_data.head(preview_rows),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered data as CSV",
        data=csv_data,
        file_name="retailpulse_filtered_data.csv",
        mime="text/csv",
    )

    st.subheader("Data Quality Summary")

    missing_summary = (
        explorer_data.isna()
        .sum()
        .reset_index()
    )
    missing_summary.columns = ["Column", "Missing Values"]

    st.dataframe(
        missing_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Filtering and downloading do not modify your original dataset. "
        "The table previews a limited number of rows for easier browsing."
    )

elif page == "RFM Customer Segmentation":
    st.title("RFM Customer Segmentation")
    st.write(
        "Analyse customers using Recency, Frequency, and Monetary value."
    )

    rfm_path = (
        PROJECT_DIR
        / "data"
        / "processed"
        / "retailpulse_rfm_analysis.csv"
    )

    if rfm_path.exists():
        rfm = pd.read_csv(rfm_path)

        # KPI metrics
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Customers", f"{len(rfm):,}")
        col2.metric(
            "Average Recency",
            f"{rfm['Recency'].mean():.0f} days"
        )
        col3.metric(
            "Average Customer Spend",
            f"{rfm['Monetary'].mean():,.2f}"
        )

        st.subheader("Customer Distribution")

        segment_counts = (
            rfm["RFM_Segment"]
            .value_counts()
            .reset_index()
        )
        segment_counts.columns = ["Segment", "Customers"]

        fig = px.bar(
            segment_counts,
            x="Segment",
            y="Customers",
            color="Segment",
            title="Customers by RFM Segment",
            text="Customers"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Search and Filter Customers")

        selected_segment = st.selectbox(
            "Choose Customer Segment",
            ["All"] + sorted(rfm["RFM_Segment"].unique().tolist())
        )

        if selected_segment != "All":
            filtered_rfm = rfm[
                rfm["RFM_Segment"] == selected_segment
            ]
        else:
            filtered_rfm = rfm

        st.dataframe(
            filtered_rfm,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download RFM Report",
            data=filtered_rfm.to_csv(index=False).encode("utf-8"),
            file_name="retailpulse_rfm_report.csv",
            mime="text/csv"
        )

    else:
        st.error("RFM file not found. Please run src/rfm_analysis.py.")

elif page == "Demand Forecasting":
    st.title("Demand Forecasting")
    st.write(
        "View historical monthly sales and the next three months' forecast."
    )

    forecast_path = (
        PROJECT_DIR
        / "outputs"
        / "monthly_sales_forecast.csv"
    )

    chart_path = (
        PROJECT_DIR
        / "outputs"
        / "monthly_sales_forecast.png"
    )

    if forecast_path.exists():
        forecast = pd.read_csv(forecast_path)
        forecast["Month"] = pd.to_datetime(forecast["Month"])

        col1, col2 = st.columns(2)

        col1.metric(
            "Forecast Period",
            f"{len(forecast)} months"
        )

        col2.metric(
            "Average Forecast Sales",
            f"{forecast['ForecastSales'].mean():,.2f}"
        )

        st.subheader("Forecast Results")

        st.dataframe(
            forecast,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Monthly Sales Forecast")

        if chart_path.exists():
            st.image(
                str(chart_path),
                caption="Historical sales and forecast"
            )
        else:
            fig = px.bar(
                forecast,
                x="Month",
                y="ForecastSales",
                title="Forecast Sales by Month"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "Download Forecast CSV",
            data=forecast.to_csv(index=False).encode("utf-8"),
            file_name="monthly_sales_forecast.csv",
            mime="text/csv"
        )

        st.caption(
            "These are baseline model estimates from historical data, "
            "not guaranteed future sales. Sales represent revenue, "
            "not profit."
        )

    else:
        st.warning(
            "Forecast file not found. Run "
            "'python src/demand_forecasting.py' first."
        )

elif page == "Inventory Optimization":
    st.title("Inventory Optimization")
    st.write(
        "Explore product demand and sales-based inventory planning recommendations."
    )

    inventory_path = (
        PROJECT_DIR
        / "outputs"
        / "inventory_recommendations.csv"
    )

    if inventory_path.exists():
        inventory = pd.read_csv(inventory_path)

        col1, col2, col3 = st.columns(3)

        col1.metric("Products Analysed", f"{len(inventory):,}")
        col2.metric(
            "High-Demand Products",
            f"{(inventory['InventoryPriority'] == 'High Demand').sum():,}"
        )
        col3.metric(
            "Monitor-Demand Products",
            f"{(inventory['InventoryPriority'] == 'Monitor Demand').sum():,}"
        )

        st.subheader("Product Demand Priorities")

        priority_counts = (
            inventory["InventoryPriority"]
            .value_counts()
            .rename_axis("Priority")
            .reset_index(name="Products")
        )

        fig = px.bar(
            priority_counts,
            x="Priority",
            y="Products",
            color="Priority",
            text="Products",
            title="Products by Demand Priority"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Find Products")

        search_text = st.text_input(
            "Search by product code or description"
        )

        selected_priority = st.selectbox(
            "Filter by priority",
            [
                "All",
                "High Demand",
                "Monitor Demand",
                "Lower Demand"
            ]
        )

        filtered = inventory.copy()

        if selected_priority != "All":
            filtered = filtered[
                filtered["InventoryPriority"] == selected_priority
            ]

        if search_text.strip():
            search = search_text.strip().lower()
            filtered = filtered[
                filtered["StockCode"].astype(str).str.lower().str.contains(
                    search, na=False
                )
                | filtered["ProductDescription"].astype(str).str.lower().str.contains(
                    search, na=False
                )
            ]

        display_columns = [
            "StockCode",
            "ProductDescription",
            "TotalUnitsSold",
            "TotalOrders",
            "TotalRevenue",
            "AverageMonthlyUnits",
            "InventoryPriority",
        ]

        st.dataframe(
            filtered[display_columns],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Inventory Recommendations",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="inventory_recommendations.csv",
            mime="text/csv"
        )

        st.caption(
            "Recommendations use historical sales data. "
            "Actual stock quantities, stockouts, and reorder levels "
            "cannot be determined without inventory and supplier data."
        )

    else:
        st.warning(
            "Inventory file not found. Run "
            "'python src/inventory_optimization.py' first."
        )
