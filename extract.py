import pdfplumber
import os
import json
from groq import Groq
from dotenv import load_dotenv

# ✅ Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# ✅ Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ✅ Function to send syllabus text to Groq model
def extract_syllabus(text):
    prompt = f"""
        You are a structured data explorer.
        Extract ONLY syllabus units.
        Each unit should become one JSON object.

        Do NOT create a separate object for the list of all units.
        Do NOT treat unit names as chapters.
        The chapters field should contain only the topics listed under that unit.

        Return ONLY valid JSON.

        Schema:

        [
        {{
            "subject": "string",
            "unit": "string",
            "chapters": ["string"],
            "exam_date": "YYYY-MM-DD or null",
            "weightage": "percentage or null"
        }}
        ]

        Syllabus text:

        {text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=4000
    )
    return response.choices[0].message.content

# ✅ Function to clean JSON response
def clean_json_response(raw):
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in response")
    return raw[start:end+1]

# ✅ Main function
def main():
    try:
        # Path to your syllabus PDF
        pdf_path = r"C:\Users\SRUJITHA\Downloads\sample_syllabus_for_studypilot.pdf.pdf"
        text = extract_text_from_pdf(pdf_path)
       

        raw_output = extract_syllabus(text)
        cleaned = clean_json_response(raw_output)
        data = json.loads(cleaned)
        

        # Save JSON file
        output_path = r"C:\Users\SRUJITHA\syllabus\syllabus.json"
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        # ✅ Success message
        print("Json has been written properly")

    except Exception as e:
        print(f"❌ Error: {e}")

# ✅ Run the script
if __name__ == "__main__":
    main()
