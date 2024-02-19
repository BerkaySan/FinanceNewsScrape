import yaml, json, newspaper, feedparser
from datetime import datetime
from fuzzywuzzy import fuzz
from loguru import logger
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")
import sys

sys.path.append("lib")
from elastic_lib import connect_to_elastic, write_to_elastic


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
log_file = f"/app/log/{current_time}.log"

logger.add(
    log_file, encoding="utf8", format="{time:DD-MM-YYYY_HH-mm}  | {level}  | {message}"
)


with open("/app/config/blacklist.json") as f:
    blacklist_data = json.load(f)


with open("/app/config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

es_config = config["elasticsearch"]


with open("rss_links.txt") as file_object:
    lines = file_object.readlines()
    counter = 0
    logger.info("Haber sitelerinden veri çekilmeye başlanıyor...")
    logger.info(f"{len(lines)} farklı siteden haber çekiliyor...")
    for line in lines:
        feed_url = line.rstrip()
        articles = scrape_news_from_feed(feed_url)
        if articles is None:
            continue
        for article in articles:
            try:
                es = connect_to_elastic(
                    host_ip=f"{es_config['host']}:{es_config['port']}",
                    username=es_config["user"],
                    password=es_config["password"],
                )
            except Exception as connection_error:
                print(
                    "An exception occurred while connecting to ElasticSearch:",
                    connection_error,
                )
                continue

            try:
                # Check if an element is in the blacklist
                blacklisted = False
                for item in blacklist_data:
                    if fuzz.ratio(item["content"], article["content"]) > 0.7:
                        blacklisted = True
                        break
                if not blacklisted:
                    write_to_elastic(
                        es,
                        "news",
                        title=article["title"],
                        date=datetime.now(),
                        content=article["content"],
                        link=article["link"],
                    )
                    counter += 1
            except Exception as error:
                print("An exception occurred while processing article data:", error)
                print("This news is already in the database.")
                continue

logger.info(f"{counter} tane yeni haber eklendi.")
logger.success("Haber çekilme işlemi başarıyla tamamlandı.")
