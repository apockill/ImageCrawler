import json
from threading import RLock


class Config:
    """
    A threading-proof class for accessing config files and settings
    """

    WEBSITE_FILE = "Websites.txt"

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
                with open(self.WEBSITE_FILE, "r") as file:
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
            with open(self.WEBSITE_FILE, 'w') as file:
                file.write(file_str)


