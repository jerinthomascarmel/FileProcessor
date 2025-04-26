
import json
import re
import os
import openai
from docx import Document
from openpyxl import Workbook, load_workbook
# from google.colab import files
from openpyxl.styles import Alignment
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI()

# Function: Read full document text
def extract_content_with_openai(docx_file):
    doc = Document(docx_file)
    full_text = "\n".join([para.text.strip()
                          for para in doc.paragraphs if para.text.strip()])

    print("🧠 Processing document with OpenAI...")

    prompt = f"""
You are given the full text of a Word document. Act as a senior bidding tender document analyst and your task is to extract the structure into a JSON array where each item contains:

- header (main section heading), Please keep the numbering etc shown in the document.
- subheader (if applicable), please keep the numbering etc shown in the document.
- requirements (list of extracted requirements under the section or subheader), it should not be rephrase or reworded, it should just be the same from the document to avoid confusions. Also keep the numbering etc same.
- page_limit (if mentioned in the text, otherwise 0)

Return only **valid JSON** in this format:

[
  {{
    "header": "Header Title",
    "subheader": "Subsection Title or null",
   "requirements": [
      "1) Requirement one",
      "2) Requirement two",
      "(a) Sub requirement",
      "(b) Another sub requirement"
    ],
    "page_limit": "2"
  }},
  ...
]

[
  {{
    "header": "Appendix A – Tender Submission Requirements",
    "subheader": "Annexure 1",
    "requirements": [
      "1) Requirement one",
      "2) Requirement two",
      "(a) Sub requirement",
      "(b) Another sub requirement"
    ],
    "page_limit": "0"
  }}
]

RULES:
- Preserve exact numbering and lettering (like "1)", "(a)", etc.)
- Keep the original punctuation and structure from the document
- Only respond with a **valid JSON array**
- Do NOT include any commentary, markdown, or natural language outside the JSON

Here is the document content:

{full_text}
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
        )

        raw_content = response.choices[0].message.content.strip()
        # Truncate for display
        print("🔎 Raw GPT response:\n", raw_content[:1000])

        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        structured_data = json.loads(raw_content)
        return structured_data

    except Exception as e:
        print("❌ Error parsing GPT response:", str(e))
        return []


# Function: Excel formatting
def apply_wrap_text(cell):
    cell.alignment = Alignment(wrap_text=True)


def break_text_into_lines(text, max_characters=50):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        if len(' '.join(current_line + [word])) > max_characters:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

