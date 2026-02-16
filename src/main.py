import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

from preprocessing import load_and_preprocess_data
from models import train_cost_model, train_co2_model
from evaluation import evaluate

# Load data
df = load_and_preprocess_data("../data/materials_database_600.xlsx")

# Features & Targets
X = df[['Density_kg_m3', 'Tensile_Strength_MPa', 'Category', 'Biodegradable']]
y_cost = df['Cost_per_kg']
y_co2 = df['CO2_Emission_kg']

# Train-test split
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)
_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

# Train models
cost_model = train_cost_model(X_train, y_cost_train)
co2_model = train_co2_model(X_train, y_co2_train)

# Predictions
y_cost_pred = cost_model.predict(X_test)
y_co2_pred = co2_model.predict(X_test)

# Evaluation
evaluate(y_cost_test, y_cost_pred, "Cost")
evaluate(y_co2_test, y_co2_pred, "CO2")

# Final ranking
df['Predicted_Cost'] = cost_model.predict(X)
df['Predicted_CO2'] = co2_model.predict(X)
df['Final_Rank_Score'] = (
    -df['Predicted_Cost']
    - df['Predicted_CO2']
    + df['Material_Suitability_Score']
)

recommendations = df.sort_values(by='Final_Rank_Score', ascending=False)
print(recommendations[['Material_Name', 'Predicted_Cost', 'Predicted_CO2', 'Final_Rank_Score']].head(10))

# Visualization
plt.figure(figsize=(15,4))
sns.scatterplot(x='Predicted_Cost', y='Predicted_CO2', hue='Biodegradable', data=df)
plt.title("EcoPackAI Material Trade-off: Cost vs CO2")
plt.show()

plt.figure(figsize=(15,5))
sns.histplot(df['Predicted_Cost'], bins=30, kde=True)
plt.title('Distribution of Predicted Cost')
plt.show()