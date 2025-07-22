import os
import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def summarize_with_cohere(stock_data, news_data):
    prompt = f"""
    Generate a complete financial news article with title and body based on the following data:
    
    STOCK DATA: {stock_data}
    NEWS DATA: {news_data}
    
    OUTPUT REQUIREMENTS:
    1. TITLE: 
       - Create a compelling 8-12 word headline
       - Include key entities and action verbs
       - Reflect the most significant development
    
    2. BODY: [In a rapidly evolving situation, begin with the most critical facts. Then provide:]
       - Comprehensive overview (500+ words) of each major development
       - Exact dates, locations, and key figures involved
       - Direct quotes from sources where applicable
       - Deep analysis of market implications (500+ words)
       - 3-5 expert perspectives with credentials
       - Historical context and comparable events
       - Detailed future projections (500+ words)
       - Minimum 4000 tokens total output
    
    3. STRUCTURE:
       LEAD PARAGRAPH: Immediate summary of why this matters
       SECTION 1: The Facts (chronological detail)
       SECTION 2: Market Impact (charts/data preferred)
       SECTION 3: Expert Roundtable
       SECTION 4: Long-Term Consequences
       CONCLUSION: Clear takeaways
    
    4. STYLE:
       - Professional financial journalism tone
       - Paragraphs of 3-5 sentences each
       - Subheadings every 200-300 words
       - No markdown or special formatting
       - Avoid first-person pronouns
    
    OUTPUT FORMAT:
    title: [generated headline here]
    body: [generated article content here]
    """
    try:
        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.7,
            max_tokens=4000,
        )
        return response.text.strip()
    except Exception as e:
        return f"Cohere Error: {str(e)}"