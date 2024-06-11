from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import pandas as pd

client = OpenAI(api_key='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')

# Step 1: Extract Trends from Google Trends
def get_trending_topics():
    pytrends = TrendReq(hl='en-US', tz=360)
    trending_searches_df = pytrends.trending_searches(pn='united_states')
    trending_topics = trending_searches_df[0].tolist()
    return trending_topics

# Step 2: Search Google (using requests and BeautifulSoup instead of googlesearch-python)
def google_search(query, num_results=5):
    search_results = []
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if 'url?q=' in href and not 'webcache' in href:
            search_results.append(href.split('url?q=')[1].split('&sa=U')[0])
    return search_results[:num_results]

# Step 3: Parse Results Using Beautiful Soup
def parse_results(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    return text[:1000]  # Limiting to the first 1000 characters for brevity

# Step 4: Generate Newsletter Using GPT-4
def generate_newsletter(trends_info):    
    prompt = f"""
    Write a LinkedIn newsletter summarizing the following trending topics and their recent developments:
    {trends_info}
    The newsletter should be engaging, informative, and suitable for a professional audience.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an AI language model that specializes in generating professional and informative LinkedIn newsletters. You will summarize trending topics and their recent developments in a way that is engaging and suitable for a professional audience."},
              {"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()

# Putting It All Together
def create_newsletter():
    trends = get_trending_topics()
    trends_info = ""
    
    for trend in trends:
        search_results = google_search(trend)
        for url in search_results:
            parsed_content = parse_results(url)
            trends_info += f"\nTrend: {trend}\nURL: {url}\nContent: {parsed_content}\n"
    
    newsletter = generate_newsletter(trends_info)
    return newsletter

# Example usage
if __name__ == "__main__":
    newsletter_content = create_newsletter()
    print(newsletter_content)
