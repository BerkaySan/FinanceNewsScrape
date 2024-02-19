from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import yaml
import sys
sys.path.append("lib")
from elastic_lib import connect_to_elastic, write_to_elastic
from loguru import logger
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

current_time = datetime.now().strftime("%d-%m-%Y_%H")
log_file = f"/app/log/{current_time}.log"
logger.add(
    log_file,
    encoding="utf8",
    format="{time:DD-MM-YYYY_HH-mm}  | {level}  | {message}",
)

def method_gundem():

    logger.info("Eksi gündem verisi alınıyor...")

    with open("/app/config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    print("1")
    es_config = config["elasticsearch"]
    print("2")
    sel_config = config["seleniumgrid"]
    print("3")

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Remote(
        command_executor=f"{sel_config['host']}:{sel_config['port']}", options=options
    )

    print("4")

    # Haber sitesine git
    driver.get("https://eksisozluk111.com/basliklar/gundem")

    # Haber başlıklarını seç
    gundem_links = driver.find_elements(By.CSS_SELECTOR, ".topic-list.partial a")

    url_list = []
    for gundem_link in gundem_links:
        url_list.append(gundem_link.get_attribute("href"))

    for url in url_list:
        driver.get(url)
        sleep(5)

        dates = driver.find_elements(By.CLASS_NAME, "entry-date.permalink")
        date_list = [date.text for date in dates]

        authors = driver.find_elements(By.CLASS_NAME, "entry-author")
        author_list = [author.text for author in authors]

        author_length = len(authors)

        #Başlık sayısı ve diğer değişkenlerin sayısını eşitleme
        titles = driver.find_elements(By.ID, "title")
        titles_extended = titles * author_length
        title_list = [title.text for title in titles_extended]

        avatars = driver.find_elements(By.CLASS_NAME, "avatar")
        avatar_list = [avatar.get_attribute("src") for avatar in avatars]

        contents = driver.find_elements(By.CLASS_NAME, "content")
        content_list = [content.text for content in contents]

        es = connect_to_elastic(
            host_ip=f"{es_config['host']}:{es_config['port']}",
            username=es_config["user"],
            password=es_config["password"],
        )

        write_to_elastic(
            es,
            "eksi",
            title=title_list,
            date=date_list,
            content=content_list,
            avatar=avatar_list,
            author=author_list,
        )
        
    logger.info(f"Toplam çekilen EKSI GUNDEM veri sayısı {len(url_list)} tanedir.")
    logger.success("EKSI GUNDEM verileri başarıyla çekilmesi tamamlandı.")

    driver.quit()
