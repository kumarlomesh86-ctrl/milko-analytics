from flask import Flask, request, jsonify, render_template_string
import re
from datetime import date
app = Flask(__name__)

# -------------------------------
# Recommendation Logic
# -------------------------------
def recommend_cow(budget, milk):
    if budget >= 90000 and milk >= 15:
        return "HF"
    elif budget >= 80000 and milk >= 12:
        return "Gir"
    else:
        return "Local Cow"

def recommend_buffalo(budget, milk):
    if budget >= 120000 and milk >= 15:
        return "Murrah"
    elif budget >= 90000 and milk >= 10:
        return "Bhadawari"
    else:
        return "Local Buffalo"


# -------------------------------
# Disease Decision Tree
# -------------------------------
def disease_decision(symptom):
    s = symptom.lower().strip()
        
    if "fever" in s:
        return (
            "🩺 <b>Fever in Cattle:</b><ul>"
            "<li>Temp > 102°F</li>"
            "<li>Give clean water</li>"
            "<li>Avoid milking stress</li>"
            "<li>Call vet if fever > 2 days</li>"
            "</ul>"
        )

    if "mouth" in s or "foot" in s:
        return (
            "🦠 <b>Foot & Mouth Disease (FMD):</b><ul>"
            "<li>Blisters in mouth/feet</li>"
            "<li>Isolate animal</li>"
            "<li>Soft feed only</li>"
            "<li>Immediate vet visit</li>"
            "</ul>"
        )

    if "udder" in s or "low milk" in s:
        return (
            "🥛 <b>Mastitis / Low Milk:</b><ul>"
            "<li>Swollen udder</li>"
            "<li>Low milk yield</li>"
            "<li>Warm water wash</li>"
            "<li>Vet antibiotic required</li>"
            "</ul>"
        )

    if "diarrhea" in s or "loose" in s:
        return (
            "💩 <b>Diarrhea:</b><ul>"
            "<li>Give ORS</li>"
            "<li>Stop green fodder</li>"
            "<li>Vet if severe</li>"
            "</ul>"
        )

    return (
        "🩺 <b>Common Diseases:</b><ul>"
        "<li>Fever</li>"
        "<li>Mastitis</li>"
        "<li>FMD</li>"
        "<li>Diarrhea</li>"
        "</ul>"
        "Type symptom like: fever, mouth wound, low milk, diarrhea"
    )

# -------------------------------
# Fodder Recommendation Logic
# -------------------------------
def fodder_recommendation(goal):
    if goal == "milk":
        return (
            "🥛 <b>Milk Increase Fodder Plan:</b><ul>"
            "<li>Green Fodder 55%</li>"
            "<li>Maize / Barley 20%</li>"
            "<li>Concentrate 20%</li>"
            "<li>Mineral Mix 5%</li>"
            "</ul>"
        )

    if goal == "fat":
        return (
            "🧈 <b>Fat Increase Fodder Plan:</b><ul>"
            "<li>Green Fodder 40%</li>"
            "<li>Oil Cake / Cotton Seed 25%</li>"
            "<li>Dry Fodder 25%</li>"
            "<li>Mineral Mix 10%</li>"
            "</ul>"
        )

    return ""


# -------------------------------
# Chatbot Core
# -------------------------------
def dairy_chatbot(message, profile):
    text = message.lower().strip()
    numbers = list(map(int, re.findall(r"\d+", text)))

    # -------------------------------
    # Initialize profile keys if not present
    # -------------------------------
    profile.setdefault("budget", None)
    profile.setdefault("milkHistory", None)
    profile.setdefault("intent", None)
    profile.setdefault("milk_records", [])
    profile.setdefault("vaccinations", [])
    profile.setdefault("add_milk_step", None)
    profile.setdefault("vaccination_step", None)
    profile.setdefault("current_vaccine", None)
    profile.setdefault("milk_rate_step", None)
    profile.setdefault("animal_step", None)
    profile.setdefault("animal_type", None)
    profile.setdefault("fat", None)
    profile.setdefault("fat_rate", None)
    profile.setdefault("snf", None)
    profile.setdefault("snf_rate", None)
    profile.setdefault("awaiting_loan_detail", False)

    # -------------------------------
    # Step-based flows
    # -------------------------------
    
# ==================================================
    # ✅ ADD MILK STEP HANDLER (FIXED & FIRST)
    # ==================================================

    if profile.get("add_milk_step") == "value":
        if not numbers:
            return " Please tell today's total milk value (in₹)."

        qty = profile.get("temp_milk_qty")
        value = numbers[0]

        profile["milk_records"].append({
            "date": str(date.today()),
            "milk": qty,
            "value": value
        })

        profile["add_milk_step"] = None
        profile.pop("temp_milk_qty", None)

        return f"✅ Milk entry saved: {qty} L, ₹{value}"

    elif profile.get("add_milk_step") == "quantity":
        if not numbers:
            return "🥛 Please enter today's milk quantity (in liters)."

        profile["temp_milk_qty"] = numbers[0]
        profile["add_milk_step"] = "value"
        return " Please tell today's total milk value (in₹)."

    # -------------------------------
    # Add Milk Trigger
    # -------------------------------
    if text in ["add milk", "milk entry"]:
        profile["add_milk_step"] = "quantity"
        return "🥛 Please enter today's milk quantity (in liters)."
    # ---- Vaccination ----
    if text == "add vaccination":
        profile["vaccination_step"] = "name"
        return "💉 Please tell vaccination name (example: FMD, HS, BQ)"

    elif profile.get("vaccination_step") == "name":
        profile["current_vaccine"] = message.upper()
        profile["vaccination_step"] = "date"
        return "📅 Please tell vaccination date (YYYY-MM-DD)"

    elif profile.get("vaccination_step") == "date":
        profile["vaccinations"].append({
            "vaccine": profile["current_vaccine"],
            "date": message
        })
        profile["vaccination_step"] = None
        profile.pop("current_vaccine", None)
        return "✅ Vaccination saved"

# ---------------- MILK RATE STEP FLOW ----------------

    if profile["milk_rate_step"] == "fat":
        if not numbers:
            return "❌ Please enter FAT (%) in numbers only."
        profile["fat"] = numbers[0]
        profile["milk_rate_step"] = "fat_rate"
        return "💰 Please enter FAT rate."
    
    if profile["milk_rate_step"] == "fat_rate":
        if not numbers:
            return "❌ Please enter FAT rate in numbers only."
        profile["fat_rate"] = numbers[0]
        profile["milk_rate_step"] = "snf"
        return "📊 Please enter SNF (%)."
    
    if profile["milk_rate_step"] == "snf":
        if not numbers:
            return "❌ Please enter SNF (%) in numbers only."
        profile["snf"] = numbers[0]
        profile["milk_rate_step"] = "snf_rate"
        return "💰 Please enter SNF rate."
    
    if profile["milk_rate_step"] == "snf_rate":
        if not numbers:
            return "❌ Please enter SNF rate in numbers only."
        profile["snf_rate"] = numbers[0]
        profile["milk_rate_step"] = "qty"
        return "📦 Please enter milk quantity (L)."
    
    if profile["milk_rate_step"] == "qty":
        if not numbers:
            return "❌ Please enter milk quantity in numbers only."
    
        qty = numbers[0]
        rate = (profile["fat"] * profile["fat_rate"]) + (profile["snf"] * profile["snf_rate"])
        total = rate * qty
    
        profile["milk_rate_step"] = None
        return f"✅ Milk Rate: ₹{rate}/L<br>💰 Total Amount: ₹{total}"


# ---------------- BUY COW / BUFFALO ----------------

    if profile["animal_step"] == "budget":
        if not numbers:
            return "❌ Please enter budget in numbers only (₹)."
        profile["budget"] = numbers[0]
        profile["animal_step"] = "milk"
        return "❓ Please tell your milk range (L/day)."
    
    if profile["animal_step"] == "milk":
        if not numbers:
            return "❌ Please enter milk range in numbers only (L/day)."
    
        milk = numbers[0]
        budget = profile["budget"]
        profile["animal_step"] = None
    
        if profile["animal_type"] == "cow":
            return f"🐄 Based on ₹{budget} & {milk} L/day → {recommend_cow(budget, milk)}"
    
        if profile["animal_type"] == "buffalo":
            return f"🐃 Based on ₹{budget} & {milk} L/day → {recommend_buffalo(budget, milk)}"

    # ------------------------------------------------
# 🔒 FLOW LOCK: block keywords during steps
# ------------------------------------------------
    if (
        profile["add_milk_step"]
        or profile["milk_rate_step"]
        or profile["animal_step"]
        or profile["vaccination_step"]
    ):
        return "❗ Please complete the current step by entering numbers."

    # -------------------------------
    # Keyword-based flows
    # -------------------------------
#-------Milk Rate Trigger---------

    if "milk rate" in text:
        profile["milk_rate_step"] = "fat"
        return "🥛 Please tell FAT (%)."
        
    # ---- Milk Trend ----
    if "milk trend" in text:
        records = profile.get("milk_records", [])
        if len(records) < 2:
            return "⚠️ Not enough milk records to calculate trend. Please add daily milk."
        if records[-1]["milk"] > records[0]["milk"]:
            return "📈 Milk trend is increasing"
        elif records[-1]["milk"] < records[0]["milk"]:
            return "📉 Milk trend is decreasing"
        else:
            return "⚖️ Milk trend is stable"

    if text == "buy cow":
        profile["animal_type"] = "cow"
        profile["animal_step"] = "budget"
        return "❓ Please tell your budget for cow."

    if text == "buy buffalo":
        profile["animal_type"] = "buffalo"
        profile["animal_step"] = "budget"
        return "❓ Please tell your budget for buffalo."

# =================================================
    # 📊 MILK CHART (HTML – FIXED)
    # =================================================
    if "milk chart" in text:
        records = profile["milk_records"]
        if not records:
            return "⚠️ No milk data available"

        html = "<b>📊 Milk Records</b><ul>"
        total_milk = 0
        total_value = 0

        for r in records:
            html += f"<li>{r['date']} — {r['milk']} L — ₹{r['value']}</li>"
            total_milk += r["milk"]
            total_value += r["value"]

        html += "</ul>"
        html += f"<b>Total Milk:</b> {total_milk} L<br>"
        html += f"<b>Total Value:</b> ₹{total_value}"
        return html




    # ---- Vaccination Chart ----
    if "vaccination chart" in text:
        records = profile.get("vaccinations", [])
        if not records:
            return "⚠️ No vaccination records found."
        chart = "<b>💉 Vaccination History:</b><ul>"
        for r in records:
            chart += f"<li>{r['date']} — {r['vaccine']}</li>"
        chart += "</ul>"
        return chart

    # ---- Reset ----
    if "reset" in text:
        profile["budget"] = None
        profile["milkHistory"] = None
        profile["intent"] = None
        profile["awaiting_loan_detail"] = False
        return "✅ Budget and milk history reset. You can start again."

    # ---- Loan ----
    if "loan" in text:
        profile["awaiting_loan_detail"] = True
        return (
            "💰 <b>Animal Loan Options:</b><ul>"
            "<li>NABARD Dairy Loan</li>"
            "<li>Cooperative Bank Loan</li>"
            "<li>Kisan Credit Card (KCC)</li></ul>"
            "💡 Would you like to know about the process and documents required for animal loan? Comment 'Yes'"
        )

    if ("yes" in text or "loan process" in text or "loan documents" in text) and profile.get("awaiting_loan_detail"):
        profile["awaiting_loan_detail"] = False
        return (
            "📄 <b>Animal Loan Process & Required Documents:</b><ul>"
            "<li>Fill application form at bank/cooperative</li>"
            "<li>Provide ID proof (Aadhaar, Voter ID)</li>"
            "<li>Address proof (ration card, electricity bill)</li>"
            "<li>Farm details and animal purchase plan</li>"
            "<li>Income proof / KCC if available</li>"
            "<li>Collateral documents if required</li></ul>"
            "💡 Banks usually process within 7–14 days after verification."
        )

   # ---- Breed Price Queries (FIXED) ----

# Generic cow / buffalo price
    if re.search(r"\bcow\s+price\b", text):
        return (
            "🐄 <b>Cow Prices:</b><ul>"
            "<li>Sahiwal: ₹40000–65000 | 10–15 L/day</li>"
            "<li>Gir: ₹55000–85000 | 12–18 L/day</li>"
            "<li>HF: ₹70000–110000 | 15–22 L/day</li>"
            "</ul>"
        )
    
    if re.search(r"\bbuffalo\s+price\b", text):
        return (
            "🐃 <b>Buffalo Prices:</b><ul>"
            "<li>Murrah: ₹90000–150000 | 15–20 L/day</li>"
            "<li>Bhadawari: ₹80000–120000 | 10–15 L/day</li>"
            "</ul>"
        )
    
    # Specific breed price
    breed_prices = {
        "hf": "🐄 Holstein Friesian Cow: ₹70000–110000 | 15–22 L/day",
        "gir": "🐄 Gir Cow: ₹55000–85000 | 12–18 L/day",
        "sahiwal": "🐄 Sahiwal Cow: ₹40000–65000 | 10–15 L/day",
        "murrah": "🐃 Murrah Buffalo: ₹90000–150000 | 15–20 L/day",
        "bhadawari": "🐃 Bhadawari Buffalo: ₹80000–120000 | 10–15 L/day"
    }
    
    for k, v in breed_prices.items():
        if re.search(rf"\b{k}\b.*price|\bprice\b.*\b{k}\b", text):
            return v


 

 # ---- Fodder main ----
    if re.search(r"\bfodder\b", text):
        return (
            "🥬 <b>Fodder Ratio:</b><ul>"
            "<li>Green 60%</li>"
            "<li>Dry 25%</li>"
            "<li>Concentrate 15%</li>"
            "<li>Mineral mix</li>"
            "</ul>"
            "💡 To increase milk type <b>milk raise</b><br>"
            "💡 To increase fat type <b>fat raise</b>"
        )
    
    # ---- Fodder goal specific ----
    if re.search(r"\bmilk\s+raise\b", text):
        return fodder_recommendation("milk")
    
    if re.search(r"\bfat\s+raise\b", text):
        return fodder_recommendation("fat")
# -------------------------------
# 🥛 MILK HELP MENU (EXACT MATCH)
# -------------------------------
    if text == "milk":
        return (
            "🥛 <b>What do you want to know about milk?</b><ul>"
            "<li>Calculate Milk rate</li>"
            "<li>Milk selling price</li>"
            "<li>Add milk</li>"
            "<li>Milk trend</li>"
            "<li>Milk chart</li>" 
            "<li>Milk raise</li>" 
            "</ul>"
            "✍️ Please comment your choice."
        )

# -------------------------------
# 🏠 SHED
# -------------------------------
    if re.search(r"\bshed\b", text):
        return (
            "🏠 <b>Shed Management:</b><ul>"
            "<li>East–West orientation</li>"
            "<li>Dry floor and regular cleaning</li>"
            "<li>Good ventilation</li>"
            "<li>Proper sunlight and drainage</li>"
            "<li>Separate sick animal area</li>"
            "</ul>"
        )

# -------------------------------
# 🦠 DISEASE HANDLER
# -------------------------------
    disease_keywords = [
        "disease",
        "fever",
        "sick",
        "mouth",
        "foot",
        "udder",
        "low milk",
        "mastitis",
        "diarrhea",
        "loose"
    ]

    if any(k in text for k in disease_keywords):
        return disease_decision(text)



    # -------------------------------
# 🥛 MILK PRICE
# -------------------------------
# -------------------------------
# 🥛 MILK SELLING PRICE
# -------------------------------
    if "milk selling price" in text or "milk selling" in text:
        return (
            "🥛 <b>Milk Selling Price (Approx.):</b><ul>"
            "<li>Cow Milk: ₹35–55 / L</li>"
            "<li>Buffalo Milk: ₹50–75 / L</li>"
            "</ul>"
            "💡 Price depends on FAT, SNF & location"
        )

       
    # ---- Fallback / Help ----
    return (
        "<b>I can help with:</b><ul>"
        "<li>Cow price / buffalo price</li>"
        "<li>Buy cow / buffalo suggestion</li>"
        "<li>Milk Rate Calculation</li>"
        "<li>Add Milk and vaccination entry</li>"
        "<li>Milk trend, chart and vaccination chart</li>"
        "<li>Fodder</li>"
        "<li>Disease symptoms</li>"
        "<li>Shed</li>"
        "<li>Loan</li>"
        
        "❓What would you like to comment?"
        "</ul>"
    )


# -------------------------------
# Routes
# -------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    profile = data.get("profile", {})
    response = dairy_chatbot(data["message"], profile)
    return jsonify({
        "response": response,
        "profile": profile
    })

# -------------------------------
# Mobile UI
# -------------------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dairy Farm Guide Chatbot</title>
<style>
body{font-family:Arial;background:#f1f5f9;margin:0}
.container{max-width:500px;margin:auto;padding:10px}
.chat{background:#fff;height:65vh;overflow:auto;padding:10px;border-radius:10px}
.user{text-align:right;color:#2563eb;margin:6px}
.bot{text-align:left;color:#15803d;margin:6px}
input,button{width:100%;padding:10px;margin-top:5px;font-size:16px}
button{background:#16a34a;color:white;border:none;border-radius:6px}
</style>
</head>
<body>
<div class="container">
<h2>🐄 Dairy Farm Guide Chatbot</h2>
<div id="chat" class="chat">
<div class="bot">Welcome! I am your dairy farm guide. I can help with cow/buffalo prices, breed recommendation, fodder, milk, milk rate calculation, shed, disease symptoms, and loans. <br>(Comment like: buy cow, buy buffalo, cow price, fodder, disease, shed, loan)<br><br> <ul>You can also ask for:<ul/> <br> <li>add milk entry</li><br> <li>add vaccination</li><br> <li>milk trend</li><br> <li>milk chart</li><br> <li>vaccination chart</li></div>
</div>
<input id="msg" placeholder="Type here...">
<button onclick="send()">Send</button>
</div>

<script>
let profile = {name:"Farmer"};

function send(){
 let t = msg.value;
 if(!t) return;
 chat.innerHTML += `<div class="user">${t}</div>`;
 msg.value = "";
 fetch("/chat",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({message:t, profile:profile})
 }).then(r => r.json()).then(d => {
   chat.innerHTML += `<div class="bot">${d.response}</div>`;
   profile = d.profile;
   chat.scrollTop = chat.scrollHeight;
 });
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    print("✅ Dairy Farm Guide Chatbot Running")
    app.run(debug=True)
