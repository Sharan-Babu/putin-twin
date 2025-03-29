import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.genai import types
from google.ai import generativelanguage as glm
import re

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDy3vyaXfTzO5QdcO6ClsuvLmC2fV_vjB0"
genai.configure(api_key=GEMINI_API_KEY)

# Load the datasource content
with open('datasource.txt', 'r', encoding='utf-8') as file:
    DATASOURCE_CONTENT = file.read()

def get_web_search_results(query):
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Based on this query: "{query}", fetch relevant recent news and information. Include citations in your response. Focus on factual, verifiable information that would enhance our understanding of the query."""),
            ],
        ),
    ]
    tools = [
        types.Tool(google_search=types.GoogleSearch())
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.4,
        tools=tools,
        response_mime_type="text/plain",
    )

    response_text = ""
    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
    except Exception as e:
        print(f"Web search error: {str(e)}")
        return ""
    
    return response_text

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
    # First, get web search results
    web_results = get_web_search_results(query)
    
    # Combine original datasource with web results
    combined_content = f"""
Original Timeline:
{DATASOURCE_CONTENT}

Recent Updates and Additional Information:
{web_results}
"""
    
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
    prompt = f"""Based on the following query: "{query}", generate a single HTML file that visualizes or presents relevant information from this datasource content. The HTML should be modern, responsive, and can use external libraries via CDN. Include any necessary CSS and JavaScript inline or via CDN links. Make it visually appealing and interactive where appropriate.

Here's the combined datasource content to use:

{combined_content}

Return ONLY the complete HTML code without any explanations or markdown formatting. The HTML should incorporate both historical timeline data and recent updates where relevant. Return only the HTML code for the question asked and nothing else."""

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