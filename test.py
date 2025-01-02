from engine.config import *
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Example usage:
response = model.generate_content("test")

print(response)

