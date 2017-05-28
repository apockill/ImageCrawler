from time import sleep
from threading import Thread, RLock


class Crawler:
    def __init__(self, website_list):
        self.running = False
        self.results_queue = []

        self.main_thread = Thread(target=self.__main_loop)
        self.main_thread.start()

    def __main_loop(self):
        self.running = True
        while self.running:
            # Do creepy web-crawly things here
            # Add 'hits' to self.results_queue
            sleep(1)
            print("Working")


    def get_results(self):
        """
        Returns all results since the last time this function was called
        :return:
        """
        results = self.results_queue
        self.results_queue = []
        return results

    def close(self):
        self.running = False


