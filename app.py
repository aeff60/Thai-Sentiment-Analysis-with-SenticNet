from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS

# โหลดโมเดลที่บันทึกไว้
model_data = np.load("thai_sentiment_model.npz")
weights = model_data["weights"]
bias = model_data["bias"]

# โหลด SenticNet2_Thai.txt
sentic_data = {}
with open("SenticNet2_Thai.txt", "r", encoding="utf-8") as file:
    next(file)  # ข้ามบรรทัดแรก
    for line in file:
        parts = line.strip().split(",")
        word = parts[1]
        features = list(map(float, parts[2:6]))  # Pleasantness, Attention, Sensitivity, Aptitude
        sentic_data[word] = features

# ฟังก์ชันสำหรับพยากรณ์ Sentiment Polarity
def forward(x):
    return np.dot(x, weights) + bias

# ฟังก์ชันแปลงประโยคภาษาไทยเป็นฟีเจอร์
def preprocess_sentence(sentence):
    words = sentence.split()  # ตัดประโยคเป็นคำ
    features = np.zeros(4, dtype=np.float32)  # เริ่มต้นฟีเจอร์เป็น 0
    count = 0  # นับจำนวนคำที่เจอใน SenticNet

    for word in words:
        if word in sentic_data:
            features += np.array(sentic_data[word])  # บวกฟีเจอร์ของคำที่พบ
            count += 1

    if count > 0:
        features /= count  # หาเฉลี่ยฟีเจอร์

    return features

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # รับข้อมูลจากคำขอ
        data = request.json
        sentence = data.get("sentence", "")

        if not sentence:
            return jsonify({"error": "Input must include a Thai sentence."}), 400

        # แปลงประโยคเป็นฟีเจอร์
        features = preprocess_sentence(sentence).reshape(1, -1)

        # พยากรณ์ค่า Polarity
        prediction = forward(features).flatten()[0]

        return jsonify({"sentence": sentence, "prediction": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
