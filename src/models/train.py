import os
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .regressors import get_models
from .evaluate import evaluate_model

PROCESSED_CSV = os.path.join(os.getcwd(), "data", "processed", "uber_dataset.csv")
MODELS_DIR = os.path.join(os.getcwd(), "models")

def run_training():
    if not os.path.exists(PROCESSED_CSV):
        print(f"| Processed dataset not found at {PROCESSED_CSV}. Run --process first.")
        return

    print("| Loading dataset...")
    df = pd.read_csv(PROCESSED_CSV)

    # Sort Chronologically
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Features and Target
    target = 'price'
    
    # Categorical features need One-Hot Encoding
    categorical_features = ['route_name', 'ride_id', 'weather_code']
    
    # Numeric features need Scaling
    numeric_features = [
        'wait_time_minutes', 'temperature_celsius', 'precipitation_mm', 
        'hour', 'minute', 'day_of_week', 'is_weekend'
    ]

    X = df[categorical_features + numeric_features]
    y = df[target]

    # Chronological Split (80% Train, 20% Test)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"| Split Complete: {len(X_train)} Train samples | {len(X_test)} Test samples.")

    # Build Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    models = get_models()
    best_model_name = None
    best_r2 = -float('inf')

    print("\n| Initiating Training and Evaluation...\n")

    # Train, Evaluate, and Save
    for name, regressor in models.items():
        # Create a scikit-learn pipeline bundling scaling/encoding + the model
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', regressor)
        ])

        # Train
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)

        # Evaluate against paper metrics
        metrics = evaluate_model(name, y_test, y_pred)

        # Save model pipeline to disk
        file_name = name.replace(' ', '_').replace('(', '').replace(')', '').lower()
        model_path = os.path.join(MODELS_DIR, f"{file_name}.joblib")
        joblib.dump(pipeline, model_path)

        # Track the best model
        if metrics['r2'] > best_r2:
            best_r2 = metrics['r2']
            best_model_name = name

    print(f"| Training Phase Finished.")
    print(f"| Best Performing Model: {best_model_name} with R²: {best_r2:.4f}")
    print(f"| All trained pipelines saved successfully to the '/models' directory.")