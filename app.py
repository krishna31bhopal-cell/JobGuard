from flask import Flask, render_template, request, jsonify
import joblib
import re
import sqlite3
from datetime import datetime


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# LOAD MACHINE LEARNING MODEL
# ==========================================

model = joblib.load("scam_model.pkl")


# ==========================================
# DATABASE
# ==========================================

def init_db():
    conn = sqlite3.connect("jobguard.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            analyzed_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# SCAM INDICATORS
# ==========================================

SCAM_PATTERNS = {

    "Payment requested": [
        r"registration fee",
        r"joining fee",
        r"processing fee",
        r"security deposit",
        r"pay.*fee",
        r"deposit.*money",
        r"send.*money"
    ],

    "Unrealistic income": [
        r"earn.*\d+.*per month",
        r"earn.*\d+.*daily",
        r"guaranteed.*income",
        r"guaranteed.*salary",
        r"make money easily"
    ],

    "Urgency": [
        r"immediately",
        r"urgent",
        r"limited seats",
        r"act now",
        r"today only"
    ],

    "No interview": [
        r"no interview",
        r"without interview",
        r"no experience required"
    ],

    "Sensitive information": [
        r"bank account",
        r"bank details",
        r"aadhaar",
        r"password",
        r"otp"
    ]
}


# ==========================================
# DETECT SCAM INDICATORS
# ==========================================

def detect_scam_indicators(text):

    text_lower = text.lower()

    indicators = []
    matched_phrases = []

    for category, patterns in SCAM_PATTERNS.items():

        for pattern in patterns:

            match = re.search(pattern, text_lower)

            if match:
                indicators.append(category)
                matched_phrases.append(match.group())
                break

    return indicators, matched_phrases


# ==========================================
# CALCULATE RISK SCORE
# ==========================================

def calculate_risk(prediction_probability, indicators):

    # Convert ML probability to percentage
    score = int(prediction_probability * 100)

    # Add extra risk for rule-based indicators
    score += len(indicators) * 5

    # Keep score between 0 and 100
    score = min(score, 100)

    return score


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# ANALYZE JOB POSTING
# ==========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # Get JSON data from frontend
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Invalid request."
            }), 400

        job_text = data.get("text", "").strip()

        # Check empty input
        if not job_text:

            return jsonify({
                "error": "Please enter a job description."
            }), 400


        # ==================================
        # MACHINE LEARNING PREDICTION
        # ==================================

        prediction = model.predict([job_text])[0]

        probabilities = model.predict_proba([job_text])[0]


        # Find probability belonging to SCAM class (1)
        scam_probability = 0.0

        if hasattr(model, "classes_"):

            classes = list(model.classes_)

            if 1 in classes:

                scam_index = classes.index(1)
                scam_probability = probabilities[scam_index]

            else:

                scam_probability = probabilities[-1]

        else:

            scam_probability = probabilities[-1]


        # ==================================
        # RULE-BASED DETECTION
        # ==================================

        indicators, matched_phrases = detect_scam_indicators(job_text)


        # ==================================
        # FINAL RISK SCORE
        # ==================================

        risk_score = calculate_risk(
            scam_probability,
            indicators
        )


        # ==================================
        # RISK LEVEL
        # ==================================

        if risk_score >= 70:

            risk_level = "HIGH"

        elif risk_score >= 40:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        # ==================================
        # PREDICTION TEXT
        # ==================================

        if prediction == 1:

            prediction_text = "Potentially Suspicious"

        else:

            prediction_text = "Likely Legitimate"


        # ==================================
        # SAVE RESULT TO DATABASE
        # ==================================

        conn = sqlite3.connect("jobguard.db")

        conn.execute(
            """
            INSERT INTO analyses
            (job_text, prediction, risk_score, analyzed_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                job_text,
                prediction_text,
                risk_score,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()


        # ==================================
        # SEND RESULT TO FRONTEND
        # ==================================

        return jsonify({

            "prediction": prediction_text,

            "risk_score": risk_score,

            "risk_level": risk_level,

            "indicators": indicators,

            "matched_phrases": matched_phrases,

            "scam_probability": round(
                scam_probability * 100,
                2
            )

        })


    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=int(__import__("os").environ.get("PORT", 5000)),
        debug=False
    )