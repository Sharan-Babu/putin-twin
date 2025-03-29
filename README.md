# Generative UI Chatbot

A dynamic web application that generates custom UI responses based on user queries about Vladimir Putin's timeline, combining historical data with real-time web search results using Google's Gemini AI.

## Features

- Interactive query interface for users
- Real-time web search integration using Gemini AI
- Dynamic HTML UI generation based on user queries
- Combines historical timeline data with recent web updates
- Modern, responsive interface using Tailwind CSS
- Live preview of generated UI in an iframe

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Gemini API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
The API key is currently hardcoded in the application for development purposes. In a production environment, you should move it to an environment variable.

## Project Structure

```
.
├── README.md
├── requirements.txt
└── app/
    ├── app.py              # Main Flask application
    ├── datasource.txt      # Historical timeline data
    └── templates/
        └── index.html      # Frontend template
```

## Usage

1. Start the Flask server:
```bash
cd app
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter your query in the text area (e.g., "Show me Putin's major political events in 2024")

4. Click "Generate UI" to get a custom-generated UI response

## How It Works

1. When a user submits a query, the application first uses Gemini AI with web search capability to fetch recent, relevant information about the query.

2. This real-time information is combined with the historical timeline data from `datasource.txt`.

3. The combined data is then sent to another Gemini AI model that generates a complete, standalone HTML page with:
   - Modern styling using CSS frameworks
   - Interactive elements using JavaScript
   - Responsive design for all screen sizes
   - Relevant visualizations when appropriate

4. The generated UI is displayed in an iframe on the page

## API Endpoints

- `GET /`: Serves the main application interface
- `POST /generate`: Accepts a query and returns generated HTML UI
  - Request body: `{ "query": "your query here" }`
  - Response: `{ "html": "generated html content" }`

## Error Handling

- The application includes error handling for:
  - Missing queries
  - API failures
  - Invalid HTML responses
  - Web search errors

## Development

The application is currently configured for development with:
- Debug mode enabled
- Direct API key usage (should be changed in production)
- Local server deployment

## Production Considerations

For production deployment:
1. Move the API key to environment variables
2. Use a production-grade WSGI server
3. Implement proper security measures
4. Add rate limiting
5. Set up proper logging
6. Configure CORS appropriately

## License

[Your chosen license] 