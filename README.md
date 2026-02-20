# 🌱 EcoPack AI — Sustainable Packaging Recommendation System

## 📌 Overview

EcoPack AI is an AI-powered web application that helps businesses and individuals choose **environment-friendly packaging materials** based on product type, weight, length, height, width of the product, fragility, distance to be delivered and sustainability goals.

The system uses a Machine Learning model to analyze product characteristics and recommends the most suitable biodegradable or recyclable packaging material while also estimating environmental impact.

The goal of this project is to promote **sustainable packaging decisions** and reduce plastic usage by making eco-friendly alternatives easily accessible.

---

## 🚀 Features

* AI-based packaging material recommendation
* Environmental impact comparison
* CO₂ emission estimation
* Sustainability scoring
* Modern responsive UI
* REST API backend
* Real-time prediction results

---

## 🧠 How It Works

1. User enters product details:

   * Product category
   * Weight
   * Lenth of the product
   * Width of the product
   * Height of the product
   * Fragility
   * Moisture sensitivity
   * Distance to be delivered
   * Mode of Transportation

2. The backend sends the data to the ML model.

3. The trained model predicts the best packaging material such as:

   * PLA (Bioplastic)
   * Recycled Paper
   * Mushroom Packaging
   * Corn Starch Polymer
   * Bagasse Packaging
   * Recycled Cardboard and so on

4. The system returns:

   * Recommended material
   * Sustainability score
   * Estimated environmental impact

---

## 🏗️ Tech Stack

### Frontend

* React.js
* HTML5
* CSS3
* JavaScript

### Backend

* Node.js / Express.js

### Machine Learning

* Python
* Scikit-learn
* Pandas
* NumPy

### Database

* MongoDB / JSON dataset

---

## 📂 Project Structure

```
EcoPack-AI/
│
├── backend/
      ├── templates/
      ├── static/
      ├── app.py
├── models/             # Python ML model
├── dataset/            # Training dataset
├── screenshots/        # UI images
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Data Preprocessing & Machine Learning Model Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```


### 2️⃣ Backend Setup

```bash
cd backend
npm install
npm start
```

Server runs on:

```
http://localhost:5000
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on:

```
http://localhost:3000
```

Run model:

```bash
python app.py
```

---

## 📊 Machine Learning Model

* Algorithm Used: Random Forest Classifier and XG Boost
* Training Data: Packaging material properties dataset
* Model Output: Optimal sustainable packaging material
* Accuracy: ~90% (depends on dataset)

---

## 📷 Screenshots

* Home Page
  <img width="1920" height="1020" alt="{F4AE3416-38BA-484C-A98D-7DE854261E17}" src="https://github.com/user-attachments/assets/80e39d3e-0455-4fe0-8ec4-86242dee4d53" />

* Input Form
  <img width="1920" height="1020" alt="{343DD9BD-97E8-4D0D-81B8-28CA7E8B1189}" src="https://github.com/user-attachments/assets/5f2d2c61-2c0a-4361-b6bb-3147f41847f7" />

* Recommendation Result Page
  <img width="1920" height="1020" alt="{D357912A-035E-4333-9812-52D4667B8220}" src="https://github.com/user-attachments/assets/50e0731c-d8df-4430-853e-7ebc74bc4f89" />

* Report downloading Page
  <img width="1920" height="1020" alt="{97EDEFFB-AA3A-4440-A781-CDE33B7CC940}" src="https://github.com/user-attachments/assets/62356471-6961-4c9f-af7b-942dcf136dec" />
  
* Analytics Dashboard
  <img width="1920" height="1020" alt="{8D475716-989C-4872-B350-032BFEDD3DB2}" src="https://github.com/user-attachments/assets/7248f617-e40e-47f5-9fb3-6aeb7be52836" />



---

## 🌍 Use Cases

* E-commerce companies
* Small businesses
* Packaging designers
* Sustainable product startups
* Environmental researchers

---

## 🔮 Future Improvements

* LCA (Life Cycle Assessment) integration
* Mobile application
* Multi-language support

---

## 🤝 Contribution

Contributions are welcome.
Fork the repository and submit a pull request.


## 📜 License

This project is for educational and research purposes.
