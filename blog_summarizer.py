

import os
print("[DEBUG] blog_summarizer.py started execution.")
groq_key = os.environ.get("GROQ_API_KEY")
firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
print(f"[DEBUG] GROQ_API_KEY loaded: {str(groq_key)[:4]}...{'set' if groq_key else 'NOT SET'}")
print(f"[DEBUG] FIRECRAWL_API_KEY loaded: {str(firecrawl_key)[:4]}...{'set' if firecrawl_key else 'NOT SET'}")
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import FirecrawlScrapeWebsiteTool
from langchain_ollama import OllamaLLM

# GROQ LLM
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.environ.get("GROQ_API_KEY"),
) 

#llm = OllamaLLM(
#    model="ollama/deepseek-r1:1.5b",
#    temperature=0.7,)

tools = [FirecrawlScrapeWebsiteTool(os.environ.get("FIRECRAWL_API_KEY"))]

# Create an agent
blog_scraper = Agent(
    name="Blog Scraper",
    role="Web Content Researcher",
    goal="Extract complete and accurate content from blog URLs.",
    backstory="I am a skilled web researcher with a passion for extracting valuable information from various sources.",
    llm=llm,
    tools=tools,
    verbose=True,
    allow_delegation=False,
)

blog_summarizer = Agent(
    name="Blog Summarizer",
    role="Content Analyst",
    goal="Create concise, informative summaries of blog content.",
    backstory="You are a content analyst with a knack for distilling complex information, Your task is to create concise, informative summaries of blog content.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# Define tasks
def scrape_blog_task(url):
    task = Task(
        description=(f"Scrape the content from the provided blog at {url} using FirecrawlScrapeWebsiteTool."
                     "Extract the main content, including text, while ensuring the content is complete and accurate, filtering out navigation, ads, and other non-content elements."
                     ),
        expected_output="Full text content of the blog post in markdown format",
        agent=blog_scraper,
    )
    return task

def summarize_blog_task(scrape_task):
    task = Task(
        description=("Summarize the scraped blog content using the extracted text."
                     "Create a concise, informative summary of the blog post, highlighting key points and main ideas."
                     ),
        expected_output=(
            "Concise summary of the blog post in 100-200 words"
            "The summary will be used to generate a podcast script"
            "Summary should be suitable for a podcast script"
            ),
        agent=blog_summarizer,
        context=[scrape_task]
    )
    print(f"[DEBUG] summarize_blog_task created: {task}")
    return task

def create_blog_summary_crew(url):
    scrape_task = scrape_blog_task(url)
    summarize_task = summarize_blog_task(scrape_task)

    crew = Crew(
        agents=[blog_scraper, blog_summarizer],
        tasks=[scrape_task, summarize_task],
        verbose=True,
        process=Process.sequential,
    )

    return crew

def summarize_blog(url):
    crew = create_blog_summary_crew(url)
    result = crew.kickoff()

    return result.raw

if __name__ == "__main__":
    url = "https://www.oliveremberton.com/p/the-problem-isnt-that-life-is-unfair-its-your-broken-idea-of-fairness"
    summary = summarize_blog(url)
    print("Blog Summary:")
    print(summary)