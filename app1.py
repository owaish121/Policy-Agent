import os
import sys

# 1. Google API Key सेट करना
os.environ["GOOGLE_API_KEY"] = "AIzaSyCrSvyrmJj0TTCWWsogcGpQTYXMsJcpIBY"

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS  
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

pdf_filename = "Order_NFSA_2015.pdf"

# जाँच करें कि पीडीएफ फाइल मौजूद है या नहीं
if not os.path.exists(pdf_filename):
    print(f"❌ error: {pdf_filename} File not found ।")
    sys.exit()

print("\n📄 PDF फ़ाइल को प्रोसेस किया जा रहा है...")
print("⏳ कृपया प्रतीक्षा करें, लोकल डेटाबेस तैयार हो रहा है...")

# 🛠️ यहाँ से हमने try-except हटा दिया है ताकि असली एरर टर्मिनल पर दिखे
loader = PyPDFLoader(pdf_filename)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
final_documents = text_splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.from_documents(final_documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4}) 
print("✅ डेटाबेस और कस्टम कंपोनेंट्स तैयार हैं।")

# 5. जेमिनी दिमाग (LLM) को लोड करना
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# 6. सिस्टम निर्देश (Prompt) सेट करना
system_prompt = (
    "आप एक सहायक पॉलिसी एक्सपर्ट हैं। नीचे दिए गए संदर्भ (context) का उपयोग करके "
    "USER के सवाल का सटीक और सीधा जवाब हिंदी में दें। जवाब हमेशा पूरी तरह स्पष्ट होना चाहिए।\n\n"
    "⚠️ महत्वपूर्ण नियम:\n"
    "1. पीडीएफ में जानकारी जिस खंड, उप-खंड, नियम या क्लॉज (जैसे: क, ख, ग, या 1, 2, 3) के तहत दी गई है, "
    "जवाब में उस खंड का नाम और नंबर हूबहू शामिल करें (उदा. 'खंड (क) के अनुसार...').\n"
    "2. अपनी तरफ से कोई काल्पनिक जानकारी न जोड़ें, केवल दिए गए संदर्भ के आधिकारिक खंडों का ही उल्लेख करें।\n\n"
    "संदर्भ (Context):\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("\n🤖 LangChain एआई पॉलिसी एजेंट सक्रिय हो चुका है... Type 'exit' to quit.")

# 🔄 लगातार सवाल पूछने का मुख्य लूप
while True:
    user_question = input("\n👉 enter your question: ").strip()
    
    if user_question.lower() == 'exit':
        print("👋 Exiting Policy Agent. Goodbye!")
        break

    if not user_question:
        print("❌ Please enter a valid question ।")
        continue

    print("\n🔍 एजेंट लोकल डेटाबेस से सही खंड ढूंढ रहा है...")
    response_text = rag_chain.invoke(user_question)
    
    print("\n📝 Answer:")
    print(response_text)
    print("\n" + "="*40)