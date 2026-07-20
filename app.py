import os
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 1. Gemini Client बनाएं
api_key = os.environ.get("MY_API_KEY")
client = genai.Client(api_key=api_key)

# 2. सर्वर स्टार्ट होते ही तुरंत PDF अपलोड करें
pdf_file = None
PDF_PATH = "Order_NFSA_2015.pdf"

print("--- सर्वर चालू हो रहा है: PDF अपलोड शुरू ---")
if os.path.exists(PDF_PATH):
    try:
        pdf_file = client.files.upload(file=PDF_PATH)
        print("✅ PDF सफलतापूर्वक Gemini पर अपलोड हो गई है!")
    except Exception as e:
        print("❌ PDF अपलोड में एरर आया:", str(e))
else:
    print(f"❌ '{PDF_PATH}' फाइल फोल्डर में नहीं मिली!")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    global pdf_file
    
    if not pdf_file:
        return jsonify({"response": "सर्वर पर फाइल अपलोड नहीं हो पाई है। कृपया रीस्टार्ट करें।"})

    try:
        user_query = request.json.get("query")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pdf_file, user_query]
        )
        return jsonify({"response": response.text})

    except Exception as e:
        print("Error during ask:", str(e))
        return jsonify({"response": f"त्रुटि: {str(e)}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)