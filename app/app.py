import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from openai import OpenAI
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDy3vyaXfTzO5QdcO6ClsuvLmC2fV_vjB0"
genai.configure(api_key=GEMINI_API_KEY)

# Configure OpenRouter API
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"  # Replace with your actual API key
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# Load the datasource content
with open('datasource.txt', 'r', encoding='utf-8') as file:
    DATASOURCE_CONTENT = file.read()

def get_web_search_results_perplexity(query):
    try:
        completion = openai_client.chat.completions.create(
            model="perplexity/sonar",
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant. Search for and provide recent news, developments, and factual information about the query. Include specific dates and citations from reliable sources. Focus on verifiable information and format your response in a clear, organized way with proper citations."
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Perplexity web search error: {str(e)}")
        return ""

def get_web_search_results(query):
    try:
        # First try Perplexity Sonar
        perplexity_results = get_web_search_results_perplexity(query)
        if perplexity_results:
            return perplexity_results
        
        # Fallback to Gemini if Perplexity fails
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""Based on this query: "{query}", search for and provide recent news, developments, and factual information. 
        Include specific dates and citations from reliable sources. Focus on verifiable information that would enhance our understanding of the query.
        Format your response in a clear, organized way with proper citations."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5
            )
        )
        
        return response.text
    except Exception as e:
        print(f"Web search error: {str(e)}")
        return ""

def clean_html_response(html_text):
    # Remove any ``` markers
    html_text = re.sub(r'```html?\s*', '', html_text)
    html_text = re.sub(r'```\s*$', '', html_text)
    
    # Extract content between <html> tags
    match = re.search(r'<html.*?>.*?</html>', html_text, re.DOTALL)
    if match:
        return match.group(0)
    return html_text

def generate_html(query, chat_history=None):
    if chat_history is None:
        chat_history = []

    # First, get web search results
    web_results = get_web_search_results_perplexity(query)
    print(web_results)
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Create chat history in the format Gemini expects
    gemini_history = []
    for msg in chat_history:
        if msg['role'] == 'user':
            gemini_history.append({
                "role": "user",
                "parts": [msg['content']]
            })
        else:
            gemini_history.append({
                "role": "model",
                "parts": [msg['content']]
            })

    # Start a new chat
    chat = model.start_chat(history=gemini_history)

    # Combine original datasource with web results for the current query
    combined_content = f"""
Your purpose is to act as Putin's digital twin and think like him based on information given below about him. Answer according to the user query. 

General Information about Putin (Data Source):
{DATASOURCE_CONTENT}

Information from the web (use only if relevant to the query):
{web_results}
"""

    prompt = f"""Based on the following user query: "{query}", generate a single HTML file that visualizes or presents relevant information from this datasource content. Choose the right UI interface for presenting the response. The HTML should be modern, responsive, and can use external libraries via CDN. Make it visually appealing.

First, think of the relevant information in the General Information and the web information and how they can be combined (plan it). Try to back your reasoning with information from the Data Source (Include this reasoning too in html). Then, proceed with the necessary html code. DO NOT include any disclaimers, footers, images."""

    # Send the combined content and prompt
    response = chat.send_message(
        combined_content + "\n\n" + prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4
        )
    )
    
    return clean_html_response(response.text)

@app.route('/')
def home():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('index.html', chat_history=session['chat_history'])

@app.route('/generate', methods=['POST'])
def generate():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Get chat history from session
        chat_history = session.get('chat_history', [])
        
        # Add user message to history
        chat_history.append({
            'role': 'user',
            'content': query
        })
        
        # Generate response
        generated_html = generate_html(query, chat_history)
        print(generated_html)
        
        # Add assistant response to history
        chat_history.append({
            'role': 'assistant',
            'content': generated_html
        })
        
        # Update session
        session['chat_history'] = chat_history
        
        return jsonify({
            'html': generated_html,
            'chat_history': chat_history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['chat_history'] = []
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True) 