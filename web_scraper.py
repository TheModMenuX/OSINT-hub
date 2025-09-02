import trafilatura
import logging

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Some common website to crawl information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "Error: Unable to fetch content from the URL"
        
        text = trafilatura.extract(downloaded)
        if not text:
            return "Error: No text content could be extracted from the website"
        
        return text
    except Exception as e:
        logging.error(f"Web scraping error for {url}: {str(e)}")
        return f"Error extracting content: {str(e)}"
