import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_model(name, y_true, y_pred):
    """Calculates and prints performance metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    print(f"--- {name} ---")
    print(f"MAE:  R$ {mae:.2f}")
    print(f"RMSE: R$ {rmse:.2f}")
    print(f"R²:   {r2:.4f}\n")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}