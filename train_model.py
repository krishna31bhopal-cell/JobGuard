import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Load dataset
data = pd.read_csv("data/job_postings.csv")

X = data["text"]
y = data["label"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2)
    )),
    ("classifier", LogisticRegression(
        max_iter=1000
    ))
])


# Train model
model.fit(X_train, y_train)


# Evaluate model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model Accuracy: {accuracy * 100:.2f}%")


# Train on complete dataset
model.fit(X, y)


# Save trained model
joblib.dump(model, "scam_model.pkl")

print("Model saved successfully as scam_model.pkl")


# Test examples
test_jobs = [
    "Earn 90000 per month from home. Pay registration fee today.",
    "Python developer required. Candidates will attend technical interview."
]

results = model.predict(test_jobs)

for job, result in zip(test_jobs, results):
    prediction = "SCAM" if result == 1 else "LEGITIMATE"
    print(f"\nJob: {job}")
    print(f"Prediction: {prediction}")