import requests
import os


def get_news_data(summary_type="daily"):
    base_url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": os.getenv("NEWSDATA_API_KEY"),
        "language": "en",
        "category": "business",  # Keep only 'business' as 'top' is too general
        "q": "stocks OR stock market OR finance OR investing OR NASDAQ OR S&P OR Dow Jones"
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        articles = data.get("results", [])
        return articles
    except Exception as e:
        return f"Failed to fetch news: {str(e)}"
