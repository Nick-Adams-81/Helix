# Helix Chat Application

A full-stack chat application with user authentication and an AI-powered chatbot. The application uses Flask for the backend, React for the frontend, and integrates with OpenAI's GPT model for intelligent responses.

## Features

- User authentication (signup, login, logout)
- Secure session management
- AI-powered chat interface
- Google Search integration
- Real-time message updates
- Responsive design

## Dependencies

### Backend (Python/Flask)
- Flask
- Flask-SQLAlchemy
- Flask-Login
- python-dotenv
- langchain
- langchain-openai
- google-api-python-client
- wikipedia

### Frontend (React)
- React
- React Router
- React Context API

## Setup Instructions

1. Clone the repository
2. Set up the backend:
   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the server directory with:
   ```
   OPENAI_API_KEY=your_openai_key
   GOOGLE_SEARCH_API_KEY=your_google_search_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   ```

4. Set up the frontend:
   ```bash
   cd client
   npm install
   ```

5. Run the application:
   - Start the backend: `cd server && python app.py`
   - Start the frontend: `cd client && npm start`

The application will be available at `http://localhost:3000`
