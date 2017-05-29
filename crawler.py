"""Contains an implementation of a web crawler for finding image URLs.
"""

from threading import Thread
import queue
from urllib.parse import urlparse
from contextlib import closing

from selenium.webdriver import Chrome

def _same_domain(url1, url2):
    """Returns true if the two domains have the same domain.
    :return: true if domains are the same
    """
    return urlparse(url1).netloc == urlparse(url2).netloc

class Crawler(Thread):
    """A basic web crawler that looks for image URLs recursively.
    """

    def __init__(self, website_list, max_depth=5):
        """Creates a new web crawler.

        :param website_list: The list of web URLs to start crawling from
        :param max_depth: The maximum amount of pages deep the crawl should go
        """

        super(Crawler, self).__init__()

        self.__running = False
        self.__results = queue.Queue()

        self.__website_list = website_list
        self.__browser = Chrome()
        self.__crawled_urls = []
        self.__found_image_urls = []
        self.__max_depth = max_depth


    def run(self):
        """Starts the crawling process the listed websites. The results queue
        will start filling up with image URLs.
        """
        self.__running = True

        with closing(Chrome()) as self.__browser:
            for url in self.__website_list:
                self._crawl_page(url)

        self.__running = False


    def get_image_url(self):
        """Blocks until a new image URL has been retrieved or the crawler has
        finished running, in which case None is returned.

        :return: An image URL or None if the crawler is finished
        """

        while self.__running:
            try:
                return self.__results.get_nowait()
            except queue.Empty:
                pass

        return None


    def _crawl_page(self, url, depth=0):
        """Crawls the given page for images and links to other webpages. Image
        URLs are put in the results queue. Links are followed and crawled.

        :param url: The URL of the page to crawl
        :param depth: The current crawling depth, starting at zero
        """

        if depth > self.__max_depth:
            return
        if not self.__running:
            print("Aborted processing page " + url)
            return

        self.__crawled_urls.append(url)

        # Load up the page
        self.__browser.get(url)
        image_urls = self._get_image_urls()
        link_urls = self._get_link_urls()

        # Emit the URLs of all unique images in the page
        for image_url in image_urls:
            if not image_url in self.__found_image_urls:
                self.__results.put(image_url)
                self.__found_image_urls.append(image_url)

        # Follow links to unique URLs that have the same domain as the parent
        for link_url in link_urls:
            if not link_url in self.__crawled_urls and _same_domain(url, link_url):
                self._crawl_page(link_url, depth=depth+1)


    def _get_image_urls(self):
        """Returns the URLs of all images in the current page.

        :return: list of image URLs
        """

        images = self.__browser.find_elements_by_css_selector("img")
        urls = []
        for image in images:
            urls.append(image.get_attribute("src"))

        return urls


    def _get_link_urls(self):
        """Returns the URLs of all links in the current page.

        :return: list of link URLs
        """

        links = self.__browser.find_elements_by_css_selector("a")
        urls = []
        for link in links:
            urls.append(link.get_attribute("href"))

        return urls


    def close(self):
        """Prematurely stops crawling pages.
        """
        self.__running = False
