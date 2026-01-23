import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# Load dataset
DATA_PATH = os.path.join("data", "xAPI-Edu-Data.csv")
df = pd.read_csv(DATA_PATH)
print(df.columns)
exit()

# Select useful features
features = [
    'raisedhands',
    'visitedresources',
    'viewedannouncements',
    'discussion'
]

X = df[features]
y = df['Class']  # Low, Medium, High

# Encode target labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Model Accuracy:", accuracy)

# Save model & encoder
joblib.dump(model, "ml/model.pkl")
joblib.dump(label_encoder, "ml/label_encoder.pkl")

print("✅ Model trained and saved successfully")
