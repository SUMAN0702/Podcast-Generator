import os

print("[DEBUG] blog_summarizer.py started execution.")

def summarize_blog(url):
    """
    Simplified blog summarizer that works with Streamlit secrets
    """
    # Import here to avoid issues with module-level initialization
    from groq import Groq
    from firecrawl import FirecrawlApp
    
    # Try to get API keys from Streamlit secrets first, then fall back to environment
    try:
        import streamlit as st
        groq_key = st.secrets.get("GROQ_API_KEY")
        firecrawl_key = st.secrets.get("FIRECRAWL_API_KEY")
        print(f"[DEBUG] Using Streamlit secrets")
    except:
        groq_key = os.environ.get("GROQ_API_KEY")
        firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
        print(f"[DEBUG] Using environment variables")
    
    print(f"[DEBUG] GROQ_API_KEY loaded: {str(groq_key)[:4]}...{'set' if groq_key else 'NOT SET'}")
    print(f"[DEBUG] FIRECRAWL_API_KEY loaded: {str(firecrawl_key)[:4]}...{'set' if firecrawl_key else 'NOT SET'}")
    
    if not groq_key or not firecrawl_key:
        return "Error: API keys not configured. Please add GROQ_API_KEY and FIRECRAWL_API_KEY to Streamlit secrets or environment variables."
    
    print(f"[DEBUG] Starting summarization for URL: {url}")
    
    # Step 1: Scrape the blog using Firecrawl
    print("[DEBUG] Scraping blog content with Firecrawl...")
    try:
        scraper = FirecrawlApp(api_key=firecrawl_key)
        scraped_result = scraper.scrape_url(url)
        
        # Extract content from Firecrawl response
        content = scraped_result.get('markdown', '') or scraped_result.get('content', '')
        
        if not content:
            content = str(scraped_result)
        
        print(f"[DEBUG] Scraped content length: {len(content)} characters")
    except Exception as e:
        print(f"[ERROR] Scraping failed: {e}")
        return f"Error scraping blog with Firecrawl: {str(e)}"
    
    # Step 2: Truncate content to fit within Groq free tier limits
    # 3000 chars ≈ 750 tokens, stays well within 6000 token/minute limit
    max_chars = 3000
    if len(content) > max_chars:
        content = content[:max_chars] + "..."
        print(f"[DEBUG] Content truncated to {max_chars} characters")
    
    # Step 3: Generate summary using Groq
    print("[DEBUG] Generating summary with Groq...")
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


if __name__ == "__main__":
    url = "https://www.oliveremberton.com/p/the-problem-isnt-that-life-is-unfair-its-your-broken-idea-of-fairness"
    summary = summarize_blog(url)
    print("Blog Summary:")
    print(summary)
