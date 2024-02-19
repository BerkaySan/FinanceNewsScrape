from selenium.webdriver.common.by import By
from selenium.common import exceptions
from elasticsearch import Elasticsearch, helpers
from pytube import YouTube
import sys

sys.path.append("lib")
from elastic_lib import write_to_elastic
import process_data
import time
import re
import warnings

warnings.filterwarnings("ignore")


def getUrls(driver, title, count=5):
    # count = number of videos to scrape their URLs
    """
    Searches for 'title' on Youtube
    and returns first #count youtube
    videos' URLs
    """

    youtube_query = "https://www.youtube.com/results?search_query="
    video_urls = []

    driver.get(youtube_query + title + "&sp=EgIQAQ%253D%253D")
    time.sleep(2)

    driver.execute_script("window.scrollBy(0, 300);")

    try:
        results = driver.find_elements(By.XPATH, '//*[@id="video-title"]')
        added = 0
        index = 0
        if len(results) != 0:
            while added < count:
                try:
                    results[index].find_element(
                        By.XPATH,
                        '//*[@id="movie_player"]/div[31]/div[2]/div[1]/div[1]/button',
                    )
                    flag = False
                except:
                    flag = True
                if flag:
                    video_urls.append(results[index].get_attribute("href"))
                    added += 1
                    time.sleep(1)
                index += 1
    except exceptions.NoSuchElementException:
        errorMessage = "Error1: Check selector OR element may not yet "
        errorMessage += "be on screen rigth before find operation!"
        print(errorMessage)

    return video_urls


def get_video_title(youtube_url):
    """
    Takes a youtube URL as parameter
    and returns the title of the video
    """

    try:
        yt = YouTube(youtube_url)
        video_title = yt.title

        return video_title
    except Exception as e:
        print(f"An error2 occurred: {e}")
        return None


def scrape(driver, url, filename, es):
    """
    Scraps the comments frm the provided URL,
    determins the status,
    and inserts into ES
    """

    last1 = url.rindex("/")
    last2 = url[:last1].rindex("/")

    # youtube shorts
    if url[last2 + 1 : last1] == "shorts":
        url = "https://www.youtube.com/watch?v=" + url[last1 + 1 :]

    driver.get(url)
    time.sleep(3)

    try:
        my_video_title = get_video_title(url)
        comment_section = driver.find_element(By.XPATH, '//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        errorMessage = "Error3: Check selector OR element may not yet "
        errorMessage += "be on the screen right before the find operation!"
        print(errorMessage)
        return

    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(3)

    max_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        temp = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight)"
        )

        time.sleep(2)
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )

        temp2 = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

        if (
            (new_height == max_height)
            | ((len(temp2) - len(temp) < 20))
            | (len(temp) < 20)
        ):
            break

        max_height = new_height

    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    replies = driver.find_elements(By.XPATH, '//*[@id="more-replies"]')
    for reply in replies:
        try:
            reply.click()
        except:
            pass

    time.sleep(1)

    for i in range(len(driver.find_elements(By.XPATH, '//*[@id="content-text"]'))):
        more_replies = driver.find_elements(
            By.XPATH,
            "/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/ytd-comments/ytd-item-section-renderer/div[3]/ytd-comment-thread-renderer["
            + str(i)
            + "]/div/ytd-comment-replies-renderer/div[1]/div/div[2]/yt-next-continuation/paper-button/yt-formatted-string",
        )
        for more in more_replies:
            try:
                more.click()
            except:
                pass

    time.sleep(1)

    try:
        all_usernamess = driver.find_elements(By.XPATH, '//*[@id="author-text"]')
        all_commentss = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        errorMessage = "Error4: Check selector OR element may not yet "
        errorMessage += "be on the screen right before the find operation!"
        print(errorMessage)
        return

    all_statuss = process_data.analyze(all_commentss)

    write_to_elastic(
        es,
        "youtube",
        title=filename,
        video_title=my_video_title,
        all_usernames=all_usernamess,
        all_comments=all_commentss,
        all_status=all_statuss,
    )
