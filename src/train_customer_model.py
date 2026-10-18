
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "retailpulse_customer_features.csv"
)

MODEL_PATH = PROJECT_DIR / "models" / "customer_risk_model.pkl"


def main():
    print("Loading customer dataset...")

    df = pd.read_csv(DATA_PATH)

    print("Dataset shape:", df.shape)
    print("Columns:", df.columns.tolist())

    # We need historical customer features and a target label.
    # This dataset does not contain confirmed future churn labels.
    # So this first model uses a transparent rule-based risk proxy.
    required = [
        "CustomerMonetary",
        "CustomerFrequency",
        "DaysSinceLastPurchase",
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=required).copy()

    # Create a simple, explainable risk proxy from historical behaviour.
    # These thresholds are project assumptions, not verified churn labels.
    df["RiskLabel"] = (
        (df["DaysSinceLastPurchase"] >= 180)
        & (df["CustomerFrequency"] <= 2)
    ).astype(int)

    features = [
        "CustomerMonetary",
        "CustomerFrequency",
        "DaysSinceLastPurchase",
    ]

    X = df[features]
    y = df["RiskLabel"]

    if y.nunique() < 2:
        raise ValueError(
            "Only one risk class was created. "
            "Review the thresholds and dataset values."
        )

    print("\nRisk-label distribution:")
    print(y.value_counts().rename(index={0: "Lower risk", 1: "Higher risk"}))

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nAccuracy against the rule-generated labels:")
    print(f"{accuracy_score(y_test, predictions):.3f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=["Lower risk", "Higher risk"],
            zero_division=0,
        )
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("\nModel saved to:", MODEL_PATH)
    print(
        "Note: This model reproduces rule-generated labels; "
        "it is not validated against actual future customer churn."
    )


if __name__ == "__main__":
    main()
