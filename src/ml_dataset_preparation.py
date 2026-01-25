import pandas as pd

# Load cleaned history dataset
history_df = pd.read_excel("data/real_packaging_history.xlsx")

# Display basic info
print("Dataset shape:", history_df.shape)
print("\nColumns:")
print(history_df.columns)



from sklearn.preprocessing import LabelEncoder

# Encode Packaging_Used
label_encoder = LabelEncoder()
history_df['Packaging_Used_Encoded'] = label_encoder.fit_transform(
    history_df['Packaging_Used']
)

# Preview encoding
print("\nPackaging encoding preview:")
print(
    history_df[['Packaging_Used', 'Packaging_Used_Encoded']]
    .drop_duplicates()
    .head()
)
