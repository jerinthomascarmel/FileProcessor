import os
import openai
from docx import Document
from openpyxl import Workbook, load_workbook
#from google.colab import files
from openpyxl.styles import Alignment
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")   
client = openai.OpenAI()
# Function to extract content from Word document
def extract_content(docx_file):
    doc = Document(docx_file)
    extracted_text = {}
    current_section = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            if is_header(text):  # Define a way to detect headers
                current_section = text
                extracted_text[current_section] = {'content': [], 'page_limit': None}
            elif 'Page Limit:' in text:  # Assuming a pattern for page limits
                page_limit = text.split('Page Limit:')[1].strip()
                if current_section:
                    extracted_text[current_section]['page_limit'] = page_limit
            elif current_section:
                extracted_text[current_section]['content'].append(text)
    return extracted_text

# Function to identify headers and subheaders using OpenAI API
def identify_headers(text):
    prompt = f"""
    For each line of the provided text, determine whether it is a 'Main Header' or 'Subheader'.
    If the text is a main header, label it as 'Main Header: {text}'.
    If the text is a subheader, label it as 'Subheader: {text}'.

    Apply this to the following text:
    {text}
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",  # Or "gpt-4" if you have access
    )

    headers = response.choices[0].message.content.strip()
    return headers

# Function to check if a paragraph is a header or subheader
def is_header(text):
    # Simple heuristic for headers (can be expanded)
    return text.isupper() or text.endswith(':') or len(text.split()) < 5

# Function to identify requirements using OpenAI API
def identify_requirements(header, paragraphs):
    combined_paragraphs = "\n".join(paragraphs)
    prompt = f"Identify the requirements from the following section under the header '{header}':\n\n{combined_paragraphs}\n\nReturn the requirements in a list format.If no text is provided just return blank or empty space."

    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",  # Or "gpt-4" if you have access
    )

    page_limits = response.choices[0].message.content.strip()
    return page_limits

# Function to detect page limits using OpenAI API
def identify_page_limits(text):
    prompt = f"Identify any page limits mentioned in the following text. Return the page limits if specified:\n\n{text}. If the text passed is null or nothing can be found, just say 0."

    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",  # Or "gpt-4" if you have access
    )

    page_limits = response.choices[0].message.content.strip()
    return page_limits

# Function to break text into lines if it exceeds the character limit
def break_text_into_lines(text, max_characters=50):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        # If adding the next word would exceed the max character limit, start a new line
        if len(' '.join(current_line + [word])) > max_characters:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)  # Join lines with a newline character to create the multi-line string

# Function to apply wrap text in Excel cells
def apply_wrap_text(cell):
    cell.alignment = Alignment(wrap_text=True)