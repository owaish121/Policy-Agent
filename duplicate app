import os
import sys
import webbrowser
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

app = Flask(__name__)

# अपनी PDF फाइल का नाम सेट करें
PDF_FILENAME = "Order_NFSA_2015.pdf" 
load_dotenv()
api_key = os.getenv("MY_API_KEY")

if not os.path.exists(PDF_FILENAME):
    print(f"❌ त्रुटि: {PDF_FILENAME} फाइल नहीं मिली।")
    sys.exit()

# जेमिनी क्लाइंट में सुरक्षित रूप से API की पास की गई है
client = genai.Client(api_key=api_key)
gemini_file_uri = None  

def upload_initial_file():
    global gemini_file_uri
    try:
        print(f"📄 बैकएंड में PDF अपलोड हो रही है: {PDF_FILENAME}...")
        uploaded = client.files.upload(file=PDF_FILENAME)
        gemini_file_uri = uploaded.name  
        print("✅ फाइल सफलतापूर्वक लोड हो गई है!")
    except Exception as e:
        print(f"❌ शुरुआत में फ़ाइल अपलोड करने में विफल: {e}")
        sys.exit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    global gemini_file_uri
    question = request.form.get('question')
    
    if not question or not question.strip():
        return jsonify({'answer': 'कृपया कोई सवाल टाइप करें।'})

    if not gemini_file_uri:
        return jsonify({'answer': 'सर्वर पर फाइल लोड नहीं है। कृपया ऐप रीस्टार्ट करें।'})
    
    try:
        file_ref = client.files.get(name=gemini_file_uri)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[file_ref, question],
            config=types.GenerateContentConfig(
                system_instruction=(
                    "आप एक सहायक पॉलिसी एक्सपर्ट हैं। अपलोड की गई स्कैन पीडीएफ को ध्यान से पढ़ें "
                    "और उसी के आधार पर USER के सवाल का सटीक जवाब दें। जवाब हमेशा हिंदी में और स्पष्ट होना चाहिए।"
                    "पीडीएफ में जानकारी जिस खंड, उप-खंड, नियम या क्लॉज (जैसे: क, ख, ग, या 1, 2, 3) के तहत दी गई है, "
                    "जवाब में उस खंड का नाम और नंबर हूबहू शामिल करें (उदा. 'खंड (क) के अनुसार...')"
                ),
                temperature=0.1
            )
        )
        return jsonify({'answer': response.text})
    except Exception as e:
        return jsonify({'answer': f"त्रुटि: {str(e)}"})

@app.route('/exit', methods=['POST'])
def exit_app():
    global gemini_file_uri
    if gemini_file_uri:
        try:
            print("🧹 जेमिनी सर्वर से फाइल हटाई जा रही है...")
            client.files.delete(name=gemini_file_uri)
            gemini_file_uri = None
            print("🗑️ फाइल साफ कर दी गई है।")
        except Exception as e:
            print(f"फाइल हटाने में त्रुटि: {e}")
    return jsonify({'message': 'Exit Successful'})

if __name__ == '__main__':
    # रेंडर और लोकल दोनों के लिए सही तालमेल सेटअप
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("RENDER"):
        upload_initial_file()
    
    if not os.environ.get("WERKZEUG_RUN_MAIN") and not os.environ.get("RENDER"):
        webbrowser.open("http://127.0.0.1:5000/")
        
    port = int(os.environ.get("PORT", 5000))
    if os.environ.get("RENDER"):
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        app.run(debug=True, port=5000)