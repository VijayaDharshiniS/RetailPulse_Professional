
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "retailpulse_sales_features.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"
FORECAST_PATH = OUTPUT_DIR / "monthly_sales_forecast.csv"
CHART_PATH = OUTPUT_DIR / "monthly_sales_forecast.png"
MODEL_PATH = PROJECT_DIR / "models" / "prophet_sales_model.pkl"


def main():
    print("Loading retail sales data...")

    df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])

    # Aggregate transaction revenue by month
    df["Month"] = (
        df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    )

    monthly = (
        df.groupby("Month", as_index=False)["Sales"]
        .sum()
        .rename(columns={"Month": "ds", "Sales": "y"})
        .sort_values("ds")
    )

    print("Historical months:", len(monthly))

    if len(monthly) < 12:
        print("At least 12 monthly observations are recommended.")
        return

    # Hold out the last 3 months for evaluation
    test_size = 3
    train = monthly.iloc[:-test_size].copy()
    test = monthly.iloc[-test_size:].copy()

    print("Training months:", len(train))
    print("Testing months:", len(test))

    # Train Prophet on historical training data
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.95
    )

    model.fit(train)

    # Evaluate on held-out months
    test_future = test[["ds"]].copy()
    test_predictions = model.predict(test_future)

    mae = mean_absolute_error(
        test["y"],
        test_predictions["yhat"]
    )

    print(f"\nTest MAE: {mae:,.2f}")

    # Refit using all historical months for future forecasting
    final_model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.95
    )

    final_model.fit(monthly)

    future_dates = pd.date_range(
        start=monthly["ds"].max() + pd.offsets.MonthBegin(1),
        periods=3,
        freq="MS"
    )

    future_df = pd.DataFrame({"ds": future_dates})
    forecast = final_model.predict(future_df)

    future = forecast[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].copy()

    future = future.rename(
        columns={
            "ds": "Month",
            "yhat": "ForecastSales",
            "yhat_lower": "LowerBound",
            "yhat_upper": "UpperBound"
        }
    )

    # Revenue cannot be negative
    future["ForecastSales"] = future["ForecastSales"].clip(lower=0)
    future["LowerBound"] = future["LowerBound"].clip(lower=0)
    future["UpperBound"] = future["UpperBound"].clip(lower=0)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    future.to_csv(FORECAST_PATH, index=False)

    # Save trained model for reuse
    import joblib
    joblib.dump(final_model, MODEL_PATH)

    # Plot historical revenue and future forecast
    fig = final_model.plot(
        final_model.predict(
            final_model.make_future_dataframe(
                periods=3,
                freq="MS",
                include_history=True
            )
        )
    )

    fig.set_size_inches(11, 6)
    plt.title("RetailPulse: Prophet Monthly Sales Forecast")
    plt.xlabel("Month")
    plt.ylabel("Sales Revenue")
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=150)
    plt.close(fig)

    print("\nProphet forecasting completed!")
    print("\nNext 3 months forecast:")
    print(future.to_string(index=False))
    print(f"\nTest MAE: {mae:,.2f}")
    print("\nForecast CSV:", FORECAST_PATH)
    print("Forecast chart:", CHART_PATH)
    print("Saved model:", MODEL_PATH)
    print(
        "\nNote: This is a baseline forecast using historical revenue. "
        "The uncertainty interval is a model estimate, not a guarantee."
    )


if __name__ == "__main__":
    main()
