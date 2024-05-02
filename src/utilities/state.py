import datetime
import json

from ..utilities.resource_path import resource_path
from ..utilities.config import config



class StateManager:
    """
    Manages the application state, particularly for tracking daily email send limits and resetting them appropriately.

    This class handles the operations related to loading, updating, and resetting the application state from a JSON file.
    It ensures that daily limits on email sends are enforced and resets these counts when a new day starts.

    Attributes:
        path (str): The relative path to the state JSON file.
        state (dict): A dictionary containing the current state of the application, including today's date and the count of sent emails.
        max_email_count (int): The maximum number of emails that can be sent in a day, loaded from configuration.

    Methods:
        get_state_from_file: Loads the application state from a JSON file.
        update_state_file: Saves the current application state to a JSON file.
        check_and_reset_if_new_day: Checks if the current day has changed and resets the email count if so.
        can_send_email: Determines if an email can be sent under the daily limit.
        increment_sent: Increments the count of sent emails if under the daily limit.
    """
    path = 'settings/state.json'
    def __init__(self) -> None:
        self.state:dict = self.get_state_from_file()
        self.max_email_count = config.get("PREFERENCES", "daily_email_limit")
        
        self.check_and_reset_if_new_day()


    def get_state_from_file(self) -> dict:
        """
        Attempts to load the application state from a JSON file. If the file is missing or corrupted, initializes with default values.

        Returns:
            dict: A dictionary representing the current state, including the date and count of sent emails.
        """
        try:
            with open(resource_path(StateManager.path), "r") as f:
                loaded_state = json.load(f)
                loaded_state["todays_date"] = datetime.datetime.strptime(loaded_state["todays_date"], "%Y-%m-%d %H:%M:%S.%f")
                return loaded_state
        except (FileNotFoundError, KeyError):
            return {"todays_date": datetime.datetime.now(), "sent_today": 0}


    def update_state_file(self) -> None:
        """
        Saves the current state to a JSON file, ensuring the date is properly formatted as a string.
        """
        self.max_email_count = config.get("DEFAULT","daily_email_limit")
        temp_state = self.state.copy()
        temp_state["todays_date"] = temp_state["todays_date"].strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(resource_path(StateManager.path), "w") as f:
            json.dump(temp_state, f, indent=4)


    def check_and_reset_if_new_day(self) -> None:
        """
        Checks if the current date has changed since the last saved state and resets the sent email count if a new day has started.
        """
        if datetime.datetime.now() - self.state["todays_date"] >= datetime.timedelta(days=1):
            self.state["todays_date"] = datetime.datetime.now()
            self.state["sent_today"] = 0
            self.update_state_file()


    def can_send_email(self) -> bool:
        """
        Determines if another email can be sent under the daily limit.

        Returns:
            bool: True if the count of sent emails is below the daily limit, False otherwise.
        """
        return self.state["sent_today"] < int(self.max_email_count)


    def increment_sent(self) -> bool:
        """
        Increments the count of sent emails if it's below the daily limit, updating the state file accordingly.

        Returns:
            bool: True if the increment was successful, False if the daily limit has been reached.
        """
        if self.can_send_email():
            self.state["sent_today"] += 1
            self.update_state_file()
            return True
        return False


state_manager = StateManager()
print("State manager loaded")
print(f"Lockout Date: {state_manager.state['todays_date']}")
print(f"        Sent: {state_manager.state['sent_today']}")
