🐄 Dairy Farm Guide Chatbot (Flask)

A single-file Flask chatbot application that helps dairy farmers with cow & buffalo selection, milk management, fodder planning, disease guidance, vaccination tracking, milk rate calculation, shed management, and animal loan assistance.

This project is rule-based, lightweight, and beginner-friendly, ideal for farmers, cooperatives, and agri-tech demos.

🌟 Key Features
🐄 Cattle Price & Breed Help

Cow price (HF, Gir, Sahiwal)

Buffalo price (Murrah, Bhadawari)

Breed-wise milk yield & price

Smart recommendation based on:

Budget

Expected milk (L/day)

🥛 Milk Management

Add daily milk entry

Milk trend analysis:

📈 Increasing

📉 Decreasing

⚖️ Stable

Milk chart (date-wise history)

Milk rate calculation using:

FAT %

SNF %

Rates

Quantity

🌿 Fodder Recommendation

General fodder ratio

Milk increase fodder plan

Fat increase fodder plan

💉 Vaccination Management

Add vaccination records

Vaccination history chart

🩺 Disease Decision Tree

Fever

Foot & Mouth Disease (FMD)

Mastitis / Low milk

Diarrhea

Symptom-based guidance

🏠 Shed Management

Proper orientation

Hygiene & ventilation

Drainage & sunlight

Sick animal isolation

💰 Animal Loan Guidance

NABARD Dairy Loan

Cooperative Bank Loan

Kisan Credit Card (KCC)

Loan process & required documents

🛠️ Technology Used

Language: Python

Framework: Flask

Frontend: HTML + CSS + JavaScript

Logic: Regex-based NLP

Storage: In-memory profile (JSON)

📁 Project Structure (Single File App)
📦 dairy-farm-chatbot
 ├── app.py        # Complete Flask app (backend + frontend)
 └── README.md     # Project documentation


✅ No database
✅ No external API
✅ One Python file only

▶️ How to Run Locally
1️⃣ Install Python (3.8+)
python --version

2️⃣ Install Flask
pip install flask

3️⃣ Run the Application
python app.py


Console output:

✅ Dairy Farm Guide Chatbot Running

4️⃣ Open in Browser
http://127.0.0.1:5000

💬 Example Commands to Try
buy cow
buy buffalo
cow price
buffalo price
hf price
gir price
add milk
milk trend
milk chart
milk rate
add vaccination
vaccination chart
fodder
milk raise
fat raise
disease fever
shed
loan
reset

🧠 How the Chatbot Works

Uses regex + keyword matching

Maintains a profile dictionary per user

Supports multi-step conversations:

Milk entry

Vaccination entry

Milk rate calculation

All logic handled inside a single Flask file

🚀 Future Improvements (Optional)

SQLite / MongoDB integration

Farmer login system

Graph charts (Chart.js)

Hindi / multilingual support

WhatsApp / Telegram bot

AI/ML disease prediction

👨‍🌾 Ideal For

Dairy farmers

Milk cooperatives

Agriculture startups

College mini-projects

Government demo tools

📜 License

MIT License
