# TwinPutin

A digital twin application for simulating conversations with Vladimir Putin, with the ability to visualize and organize responses in a custom dashboard view called Eagle's Eye.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the `.env.example` file to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Then edit the `.env` file and add your API keys:

```
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 3. Run the Application

```bash
cd app
python app.py
```

The application will be available at http://localhost:5000

## Features

- Chat interface with Putin's digital twin
- Real-time web search for up-to-date information
- Eagle's Eye dashboard for organizing and viewing multiple responses
- Draggable and resizable response containers
- Persistence of dashboard layouts between sessions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Gemini API key

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