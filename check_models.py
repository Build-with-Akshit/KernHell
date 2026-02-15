import google.generativeai as genai
import os
from kernhell.config import config

key = config.get_active_key()
if not key:
    print("No key found")
    exit()

print(f"Using Key: {key[:5]}...")
genai.configure(api_key=key)

print("Listing Models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
