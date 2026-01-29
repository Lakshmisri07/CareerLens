import google.generativeai as genai

# Configure with your key
genai.configure(api_key='AIzaSyBcRXfsbPY8HYdsZLPDSV_cv1BV1A-vS44')

print("Available models that support generateContent:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")