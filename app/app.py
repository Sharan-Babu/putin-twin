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
                    "content": "You are a research assistant. Search for and provide recent news, developments, and factual information about the query. Include specific dates and citations from reliable sources. Focus on verifiable information and format your response in a clear, organized way. Return the information as a list of bullet points, with each point being a separate finding or fact."
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        # Split the response into bullet points and clean them up
        results = completion.choices[0].message.content.split('\n')
        # Clean up and filter empty lines
        results = [line.strip().lstrip('•-* ') for line in results if line.strip()]
        return results
    except Exception as e:
        print(f"Perplexity web search error: {str(e)}")
        return []

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
        Format your response as a bullet-point list, with each point being a separate finding or fact."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5
            )
        )
        
        # Split the response into bullet points and clean them up
        results = response.text.split('\n')
        # Clean up and filter empty lines
        results = [line.strip().lstrip('•-* ') for line in results if line.strip()]
        return results
    except Exception as e:
        print(f"Web search error: {str(e)}")
        return []

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
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Format chat history in a more context-aware way
    formatted_history = ""
    if chat_history:
        formatted_history = "Previous conversation:\n"
        for msg in chat_history[:-1]:  # Exclude the current query
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted_history += f"{role}: {msg['content']}\n"

    # Combine original datasource with web results and chat history
    combined_content = f"""
You are Putin's digital twin, tasked with thinking and responding like him based on the following information. 
Maintain consistent context with previous conversation and respond naturally to follow-up questions.

General Information about Putin (Data Source):
{DATASOURCE_CONTENT}

Previous Conversation Context:
{formatted_history}

Recent Information from web search (if relevant to query):
{web_results}

Current user query: "{query}"

Instructions:
1. Consider the entire conversation history when formulating your response
2. Maintain consistency with previous answers
3. Reference relevant parts of the previous conversation if needed
4. Generate a single HTML file that visualizes your response
5. Make the HTML modern, responsive, and visually appealing (can use external libraries via CDN)
6. DO NOT include disclaimers, footers, or images
7. If the query references something from previous conversation, make sure to maintain that context
"""

    print(combined_content)
    # Send the combined content
    response = model.generate_content(
        combined_content,
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
        web_results = get_web_search_results(query)
        
        # Add assistant response to history with web results
        chat_history.append({
            'role': 'assistant',
            'content': generated_html,
            'web_results': web_results
        })
        
        # Update session
        session['chat_history'] = chat_history
        
        return jsonify({
            'html': generated_html,
            'web_results': web_results,
            'chat_history': chat_history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['chat_history'] = []
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 