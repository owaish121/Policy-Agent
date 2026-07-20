import os
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_key = os.environ.get("MY_API_KEY")
client = genai.Client(api_key=api_key)

PDF_PATH = "Order_NFSA_2015.pdf"
pdf_file = None

# सर्वर स्टार्ट होते ही PDF अपलोड
if os.path.exists(PDF_PATH):
    try:
        pdf_file = client.files.upload(file=PDF_PATH)
        print("✅ PDF सफलतापूर्वक Gemini पर अपलोड हो गई है!")
    except Exception as e:
        print("❌ PDF अपलोड एरर:", str(e))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    global pdf_file
    try:
        # JSON या Form डेटा दोनों को रीड करने के लिए
        data = request.get_json(force=True, silent=True) or request.form
        user_query = data.get("query") if data else None

        if not user_query:
            return jsonify({"response": "कृपया कोई सवाल लिखें।"})

        if not pdf_file:
            if os.path.exists(PDF_PATH):
                pdf_file = client.files.upload(file=PDF_PATH)
            else:
                return jsonify({"response": "सर्वर पर PDF फाइल नहीं मिली।"})

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