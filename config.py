import json
from threading import RLock


class Config:
    """
    A threading-proof class for accessing config files and settings
    """

    WEBSITES_FILE = "Websites.txt"
    SETTINGS_FILE = "Settings.json"

    DEFAULT_SETTINGS = {"search_depth": 3,
                        "max_browsers": 1}

    def __init__(self):
        self.lock = RLock()


    @property
    def websites(self):
        """
        Tries to load a file with website list in the current directory.
        :return:
        """
        web_list = []
        with self.lock:
            try:
                with open(self.WEBSITES_FILE, "r") as file:
                    for line in file:
                        line = line.replace('\n', '')
                        web_list.append(line)
            except FileNotFoundError:
                # Return default empty value if the file does not exist
                return web_list

        return web_list

    @websites.setter
    def websites(self, website_list):
        """
        Saves the website list to a file. If the file doesn't exist, it will create it.
        :param website_list: ['website', 'website']
        :return: Nothing
        """
        file_str = ""
        for line in website_list:
            file_str += line + "\n"

        with self.lock:
            with open(self.WEBSITES_FILE, 'w') as file:
                file.write(file_str)


    @property
    def search_depth(self):
        """ Tries to load from settings.json, returns default value otherwise """
        return self.__load_from_settings("search_depth")

    @search_depth.setter
    def search_depth(self, website_list):
        pass


    @property
    def max_browsers(self):
        return self.__load_from_settings("max_browsers")

    @max_browsers.setter
    def max_browsers(self, website_list):
        pass


    def __save_to_settings(self, key, val):


    def __load_from_settings(self, key):
        """ Tries to load from settings.json, returns default value otherwise """

        with self.lock:
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                return self.DEFAULT_SETTINGS[key]

        return data[key]