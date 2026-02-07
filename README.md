# Stock Pulse AI

A simple web app that tracks recent news for any stock ticker and uses Groq AI to analyze sentiment and summarize headlines.

### Features (MVP)
- Enter a stock ticker (e.g., NVDA, TSLA)
- Fetches latest news articles via NewsAPI
- Groq-powered sentiment scoring (-1 to +1) and 1-sentence summaries
- Basic Flask web interface

### Live Demo
(Coming soon – deploying to Render)

### Local Setup
```bash
git clone https://github.com/gh3g3dus/Stock-Pulse-AI.git
cd Stock-Pulse-AI

# Activate virtual environment
venv\Scripts\activate.bat   # Windows

# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env
# GROQ_API_KEY=your_groq_key
# NEWS_API_KEY=your_newsapi_key

# Run the app
python app_news.py