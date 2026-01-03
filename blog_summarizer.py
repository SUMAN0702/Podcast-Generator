import os
import streamlit as st

print("[DEBUG] blog_summarizer.py started execution.")

# Don't load from os.environ - use Streamlit secrets instead
def get_api_keys():
    """Get API keys from Streamlit secrets"""
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
        firecrawl_key = st.secrets["FIRECRAWL_API_KEY"]
        print(f"[DEBUG] GROQ_API_KEY loaded: {str(groq_key)[:4]}...set")
        print(f"[DEBUG] FIRECRAWL_API_KEY loaded: {str(firecrawl_key)[:4]}...set")
        return groq_key, firecrawl_key
    except Exception as e:
        print(f"[ERROR] Failed to load API keys: {e}")
        return None, None

def summarize_blog(url):
    """
    Simplified blog summarizer for Streamlit
    """
    from groq import Groq
    from firecrawl import FirecrawlApp
    
    print(f"[DEBUG] Starting summarization for URL: {url}")
    
    # Get API keys
    groq_key, firecrawl_key = get_api_keys()
    
    if not groq_key or not firecrawl_key:
        return "Error: API keys not configured. Please add them to Streamlit secrets."
    
    # Step 1: Scrape the blog
    print("[DEBUG] Scraping blog content...")
    try:
        scraper = FirecrawlApp(api_key=firecrawl_key)
        scraped_result = scraper.scrape_url(url)
        
        # Extract content
        content = scraped_result.get('markdown', '') or scraped_result.get('content', '')
        
        if not content:
            content = str(scraped_result)
        
        print(f"[DEBUG] Scraped content length: {len(content)} characters")
    except Exception as e:
        print(f"[ERROR] Scraping failed: {e}")
        return f"Error scraping blog: {str(e)}"
    
    # Step 2: Truncate content to fit within token limits
    max_chars = 3000
    if len(content) > max_chars:
        content = content[:max_chars] + "..."
        print(f"[DEBUG] Content truncated to {max_chars} characters")
    
    # Step 3: Generate summary using Groq
    print("[DEBUG] Generating summary...")
    try:
        client = Groq(api_key=groq_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a content analyst. Create concise, informative summaries suitable for podcast scripts."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following blog post in 100-200 words, highlighting key points:\n\n{content}"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=300,
        )
        
        summary = chat_completion.choices[0].message.content
        print("[DEBUG] Summary generated successfully")
        return summary
        
    except Exception as e:
        print(f"[ERROR] Summary generation failed: {e}")
        return f"Error generating summary: {str(e)}"
