import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

def load_models():
    cost_model_path = os.path.join(MODEL_DIR, "cost_model.pkl")
    co2_model_path = os.path.join(MODEL_DIR, "co2_model.pkl")

    with open(cost_model_path, "rb") as cost_file:
        cost_model = pickle.load(cost_file)

    with open(co2_model_path, "rb") as co2_file:
        co2_model = pickle.load(co2_file)

    return cost_model, co2_model
