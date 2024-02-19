from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys

sys.path.append("lib")
from elastic_lib import connect_to_elastic
import comment_scrape
from datetime import datetime
import yaml
import time
from loguru import logger
import warnings

warnings.filterwarnings("ignore")


def main():
    print("Starting...")
    num_video = 3
    trend_num = 3

    current_time = datetime.now().strftime("%d-%m-%Y_%H")
    log_file = f"/app/log/{current_time}.log"
    logger.add(
        log_file,
        encoding="utf8",
        format="{time:DD-MM-YYYY_HH-mm}  | {level}  | {message}",
    )

    with open("/app/config/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    es_config = config["elasticsearch"]
    sel_config = config["seleniumgrid"]

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Remote(
        command_executor=f"{sel_config['host']}:{sel_config['port']}", options=options
    )

    es = connect_to_elastic(
        host_ip=f"{es_config['host']}:{es_config['port']}",
        username=es_config["user"],
        password=es_config["password"],
    )

    logger.info("Youtube modülü selenium'a ve ES'e bağlandı...")

    # query = {
    #     "_source": ["Baslik"],
    #     "query": {
    #         "match_all": {}
    #     }
    # }

    # index_name = "haberler"
    # response = es.search(index=index_name, body=query, size=5)
    # titles = [doc['_source']['Baslik'] for doc in response['hits']['hits']]

    titles = []
    driver.get("https://eksisozluk111.com/basliklar/m/populer")

    ul = driver.find_element(By.CLASS_NAME, "topic-list.partial.mobile")
    trends = ul.find_elements(By.TAG_NAME, "li")[:trend_num]

    for li_elements in trends:
        clear_title = li_elements.text.split("\n")[0]
        titles.append(clear_title)

    time.sleep(2)

    for video in titles:
        j = 1
        time.sleep(2)
        for url in comment_scrape.getUrls(driver, video, num_video):
            if url is not None:
                comment_scrape.scrape(driver, url, video, es)
            j += 1
    driver.close()

    logger.success("Youtube yorumları ile tüm işlemler tamamlandı!")


if __name__ == "__main__":
    main()
