import joblib
import numpy as np

# Load saved model
model = joblib.load("ml/model.pkl")
label_encoder = joblib.load("ml/label_encoder.pkl")

def predict_user_level(raisedhands, visitedresources, viewedannouncements, discussion):
    data = np.array([[raisedhands, visitedresources, viewedannouncements, discussion]])
    prediction = model.predict(data)
    result = label_encoder.inverse_transform(prediction)
    return result[0]
