import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv(override=True)

try:
    key = os.environ.get("GEMINI_API_KEY")
    print("Key length:", len(key) if key else 0)
    genai.configure(api_key=key)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Hello")
    print("SUCCESS")
    print(response.text)
            
except Exception as e:
    import traceback
    traceback.print_exc()
