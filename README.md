# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Platform

## Project Overview
RetailPulse is a Python-based retail analytics platform that helps businesses understand sales performance, customer behaviour, product demand, and sales trends through interactive dashboards and machine learning.

## Key Features
- **Executive Overview:** Track key business performance indicators.
- **Sales Analytics:** Analyse revenue trends and order performance.
- **Product Analytics:** Explore product-level sales performance.
- **Customer Analytics:** Understand purchasing patterns and customer value.
- **RFM Segmentation:** Group customers using Recency, Frequency, and Monetary value.
- **Demand Forecasting:** Forecast monthly sales revenue using Facebook Prophet.
- **Inventory Optimization:** Identify high-demand products and monitor product demand.
- **Geographic Analytics:** Compare sales across countries.
- **Returns & Cancellations:** Analyse cancelled transactions.
- **Interactive Dashboard:** Explore results using Streamlit.

## Technology Stack
- Python
- Pandas and NumPy
- Plotly
- Scikit-learn
- Facebook Prophet
- Streamlit
- Joblib

## Dataset
This project uses the Online Retail II dataset containing historical retail transactions from 2009–2011. The data is cleaned and transformed into processed datasets for analytics and modelling.

## How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/VijayaDharshiniS/RetailPulse_Professional.git
   ```

2. Navigate to the project folder:
   ```bash
   cd RetailPulse_Professional
   ```

3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the dashboard:
   ```bash
   python -m streamlit run app.py
   ```

## Project Status
The interactive dashboard, customer segmentation, Prophet-based sales forecasting, and inventory demand analysis have been implemented. Public deployment and further model improvements are planned.

## Disclaimer
Sales values represent revenue, not profit. Demand forecasts are estimates based on historical data and are not guaranteed future results.
