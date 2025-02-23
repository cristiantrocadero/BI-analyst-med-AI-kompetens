# Description: This script fetches articles from a list of RSS feeds and
#  stores them in a list of dictionaries.
import feedparser  

# List of RSS feed URLs
RSS_URLS = [
    'http://www.dn.se/nyheter/m/rss/',
    'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/',
    'https://feeds.expressen.se/nyheter/',
    'http://www.svd.se/?service=rss',
    'http://api.sr.se/api/rss/program/83?format=145',
    'http://www.svt.se/nyheter/rss.xml'
]

# Create an empty list to store articles
posts = []

def main():
    print('-----Starting Rssarticles_1.py-----')
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ""),
                    'summary': entry.get('summary', ""),
                    'link': entry.get('link', ""),
                    'published': entry.get('published', "")
                }
                posts.append(article)
        except Exception as e:
            print(f"Error parsing URL {url}: {e}")
    print(f"Fetched {len(posts)} articles.")

if __name__ == "__main__":
    main()
