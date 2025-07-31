from fetch_data import get_news_data
from gemini_Client import summarize_with_gemini
from twitter_client import post_to_twitter
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import uvicorn
import datetime
import logging
from pytz import timezone
import sys
from fastapi.middleware.cors import CORSMiddleware
import json
import re
from pprint import pprint
import uuid
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()
tz = timezone("Asia/Karachi")

origins = [
    "https://equibrief-market-pulse-fronted.vercel.app",  # production frontend URL
    "http://localhost:3000",     # frontend dev server (React, etc.)
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],              # allows all HTTP methods
    allow_headers=["*"],              # allows all headers
)

articles = []
tweet = {}

latest_data = {
    "news": articles,
    "tweet": {}
}

latest_events = []

def parse_dynamic_article(text):
    article = {}

    # 1. Extract title
    title_match = re.search(r"title:\s*(.+)", text)
    if title_match:
        article['title'] = title_match.group(1).strip()

    # 2. Extract body section
    body_match = re.search(r"body:\s*(.*)", text, re.DOTALL)
    if not body_match:
        return article

    body_text = body_match.group(1).strip()
    article['body'] = {}

    # 3. Detect section headers dynamically (lines ending with colon)
    section_matches = list(re.finditer(r"^([A-Z][^\n]{3,100}):\s*$", body_text, re.MULTILINE))

    # 4. Split content based on detected headers
    for i, match in enumerate(section_matches):
        section_title = match.group(1).strip()
        start_index = match.end()
        end_index = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(body_text)
        section_content = body_text[start_index:end_index].strip()

        # Process Key Takeaways as list
        if "takeaway" in section_title.lower():
            lines = [line.strip("•- ") for line in section_content.splitlines() if line.strip()]
            article['body'][section_title] = lines
        else:
            article['body'][section_title] = section_content

    return article


def initialize_scheduler():
    scheduler = BackgroundScheduler(
    timezone=tz,
    job_defaults={"coalesce": True, "max_instances": 1}
)
    scheduler.add_job(
        fetch_and_store_news,
        trigger="interval",
        hours=4,  # 24 / 5 = 4.8 → closest integer is 4
        id="five_times_news_fetch",
        replace_existing=True
    
    )
    scheduler.add_job(
        get_calendar,
        trigger="interval",
        hours=1,
        id="get_calendar",
        replace_existing=True
    )
        # Daily tweet
    scheduler.add_job(
        tweet,
        trigger="cron",
        hour=8,
        minute=00,
        args=["daily"],
        id="daily_morning",
        replace_existing=True
    )

    # Weekly tweet
    scheduler.add_job(
        tweet,
        trigger="cron",
        day_of_week="mon",
        hour=10,
        args=["weekly"],
        id="weekly",
        replace_existing=True
    )

    # Monthly tweet
    scheduler.add_job(
        tweet,
        trigger="cron",
        day=1,
        hour=11,
        args=["monthly"],
        id="monthly",
        replace_existing=True
    )

    # Yearly tweet
    scheduler.add_job(
        tweet,
        trigger="cron",
        month=1,
        day=1,
        hour=12,
        args=["yearly"],
        id="yearly",
        replace_existing=True
    )

    return scheduler

def tweet(summary_type="daily"):
    global tweet
    try:
        logger.info(f"Triggering {summary_type} tweet")
        news = get_news_data(summary_type=summary_type)
        titles = [a["title"] for a in news[:10]]
        newsTitles =  "\n".join(titles)
        logger.info("News data fetched successfully")
        
        tweet_text = summarize_with_gemini("", newsTitles)
        logger.info(f"Generated tweet: {tweet_text[:50]}...")
        
        result = {
            "id": str(uuid.uuid4()),
            "text": "message",
            "url": "tweet_url",
            "timestamp": datetime.datetime.now().isoformat()
        }
        result = post_to_twitter(tweet_text)
        logger.info(f"Tweet result: {result}")
        
        if "error" not in result:
            tweet = result
        
        return result
    except Exception as e:
        logger.error(f"Error in {summary_type} tweet: {str(e)}", exc_info=True)
        return False

def fetch_and_store_news():
    global articles
    try:
        news = get_news_data(summary_type="daily")
        desc_list = [item["description"] for item in news]
        concatenated_descriptions = "\n".join([f"[{i}] {desc}" for i, desc in enumerate(desc_list, start=1)])
        generated_article = summarize_with_gemini("", concatenated_descriptions)
        parsed = parse_dynamic_article(generated_article)
        structured_article = {
            "title": parsed["title"],
            "body": parsed["body"],
            "dateTime": datetime.datetime.now(tz).isoformat(),
            "id": str(uuid.uuid4())
        }
        if len(articles) >= 5:
            articles.pop(0)  # Remove the first (oldest) article
        articles.append(structured_article)  # Add the newest article
    
        latest_data["news"] = articles.copy()
        
    except Exception as e:
        logger.error(f"Error fetching hourly news: {str(e)}", exc_info=True)

def get_economic_calendar():
    try:
        global latest_events
        FAIRECONOMY_URL = "https://nfs.faireconomy.media/cc_calendar_thisweek.json"
        response = requests.get(FAIRECONOMY_URL, timeout=10)
        print("Response: ", response)
        response.raise_for_status()
        data = response.json()
        usd_events = [event for event in data if event.get("country") == "USD"]
        if len(usd_events) != 0:
            latest_events = usd_events
        return usd_events
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/")
async def manual_trigger(summary_type: str = "daily"):
    success = tweet(summary_type)
    return {
        "status": "success" if success else "error",
        "message": f"Tweet {'sent' if success else 'failed'} for {summary_type}",
        "data":success
    }

@app.get("/latest-data")
async def get_latest_data():
    global latest_data
    return latest_data

@app.get("/fetch-data")
async def get_latest_data():
    fetch_and_store_news()
    global latest_data
    return latest_data

@app.get("/latest-news")
async def get_latest_data():
    global latest_data
    news = get_news_data(summary_type="daily")
    latest_data["news"] = news
    return latest_data

@app.get("/economic-calendar")
async def get_calendar():
    try:
        global latest_events
        FAIRECONOMY_URL = "https://nfs.faireconomy.media/cc_calendar_thisweek.json"
        response = requests.get(FAIRECONOMY_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        usd_events = [event for event in data if event.get("country") == "USD"]
        if len(usd_events) != 0:
            latest_events = usd_events
        return {"status": "success", "events": usd_events}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/latest-events")
async def get_latest_data():
    global latest_events
    return latest_events


@app.on_event("startup")
async def startup_event():
    try:
        scheduler = initialize_scheduler()
        scheduler.start()
        
        logger.info("Scheduler started with the following jobs:")
        for job in scheduler.get_jobs():
            logger.info(f"Job: {job.id}, Next run: {job.next_run_time}")
            
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Starting server + scheduler")
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_config=None  # Use our configured logging
        )
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}", exc_info=True)