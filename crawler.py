"""Contains an implementation of a web crawler for finding image URLs.
"""
from threading import Thread
from PIL import Image
from urllib.parse import urlparse
from contextlib import closing
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
import io
import cv2
import numpy as np
import queue
import urllib



def _same_domain(url1, url2):
    """Returns true if the two domains have the same domain.
    :return: true if domains are the same
    """
    return urlparse(url1).netloc == urlparse(url2).netloc


class Crawler(Thread):
    """A basic web crawler that looks for image URLs recursively.
    """

    def __init__(self, website_list, max_depth, max_browser_instances, load_timeout):
        """Creates a new web crawler.

        :param website_list: The list of web URLs to start crawling from
        :param max_depth: The maximum amount of pages deep the crawl should go
        :param max_browser_instances: The maximum amount of browser instances
            that may be open at once
        """

        super(Crawler, self).__init__()

        self.__running = False
        self.__results = queue.Queue()

        self.__website_list = website_list
        self.__browser_pool = queue.Queue()
        self.__crawled_urls = []
        self.__found_image_urls = []
        self.__max_depth = max_depth
        self.__load_timeout = load_timeout
        self.__browser_instance_cnt = max_browser_instances


    def run(self):
        """Starts the crawling process the listed websites. The results queue
        will start filling up with image URLs.
        """
        self.__running = True

        # Open up all browser windows
        for i in range(self.__browser_instance_cnt):
            browser = Chrome()
            # Set the page timeout
            browser.set_page_load_timeout(self.__load_timeout)
            self.__browser_pool.put(browser)

        crawl_threads = []

        # Starts crawling the page and returns the given browser to the pool
        # when finished
        def crawl_and_return_to_pool(url, browser):
            self._crawl_page(url, browser)
            self.__browser_pool.put(browser)

        # Start crawling each URL
        for url in self.__website_list:
            if self.__running:
                # Wait for an unused browser instance
                browser = self.__browser_pool.get()
                # Start crawling
                thread = Thread(target = crawl_and_return_to_pool, args = (url, browser))
                thread.start()
                crawl_threads.append(thread)

        # Wait for crawling to finish
        for thread in crawl_threads:
            thread.join()

        # Close all browser instances
        for i in range(self.__browser_instance_cnt):
            browser = self.__browser_pool.get()
            browser.close()

        self.__running = False


    def get_image(self):
        """Returns image data loaded from the crawler. Blocks until a new image
        has been found or until the crawler has finished running, in which case
        None is returned.

        :return: Numpy array of image data or None
        """

        if self.__running:
            try:
                # Load image from URL and convert it to a Numpy array
                url = self.__results.get_nowait()
                return self._url_to_image(url)
            except queue.Empty:
                # Try again
                pass

        return None


    def _crawl_page(self, url, browser, depth=0):
        """Crawls the given page for images and links to other webpages. Image
        URLs are put in the results queue. Links are followed and crawled.

        :param url: The URL of the page to crawl
        :param browser: The browser instance to open the page on
        :param depth: The current crawling depth, starting at zero
        """

        if depth > self.__max_depth:
            return
        if not self.__running:
            # Abort processing the page
            return

        self.__crawled_urls.append(url)

        image_urls = []
        link_urls = []

        # Load up the page
        try:
            browser.get(url)
            image_urls = self._get_image_urls(browser)
            link_urls = self._get_link_urls(browser)
        except TimeoutException:
            # TODO(velovix): Add support for partially loaded pages
            print("Warning: page " + url + " timed out")

        # Emit the URLs of all unique images in the page
        for image_url in image_urls:
            if not image_url in self.__found_image_urls:
                self.__results.put(image_url)
                self.__found_image_urls.append(image_url)

        # Follow links to unique URLs that have the same domain as the parent
        for link_url in link_urls:
            if not link_url in self.__crawled_urls and _same_domain(url, link_url):
                self._crawl_page(link_url, browser, depth=depth+1)


    def _get_image_urls(self, browser):
        """Returns the URLs of all images in the current page.

        :param browser: The browser that the page is loaded on
        :return: list of image URLs
        """

        images = browser.find_elements_by_css_selector("img")
        urls = []
        for image in images:
            urls.append(image.get_attribute("src"))

        return urls


    def _get_link_urls(self, browser):
        """Returns the URLs of all links in the current page.

        :param browser: The browser that the page is loaded on
        :return: list of link URLs
        """

        links = browser.find_elements_by_css_selector("a")
        urls = []
        for link in links:
            urls.append(link.get_attribute("href"))

        return urls


    def _url_to_image(self, url):
        """ Download the image, convert it to a NumPy array, and then read it into OpenCV format"""
        # image_data = urllib.request.urlopen(url).read()
        # return np.array(Image.open(io.BytesIO(image_data)))

        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        return image

    def close(self):
        """Prematurely stops crawling pages.
        """
        self.__running = False
