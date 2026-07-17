import os
import sys

# Google API Key 
os.environ["GOOGLE_API_KEY"] = "AIzaSyCrSvyrmJj0TTCWWsogcGpQTYXMsJcpIBY"

from google import genai
from google.genai import types

pdf_filename = "Order_NFSA_2015.pdf"

if not os.path.exists(pdf_filename):
    print(f"❌ error: {pdf_filename} File not found ।")
    sys.exit()

# start google client
client = genai.Client()

print("\n📄 Uploade scan pdf on google gemini...")
print("⏳ Please wait...")

try:
    # Uploade the pdf file on google gemini and read it
    uploaded_file = client.files.upload(file=pdf_filename)
    print("✅ Succesesfully uploade pdf on gemini!")
except Exception as e:
    print(f"❌ some error at the uploade time {e}")
    sys.exit()

# Start main Program
print("\n🤖 Policy Agent is now active. Type 'exit' to quit the program.")

# 🔄 लूप को बिल्कुल सुरक्षित तरीके से यहाँ शुरू करते हैं
while True:
    try:
        user_question = input("\n👉 enter your question: ")
        
        # Check if the user wants to exit the loop
        if user_question.strip().lower() == 'exit':
            print("👋 Exiting Policy Agent. Goodbye!")
            break

        if not user_question.strip():
            print("\n❌ Please enter your question ।")
            continue  # बिना क्रैश किए दोबारा सवाल पूछने पर ले जाएगा

        print("\n🔍 Gemini is searching for the answer in your scanned PDF...")
        
        # Generate the answer using Google Gemini model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_file, user_question],
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
        
        print("\n📝 Answer:")
        print(response.text)
        
    except Exception as e:
        if "429" in str(e):
            print("\n⚠️ Server error Please try after 5 to 7 minuts।")
        elif "404" in str(e):
            print("\n⚠️ Server error Please try later।")
        else:
            print(f"\n❌ Some error: {e}")
        
        # एरर आने के बाद भी लूप न टूटे, इसलिए हम यहाँ 'continue' कर रहे हैं
        continue

# 🧹 जब यूजर खुद 'exit' लिखेगा, तब लूप खत्म होगा और फाइल सर्वर से डिलीट होगी
print("\n🧹 Cleaning up server files...")
try:
    client.files.delete(name=uploaded_file.name)
    print("🗑️ Server files deleted successfully.")
except:
    pass