from flask import Flask, request, jsonify, render_template_string
import re

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
    s = symptom.lower()

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

    if "milk" in s or "udder" in s or "low milk" in s:
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
    text = message.lower()
    numbers = list(map(int, re.findall(r"\d+", text)))

    budget = profile.get("budget")
    milk = profile.get("milkHistory")
    intent = profile.get("intent")

        # ---- Milk Rate Variables ----
    profile.setdefault("milk_rate_step", None)
    profile.setdefault("fat", None)
    profile.setdefault("fat_rate", None)
    profile.setdefault("snf", None)
    profile.setdefault("snf_rate", None)


    # ---- Reset option ----
    if "reset" in text:
        profile["budget"] = None
        profile["milkHistory"] = None
        profile["intent"] = None
        profile["awaiting_loan_detail"] = False
        return "✅ Budget and milk history reset. You can start again."

    # ---- Loan Process / Documents ----
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

    # ---- Specific breed prices ----
    if "hf price" in text:
        return "🐄 Holstein Friesian Cow: ₹70000–110000 | 15–22 L/day"
    if "murrah price" in text:
        return "🐃 Murrah Buffalo: ₹90000–150000 | 15–20 L/day"
    if "bhadawari price" in text:
        return "🐃 Bhadawari Buffalo: ₹80000–120000 | 10–15 L/day"
    if "sahiwal price" in text:
        return "🐄 Sahiwal Cow: ₹40000–65000 | 10–15 L/day"
    if "gir price" in text:
        return "🐄 Gir Cow: ₹55000–85000 | 12–18 L/day"

    # ---- Buy cow / buffalo intent ----
    if "buy cow" in text or "suggest cow" in text:
        profile["intent"] = "cow"
        if budget is None:
            return "❓ Please tell your budget for cow"
        if milk is None:
            return "❓ Please tell your milk range (L/day)"
        breed = recommend_cow(budget, milk)
        return (f"🐄 Based on ₹{budget} & {milk} L/day → <b>{breed}</b><br>"
                "💡 Go with the same budget or type Reset for a new budget")

    if "buy buffalo" in text or "suggest buffalo" in text:
        profile["intent"] = "buffalo"
        if budget is None:
            return "❓ Please tell your budget for buffalo"
        if milk is None:
            return "❓ Please tell your milk range (L/day)"
        breed = recommend_buffalo(budget, milk)
        return (f"🐃 Based on ₹{budget} & {milk} L/day → <b>{breed}</b><br>"
                "💡 Go with the same budget or type Reset for a new budget")

    # ---- Budget input ----
    if numbers and intent and budget is None:
        profile["budget"] = numbers[0]
        return f"✅ Budget saved: ₹{numbers[0]}<br>❓ Please tell your milk range (L/day)"

    # ---- Milk input ----
    if numbers and intent and budget is not None and milk is None:
        profile["milkHistory"] = numbers[0]
        if intent == "cow":
            breed = recommend_cow(profile["budget"], profile["milkHistory"])
            return (
                f"✅ Milk expectation saved: {profile['milkHistory']} L/day<br>"
                f"🐄 Based on ₹{profile['budget']} & {profile['milkHistory']} L/day → <b>{breed}</b><br>"
                "💡 Go with the same budget or type Reset for a new budget"
            )
        if intent == "buffalo":
            breed = recommend_buffalo(profile["budget"], profile['milkHistory'])
            return (
                f"✅ Milk expectation saved: {profile['milkHistory']} L/day<br>"
                f"🐃 Based on ₹{profile['budget']} & {profile['milkHistory']} L/day → <b>{breed}</b><br>"
                "💡 Go with the same budget or type Reset for a new budget"
            )



        # ---- Cow / Buffalo List ----
    if "cow list" in text:
        return "🐄 Cow List:<ul><li>Sahiwal</li><li>Gir</li><li>HF</li></ul>"

    if "buffalo list" in text:
        return "🐃 Buffalo List:<ul><li>Murrah</li><li>Bhadawari</li></ul>"

        
    # ---- Cow / Buffalo Prices ----
    if "cow price" in text: 
        return "🐄 Cow Prices:<ul><li>Sahiwal: ₹40000–65000 | 10–15 L/day</li><li>Gir: ₹55000–85000 | 12–18 L/day</li><li>HF: ₹70000–110000 | 15–22 L/day</li></ul>"

    if "buffalo price" in text:
        return "🐃 Buffalo Prices:<ul><li>Murrah: ₹90000–150000 | 15–20 L/day</li><li>Bhadawari: ₹80000–120000 | 10–15 L/day</li></ul>"

    # ---- Fodder ----
    if "fodder" in text:
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

    # ---- Fodder Goal Specific ----
    if re.search(r"\bmilk\s+raise\b", text):
        return fodder_recommendation("milk")
    
    if re.search(r"\bfat\s+raise\b", text):
        return fodder_recommendation("fat")


    # ---- Shed ----
    if "shed" in text:
        return (
            "🏠 <b>Shed Management:</b><ul>"
            "<li>East–West direction</li>"
            "<li>Dry floor</li>"
            "<li>Good ventilation</li>"
            "</ul>"
        )

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

    # ---- Milk Rate Calculation Flow ----
    if "milk rate" in text or "milk price" in text:
        profile["milk_rate_step"] = "fat"
        return "🥛 Please tell FAT (%)"

    if profile["milk_rate_step"] == "fat" and numbers:
        profile["fat"] = numbers[0]
        profile["milk_rate_step"] = "fat_rate"
        return "💰 Please tell FAT rate"

    if profile["milk_rate_step"] == "fat_rate" and numbers:
        profile["fat_rate"] = numbers[0]
        profile["milk_rate_step"] = "snf"
        return "📊 Please tell SNF (%)"

    if profile["milk_rate_step"] == "snf" and numbers:
        profile["snf"] = numbers[0]
        profile["milk_rate_step"] = "snf_rate"
        return "💰 Please tell SNF rate"

    if profile["milk_rate_step"] == "snf_rate" and numbers:
        profile["snf_rate"] = numbers[0]
        profile["milk_rate_step"] = "quantity"
        return "📦 Please tell milk quantity (L)"

    if profile["milk_rate_step"] == "quantity" and numbers:
        quantity = numbers[0]

        rate_per_liter = (
            profile["fat"] * profile["fat_rate"]
            + profile["snf"] * profile["snf_rate"]
        )
        total_amount = rate_per_liter * quantity

        profile["milk_rate_step"] = None

        return (
            f"🥛 <b>Milk Rate Calculation:</b><br>"
            f"Rate per Liter: ₹{rate_per_liter:.2f}<br>"
            f"Total Milk Value: ₹{total_amount:.2f}"
        )

    
    # ---- Disease ----
    disease_keywords = ["disease","fever","sick","mouth","foot","milk","udder","low milk","diarrhea","loose"]
    if any(k in text for k in disease_keywords):
        return disease_decision(text)

    # ---- Fallback Help ----
    return (
        "<b>I can help with:</b><ul>"
        "<li>Cow price / buffalo price</li>"
        "<li>Buy cow / buffalo suggestion</li>"
        "<li>Milk Rate Calculation</li>"
        "<li>Fodder</li>"
        "<li>Disease symptoms</li>"
        "<li>Shed</li>"
        "<li>Loan</li>"
        "<li>Reset budget/milk</li>"
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
<div class="bot">Welcome! I am your dairy farm guide. I can help with prices, breed recommendation, fodder, milk, milk rate calculation, shed, disease symptoms, and loans. (Comment like: buy cow, buy buffalo, cow price, fodder, disease, shed, loan)</div>
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
