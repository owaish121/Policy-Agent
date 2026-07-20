import os
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_key = os.environ.get("MY_API_KEY")
client = genai.Client(api_key=api_key)

# PDF फाइल ऑब्जेक्ट के बजाय केवल उसका नाम / पाथ स्टोर करें
PDF_PATH = "Order_NFSA_2015.pdf"
pdf_file_obj = None

def get_file():
    global pdf_file_obj
    if pdf_file_obj is None:
        if os.path.exists(PDF_PATH):
            print("Gemini पर PDF अपलोड हो रही है...")
            pdf_file_obj = client.files.upload(file=PDF_PATH)
            print("PDF सफलता पूर्वक अपलोड हो गई!")
    return pdf_file_obj

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_query = request.json.get("query")
        
        # हर वर्कर अपनी जरूरत के हिसाब से फाइल ऑब्जेक्ट उठा लेगा
        file_data = get_file()
        
        if not file_data:
            return jsonify({"response": "सर्वर पर Order_NFSA_2015.pdf फाइल उपलब्ध नहीं है।"})

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[file_data, user_query]
        )
        
        answer = response.text if response.text else "कोई जवाब नहीं मिला।"
        return jsonify({"response": answer})

    except Exception as e:
        print("Error during ask:", str(e))
        return jsonify({"response": f"त्रुटि: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)