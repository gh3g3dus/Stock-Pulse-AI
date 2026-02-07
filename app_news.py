from flask import Flask, render_template, request
import requests
from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
app = Flask(__name__)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        ticker = request.form.get("ticker", "").upper().strip()
        if ticker:
            try:
                # Fetch recent news
                url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
                response = requests.get(url)
                response.raise_for_status()
                articles = response.json().get("articles", [])[:8]  # Limit to 8

                results = []
                for article in articles:
                    title = article.get("title", "No title")
                    desc = article.get("description", "") or ""
                    content = f"{title}. {desc}"

                    # Groq sentiment + summary
                    groq_resp = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",  # Updated to current supported model
                        messages=[
                            {
                                "role": "system",
                                "content": "Return ONLY valid JSON, nothing else. No text, no fences, no markdown, no explanations. "
                                           "Exactly: {\"sentiment\": float from -1.0 to 1.0, \"summary\": \"one sentence\"} "
                                           "If no sentiment or too short: {\"sentiment\": 0.0, \"summary\": \"Insufficient content\"}"
                            },
                            {"role": "user", "content": content}
                        ],
                        temperature=0.0,
                        max_tokens=80
                    )

                    raw = groq_resp.choices[0].message.content.strip()

                    # Aggressive JSON extraction
                    start_idx = raw.find('{')
                    end_idx = raw.rfind('}') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        raw = raw[start_idx:end_idx]

                    raw = raw.replace("```json", "").replace("```", "").strip()

                    try:
                        data = json.loads(raw)
                        sentiment = float(data.get("sentiment", 0.0))
                        summary = str(data.get("summary", "No summary available"))
                    except json.JSONDecodeError:
                        sentiment = 0.0
                        lower_content = content.lower()
                        if any(word in lower_content for word in ['growth', 'strong', 'positive', 'beat', 'upside', 'bullish', 'rally', 'gain']):
                            sentiment = 0.5
                        if any(word in lower_content for word in ['decline', 'risk', 'negative', 'miss', 'downside', 'bearish', 'drop', 'loss']):
                            sentiment = -0.5
                        summary = "Analysis failed (invalid format) - fallback applied"

                    results.append({
                        "title": title,
                        "url": article.get("url", "#"),
                        "sentiment": sentiment,
                        "summary": summary
                    })

            except Exception as e:
                error = f"Error: {str(e)} (check API keys or network)"

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)