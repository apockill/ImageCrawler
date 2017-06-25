from threading import RLock
import json



class Config:
    """
    A threading-proof class for accessing config files and settings
    """

    WEBSITES_FILE = "Websites.txt"
    SETTINGS_FILE = "Settings.json"

    DEFAULT_SETTINGS = {"search_depth": 1,
                        "max_browsers": 5,
                        "browser_timeout": 60,
                        "min_match_percent": 30}

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
    def search_depth(self, value):
        self.__save_to_settings("search_depth", value)


    @property
    def max_browsers(self):
        return self.__load_from_settings("max_browsers")

    @max_browsers.setter
    def max_browsers(self, value):
        self.__save_to_settings("max_browsers", value)


    @property
    def browser_timeout(self):
        return self.__load_from_settings("browser_timeout")

    @browser_timeout.setter
    def browser_timeout(self, value):
        self.__save_to_settings("browser_timeout", value)


    @property
    def min_match_percent(self):
        return self.__load_from_settings("min_match_percent")

    @min_match_percent.setter
    def min_match_percent(self, value):
        self.__save_to_settings("min_match_percent", value)


    # Helper Functions
    def __save_to_settings(self, key, val):
        """ Saves a settings to the settings file"""


        with self.lock:
            # Try to pull the current settings from the settings file. If that file doesn't exist, use the default
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                data = self.DEFAULT_SETTINGS

            # Change the setting
            data[key] = val

            # Write the setting to file
            with open(self.SETTINGS_FILE, 'w') as file:
                json.dump(data, file)

    def __load_from_settings(self, key):
        """ Tries to load from settings.json, returns default value otherwise """

        with self.lock:
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                return self.DEFAULT_SETTINGS[key]

        return data[key]