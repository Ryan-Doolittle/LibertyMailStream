import configparser

from .resource_path import resource_path



class Config:
    """
    Manages configuration settings for the application by reading from and writing to a configuration file.

    This class utilizes Python's configparser to handle application settings such as UI preferences, paths, 
    and other options that need to be persisted across sessions.

    Attributes:
        path (str): The path to the configuration file, derived from a helper function to handle resource paths.
    """
    path = resource_path("settings/config.cfg")
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(self.path)


    def get(self, section, option):
        """
        Retrieves the value of an option from the specified section in the configuration file.

        Args:
            section (str): The section in the configuration file.
            option (str): The option key whose value needs to be fetched.

        Returns:
            str: The value of the specified option within the given section.
        """
        return self.config.get(section, option)


    def get_bool(self, section, option):
        """
        Retrieves a boolean value from the configuration file. The expected values are 'True' or 'False' as strings.

        Args:
            section (str): The section in the configuration file.
            option (str): The option key whose boolean value needs to be fetched.

        Returns:
            bool: The boolean value of the specified option.
        """
        if self.config.get(section, option) == "True":
            return True
        return False


    def set(self, section, option, value):
        """
        Sets the value of an option within a section in the configuration file and saves the updated configuration.

        Args:
            section (str): The section in the configuration file.
            option (str): The option key whose value needs to be set.
            value (str): The value to be set for the option.
        """
        self.config[section][option] = value
        self.save()


    def set_window_size(self, width, height):
        """
        Sets the window dimensions in the configuration file under the 'PREFERENCES' section and saves the update.

        Args:
            width (int): The width of the window to be saved.
            height (int): The height of the window to be saved.
        """
        self.config["PREFERENCES"]["window_width"] = str(width)
        self.config["PREFERENCES"]["window_height"] = str(height)
        self.save()
    

    def save(self):
        """
        Writes the current configuration settings back to the file, persisting any changes made during runtime.
        """
        with open(self.path, "w") as config_file:
            self.config.write(config_file)



config = Config()
print("Config loaded")