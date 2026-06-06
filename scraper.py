

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from confluent_kafka import Producer
import datetime
from logger import get_logger

logger = get_logger("Scraper")

class Scraper():
    def __init__(self):
        """
        Initializes the Kafka Producer and the Selenium WebDriver.
        """
        try:
            self.producer = Producer({'bootstrap.servers': 'localhost:9092'})
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.producer = None

        self.driver = self.__initialize_driver()

    def scrape(self, url: str) -> None:
        """
        Scrapes titles, text and links from articles on the given url webpage and publishes them to Kafka

        Args:
            url (str): URL to a webpage

        Returns:
            /
        """
        self.driver.get(url)
        time.sleep(3)

        #Check if cookie pop up needs to be accepted
        try:
            self.driver.find_element(By.NAME, "agree").click()
        except NoSuchElementException:
            logger.info("No Cookies to accept")
        except Exception as e:
            logger.error(f"Error checking cookies: {e}")

        self.driver.maximize_window()

        # Simulate continuous scrolling
        stop_scrolling = 0
        while True:
            stop_scrolling += 1
            self.driver.execute_script("window.scrollBy(0,40)")
            time.sleep(0.5)
            if stop_scrolling > 400:
                break

        page_source = self.driver.page_source

        soup = BeautifulSoup(page_source, "html.parser")
        divs = soup.find_all("div")
        filtered_divs = [div for div in divs if div.h3 and len(div.h3.text) > 20]

        for div in filtered_divs:
            
            try:
                title = div.h3.text
            except Exception:
                title = "/"
                logger.warning("The crawled entry doesn't have a title")
                continue

            try:
                link = div.a["href"]
            except Exception:
                link = "/"
                logger.warning("The crawled entry doesn't have a link")

            self._publish_article(title, link)

        # Flush Kafka messages for this page
        if self.producer:
            self.producer.flush()

    def _delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result. """
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            pass # Delivered successfully

    def _publish_article(self, title: str, link: str) -> None:
        """
        Publishes a datapoint consisting of article title and article link 
        to a Kafka topic

        Args:
            title (str): Title of the article
            link (str): Link of the article
        """

        entry = {
            "title": title,
            "link": link,
            "date": datetime.datetime.now().isoformat()
        }

        if self.producer:
            try:
                self.producer.produce(
                    'scraped_articles',
                    value=json.dumps(entry).encode('utf-8'),
                    callback=self._delivery_report
                )
                self.producer.poll(0)
            except Exception as e:
                logger.error(f"Failed to publish article to Kafka: {e}")

    def __initialize_driver(self) -> webdriver.Chrome:
        """
        initializes the chrome webdriver for selenium
        """
        options = Options()
        try:
            options.add_argument("--disable-search-engine-choice-screen")
            options.add_argument("--no-sandbox")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-dev-shm-usage")
        except Exception as e:
            logger.error(f"An Unknown error has occured: {e}")
        driver = webdriver.Chrome(options=options)

        return driver

    def close(self):
        """
        Closes the webdriver and flushes Kafka producer.
        """
        if self.driver:
            self.driver.quit()
        if self.producer:
            self.producer.flush()
