
RANDOM_STATE = 42

RF_PARAMS = {
    'n_estimators': 100,
    'max_depth': 12,
    'random_state': RANDOM_STATE,
    'n_jobs': -1 # all CPU cores
}

XGB_PARAMS = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1,
    'random_state': RANDOM_STATE,
    'n_jobs': -1
}