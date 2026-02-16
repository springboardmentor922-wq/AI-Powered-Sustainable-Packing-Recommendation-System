from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def train_cost_model(X_train, y_train):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_co2_model(X_train, y_train):
    model = XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model