import yaml, json, newspaper, feedparser
from datetime import datetime
from fuzzywuzzy import fuzz
from datetime import datetime
import warnings
import sqlite3
import os

warnings.filterwarnings("ignore")



def scrape_news_from_feed(feed_url):
    articles = []
    try:
        # download the feed
        feed = feedparser.parse(feed_url)
        print("Parsed the feed.{0}".format(feed_url))
    except:
        print("An error occured while downloading the feed.")
        return None
    for entry in feed.entries:
        try:
            # create a newspaper article object
            article = newspaper.Article(entry.link)
            # download and parse the article
            article.download()
            article.parse()
            # extract relevant information
            articles.append(
                {
                    "title": article.title,
                    "author": article.authors,
                    "publish_date": article.publish_date,
                    "content": article.text,
                    "link": entry.link,
                }
            )
        except:
            print("An error occured while scraping the article.")
            continue
    return articles


current_time = datetime.now().strftime("%d-%m-%Y_%H")

# with open("/app/config/blacklist.json") as f:
#     blacklist_data = json.load(f)

with open("rss_links.txt") as file_object:
    lines = file_object.readlines()
    counter = 0
    conn = sqlite3.connect('/app/data/news.db')

    c = conn.cursor()

     
    for line in lines:
        feed_url = line.rstrip()
        articles = scrape_news_from_feed(feed_url)
        if articles is None:
            continue
        for article in articles:
            #if table does not exist, create it
            c.execute('''CREATE TABLE IF NOT EXISTS news (title text PRIMARY KEY, date text, content text, link text)''')
            try:
                # Check if an element is in the blacklist
                blacklisted = False
                # for item in blacklist_data:
                #     if fuzz.ratio(item["content"], article["content"]) > 0.7:
                #         blacklisted = True
                #         break
                if not blacklisted:
                    # Insert the article into the database
                    print("Inserting article into the database.")
                    c.execute("INSERT INTO news VALUES (?, ?, ?, ?)", (article["title"], article["publish_date"], article["content"], article["link"]))
                    conn.commit()

                    counter += 1
            except Exception as error:
                print("An exception occurred while processing article data:", error)
                print("This news is already in the database.")
    
                continue
    # We can also close the cursor if we are done with it
c.close()

