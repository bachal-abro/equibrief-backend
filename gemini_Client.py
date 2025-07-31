import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configure the Gemini API with your key from environment variables
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    # It's good practice to exit or handle this error appropriately
    # For this example, we'll print and continue, but in a real app,
    # you might want to stop execution.
    exit()


def summarize_with_gemini(stock_data, news_data):
    """
    Generates a financial news article using Google's Gemini API.

    Args:
        stock_data (str): A string containing stock market data.
        news_data (str): A string containing relevant news headlines or articles.

    Returns:
        str: The generated financial news article or an error message.
    """
    # The prompt is slightly adjusted for clarity but keeps the user's original structure.
    # Gemini models are powerful and can understand complex instructions directly.
    prompt = f"""
    Generate a complete financial news article with a title and a body based on the following data.

    **Stock Data Provided:**
    {stock_data}

    **News Data Provided:**
    {news_data}

    ---

    **Output Requirements:**

    **1. Title:**
    - Create a compelling and informative headline between 8 and 12 words.
    - The headline must include key entities and action-oriented verbs.
    - It should accurately reflect the most significant development from the data.

    **2. Body:**
    - **Lead Paragraph:** Start with a concise summary that immediately explains why this news is important.
    - **The Core Developments:** Under this exact subheading, provide a comprehensive overview (500+ words) detailing each major development in chronological order. Include exact dates, locations, and key figures involved. Use direct quotes from sources where applicable.
    - **Market Impact and Analysis:** Under this exact subheading, deliver a deep analysis of the market implications (500+ words). If possible, interpret the data in a way that could be visualized with charts.
    - **Expert Perspectives:** Under this exact subheading, include perspectives from 3-5 fictional experts, providing their credentials and viewpoints on the situation.
    - **Future Outlook and Long-Term Consequences:** Under this exact subheading, write a detailed projection of the potential long-term effects (500+ words), considering historical context and comparable events.
    - **Key Takeaways:** Under this exact subheading, end with clear, actionable takeaways for the reader.

    **3. Style and Structure:**
    - Maintain a professional tone suitable for financial journalism.
    - Structure the article with paragraphs of 3-5 sentences each.
    - The body of the article must be organized with the clear, plain-text subheadings specified in the "Body" section above.
    - Do not use markdown, bolding, or special formatting in the final output.
    - Write in the third person, avoiding first-person pronouns.

    **Output Format:**
    Provide the output in the following strict format, with "title:" and "body:" on separate lines.

    title: [Generated Headline Here]
    body: [Generated Article Content Here, including the specified subheadings]
    """

    # --- Gemini API Call ---
    try:
        # Select the Gemini model. 'gemini-1.5-flash-latest' is a fast and cost-effective choice.
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Set the generation configuration
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=8192, # Gemini 1.5 has a large context window; 8192 is a safe max for the output.
        )

        # Make the API call to generate content
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # Return the generated text, stripping any leading/trailing whitespace
        return response.text.strip()

    except Exception as e:
        # Handle potential errors from the API call
        return f"Gemini API Error: {str(e)}"

# --- Example Usage ---
if __name__ == "__main__":
    # Create a .env file in your project directory with:
    # GEMINI_API_KEY="YOUR_API_KEY_HERE"

    # Example data (replace with your actual data fetching logic)
    sample_stock_data = "AAPL: $170.15 (+1.2%), NVDA: $880.08 (-2.5%), TSLA: $175.79 (+0.8%) after hours."
    sample_news_data = "Federal Reserve hints at holding interest rates steady. New report shows consumer spending unexpectedly rose by 0.5% last month. Tech sector faces scrutiny over AI energy consumption."

    # Generate the article
    article = summarize_with_gemini(sample_stock_data, sample_news_data)

    # Print the result
    print(article)
