import configparser

from .resource_path import resource_path



class Config:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(resource_path('settings/config.cfg'))


    def get(self, section, option):
        return self.config.get(section, option)


    def get_bool(self, section, option):
        if self.config.get(section, option) == "True":
            return True
        return False


    def set(self, section, option, value):
        self.config[section][option] = value
        self.save()


    def set_window_size(self, width, height):
        self.config["PREFERENCES"]["window_width"] = str(width)
        self.config["PREFERENCES"]["window_height"] = str(height)
        self.save()
    

    def save(self):
        with open('config.cfg', "w") as config_file:
            self.config.write(config_file)



config = Config()
print("Config loaded")