import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.ai import generativelanguage as glm
import re

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDy3vyaXfTzO5QdcO6ClsuvLmC2fV_vjB0"
genai.configure(api_key=GEMINI_API_KEY)

# Load the datasource content
with open('datasource.txt', 'r', encoding='utf-8') as file:
    DATASOURCE_CONTENT = file.read()

def clean_html_response(html_text):
    # Remove any ``` markers
    html_text = re.sub(r'```html?\s*', '', html_text)
    html_text = re.sub(r'```\s*$', '', html_text)
    
    # Extract content between <html> tags
    match = re.search(r'<html.*?>.*?</html>', html_text, re.DOTALL)
    if match:
        return match.group(0)
    return html_text

def generate_html(query):
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
    prompt = f"""Based on the following query: "{query}", generate a single HTML file that visualizes or presents relevant information from this datasource content. The HTML should be modern, responsive, and can use external libraries via CDN. Include any necessary CSS and JavaScript inline or via CDN links. Make it visually appealing and interactive where appropriate.

Here's the datasource content to use:

{DATASOURCE_CONTENT}

Return ONLY the complete HTML code without any explanations or markdown formatting and use only the datasource content to generate the html. Return only the HTML code for the question asked and ntg else."""

    response = model.generate_content(prompt)
    return clean_html_response(response.text)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        generated_html = generate_html(query)
        return jsonify({'html': generated_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 